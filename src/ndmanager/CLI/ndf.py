"""Entry point for the ndf command."""

import shutil
from pathlib import Path

import click
import requests
from rich import box
from rich.console import Console
from rich.table import Table

from ndmanager.data import SUBLIBRARIES_SHORTLIST
from ndmanager.endf6 import Endf6
from ndmanager.env import NDMANAGER_ENDF6
from ndmanager.iaea import IAEA


@click.group()
def ndf() -> None:
    """Manage your ENDF6 format nuclear data libraries."""


@ndf.command(name="list")
@click.option("--all", "-a", "_all", is_flag=True, help="Show all libraries.")
def list_command(*, _all: bool) -> None:
    """List available ENDF6 nuclear data libraries."""
    iaea = IAEA()

    names = list(iaea.libraries) if _all else list(iaea.aliases)
    names = [iaea.get_alias(name) for name in names]
    fullnames = [iaea.aliases.get(name, name) for name in names]

    exists = [(NDMANAGER_ENDF6 / name).exists() for name in names]
    checks = ["✅" if ex else "❌" for ex in exists]
    descriptions = [iaea[fullname].library for fullname in fullnames]

    console = Console()
    table = Table(title="Available Libraries (use --all to show all)", box=box.SIMPLE)

    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Available", justify="center")
    table.add_column("Description", style="green")

    rows = zip(names, fullnames, checks, descriptions, strict=True)
    for row in rows:
        table.add_row(*row)

    console.print(table)


@ndf.command(name="remove")
@click.argument("libraries", nargs=-1, required=True)
def remove(libraries: tuple[str, ...]) -> None:
    """Remove one or more installed ENDF6 libraries.

    Args:
        libraries (Tuple[str, ...]): Names of the libraries to remove

    """
    libraries = [NDMANAGER_ENDF6 / lib for lib in libraries]
    for library in libraries:
        if library.exists():
            shutil.rmtree(library)


@ndf.command(name="install")
@click.argument("libraries", nargs=-1, required=True)
@click.option("--sub", "-s", multiple=True, help="Specify sublibraries to install.")
@click.option("--all", "-a", "_all", is_flag=True, help="Install all sublibraries.")
@click.option("--name", "-n", type=str, help="Custom name for local library installation.")
@click.option("--jobs", "-j", type=int, default=1, help="Number of concurrent processes.")
def install(
    libraries: tuple[str, ...],
    *,
    sub: tuple[str, ...],
    _all: bool,
    name: str | None,
    jobs: int,
) -> None:
    """Install ENDF6 nuclear data libraries.

    Args:
        libraries (Tuple[str, ...]): Names of the libraries to install
        sub (Tuple[str, ...]): Names of the sublibraries to install
        all (bool): Whether to install all sublibraries
        name (str | None): Custom name for local library installation
        jobs (int): Number of concurrent processes

    """
    if name is not None and len(libraries) > 1:
        msg = "Custom name can only be used when installing a single library."
        raise ValueError(msg)

    for library in libraries:
        if (p := Path(library)).exists():
            if name is None:
                name = p.name
            _install_local_library(p, name)
            continue

        iaea = IAEA()

        if sub:
            sublibraries = list(sub)
        elif _all:
            sublibraries = list(iaea[library].keys())
        else:
            sublibraries = SUBLIBRARIES_SHORTLIST

        libdata = iaea[library]
        for sublibrary in sublibraries:
            if sublibrary not in libdata.sublibraries:
                continue

            target = NDMANAGER_ENDF6 / library / sublibrary
            sublibdata = libdata[sublibrary]
            sublibdata.download(targetdir=target, processes=jobs)

            # A manual erratum for the neutron xs of B10 in ENDF/B-VIII.0
            if library == "endfb8" and sublibrary == "n":
                url = "https://www.nndc.bnl.gov/endf-b8.0/erratafiles/n-005_B_010.endf"
                tape = requests.get(url, timeout=600).text
                target = NDMANAGER_ENDF6 / "endfb8/n/B10.endf6"
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("w", encoding="utf-8", newline="") as f:
                    f.write(tape)


def _install_local_library(library: Path, name: str) -> None:
    target = NDMANAGER_ENDF6 / name
    if target.exists():
        click.echo(f"[Error] Library {name} already exists", err=True)
        raise SystemExit(1)
    target.mkdir(parents=True)

    candidates = Path(library).rglob("*")
    ntapes = {}
    for candidate in candidates:
        try:
            e = Endf6(candidate)
        except (UnicodeDecodeError, ValueError, IsADirectoryError):
            continue

        if e.sublibrary not in ntapes:
            ntapes[e.sublibrary] = 0
        if not (target / e.sublibrary).exists():
            (target / e.sublibrary).mkdir()
        ntapes[e.sublibrary] += 1

        if e.sublibrary == "tsl":
            tapename = f"{e.sublibrary}/{candidate.stem}.endf6"
        elif e.sublibrary in ["photo", "ard"]:
            tapename = f"{e.sublibrary}/{e.nuclide.element}.endf6"
        else:
            tapename = f"{e.sublibrary}/{e.nuclide.name}.endf6"

        shutil.copy(candidate, target / tapename)

    console = Console()
    table = Table(title=f"{name}", box=box.SIMPLE)

    table.add_column("Sublibrary", style="cyan", no_wrap=True)
    table.add_column("Number of Tapes", style="magenta")

    for sub, n in ntapes.items():
        table.add_row(sub, str(n))
    console.print(table)
