"""Entry point for the ndo command."""

import shutil
import tarfile
import tempfile
from contextlib import chdir
from pathlib import Path

import click
import requests
import yaml
from rich import box
from rich.console import Console
from rich.progress import Progress
from rich.table import Table

from ndmanager.data import OPENMC_LIBS
from ndmanager.env import NDMANAGER_HDF5
from ndmanager.library import Library


@click.group()
def ndo() -> None:
    """Manage your OpenMC HDF5 nuclear data libraries."""


@ndo.command(name="list")
def list_command() -> None:
    """List installable and installed OpenMC nuclear data libraries."""
    xmls = NDMANAGER_HDF5.rglob("*.xml") if NDMANAGER_HDF5.exists() else []
    installed = sorted([str(f.parent.relative_to(NDMANAGER_HDF5)) for f in xmls], key=str.lower)

    console = Console()
    table = Table(title="Installable Libraries", box=box.SIMPLE)

    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Evaluation", style="magenta")
    table.add_column("Installed", justify="center")
    table.add_column("Description", style="green")

    installables = []
    for category, libraries in OPENMC_LIBS.items():
        for library, data in libraries.items():
            name = f"{category}/{library}"
            fancyname = data["fancyname"]
            status = "✅" if (NDMANAGER_HDF5 / name).exists() else "❌"
            installables.append(name)
            table.add_row(name, fancyname, status, data["info"])

    console.print(table)

    table = Table(title="Custom Libraries", box=box.SIMPLE)

    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Description", style="green")

    for name in installed:
        if name in installables:
            continue
        ymlfile = NDMANAGER_HDF5 / name / "input.yml"
        if ymlfile.exists():
            with ymlfile.open(encoding="utf-8") as f:
                desc = yaml.safe_load(f).get("summary", "")
        else:
            desc = "No description available."
        table.add_row(name, desc)

    console.print(table)


@ndo.command(name="install")
@click.argument("libraries", nargs=-1, required=True)
def install_command(libraries: tuple[str, ...]) -> None:
    """Install one or more OpenMC nuclear data libraries.

    Args:
        libraries (tuple[str, ...]): Names of the libraries to install

    """
    for libname in libraries:
        with tempfile.TemporaryDirectory() as tmpdir, chdir(tmpdir):
            category, library = libname.split("/")
            data = OPENMC_LIBS[category][library]

            r = requests.get(data["source"], stream=True, timeout=3600)

            total = int(r.headers.get("content-length", 0))
            with Progress() as pbar:
                task = pbar.add_task(f"Downloading {category}/{library}", total=total)
                with Path(data["tarname"]).open("wb") as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        size = f.write(chunk)
                        pbar.update(task, advance=size)

            with tarfile.open(data["tarname"]) as tar, Progress() as pbar:
                task = pbar.add_task(f"Extracting  {category}/{library}", total=total)
                for item in tar:
                    tar.extract(item, ".", filter="tar")
                    pbar.update(task, advance=item.size)

            source = Path(data["extractedname"])
            target = NDMANAGER_HDF5 / category / library
            target.parent.mkdir(exist_ok=True, parents=True)
            shutil.rmtree(target, ignore_errors=True)
            shutil.move(source, target)


@ndo.command(name="remove")
@click.argument("libraries", nargs=-1, required=True)
def remove_command(libraries: tuple[str, ...]) -> None:
    """Remove one or more installed OpenMC libraries.

    Args:
        libraries (Tuple[str, ...]): Names of the libraries to remove

    """
    libraries = [NDMANAGER_HDF5 / lib for lib in libraries]
    for library in libraries:
        if library.exists():
            shutil.rmtree(library)


@ndo.command(name="copy")
@click.argument("source", type=str, required=True)
@click.argument("target", type=str, required=True)
def copy_command(source: str, target: str) -> None:
    """Copy an installed OpenMC library.

    Args:
        source (str): Name for the original library
        target (str): Name for the new cloned library

    Raises:
        ValueError: The source library does not exist
        ValueError: The target library already exists

    """
    source_path = NDMANAGER_HDF5 / source
    target_path = NDMANAGER_HDF5 / target
    if not source_path.exists():
        msg = f"{source} is not in the library list."
        raise ValueError(msg)
    if target_path.exists():
        msg = f"{target} is already in the library list."
        raise ValueError(msg)
    shutil.copytree(source_path, target_path)


@ndo.command(name="build")
@click.argument("filename", type=str, required=True)
@click.option("--clean", is_flag=True, help="Remove the library before building")
@click.option("--temperatures", "-T", multiple=True, type=int, help="Override the temperature values in the input file")
@click.option("--jobs", "-j", type=int, default=1, help="Number of concurrent processes")
def build_command(
    filename: str,
    *,
    clean: bool,
    temperatures: tuple[int, ...] | None,
    jobs: int,
) -> None:
    """Build an OpenMC HDF5 nuclear data library from a YAML descriptive file.

    Args:
        filename (str): The name of the YAML file describing the target library
        clean (bool): Remove the library before building
        temperatures (Tuple[int, ...] | None): Override the temperature values in the input file.
        jobs (int): Number of concurrent processes.

    """
    lib = Library(filename)
    if clean:
        lib.remove()
    lib.build(jobs=jobs)
    lib.export_to_xml()
