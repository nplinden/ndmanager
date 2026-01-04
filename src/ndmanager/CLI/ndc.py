"""Entry point for the ndc command."""

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

from ndmanager._vendor.omc_data import Chain
from ndmanager.data import BRANCHING_RATIOS, OPENMC_CHAINS, REACTIONS
from ndmanager.endf6 import list_endf6
from ndmanager.env import NDMANAGER_CHAINS


@click.group()
def ndc() -> None:
    """Manage your OpenMC XML chain files."""


@ndc.command(name="list")
def list_command() -> None:
    """List installable and installed OpenMC nuclear data chains."""
    xmls = NDMANAGER_CHAINS.glob("*.xml")
    installed = sorted([f.stem for f in xmls], key=str.lower)

    console = Console()
    table = Table(title="Installable Chains", box=box.SIMPLE)

    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Installed", justify="center")
    table.add_column("Description", style="green")

    for chain, data in OPENMC_CHAINS.items():
        status = "✅" if (NDMANAGER_CHAINS / f"official/{chain}.xml").exists() else "❌"
        table.add_row(f"official/{chain}", status, data["info"])

    console.print(table)

    table = Table(title="Custom Chains", box=box.SIMPLE)

    table.add_column("ID", style="cyan", no_wrap=True)

    for name in installed:
        if name in OPENMC_CHAINS:
            continue
        table.add_row(name)
    if table.row_count:
        console.print(table)


@ndc.command(name="install")
@click.argument("chains", nargs=-1, type=str)
def install_command(chains: tuple[str, ...]) -> None:
    """Download and install one or more OpenMC chain files from the official website.

    Args:
        chains (Tuple[str, ...]): Names of the chains to install.

    """
    chains = [chain.removeprefix("official/") for chain in chains]
    for chain in chains:
        if chain not in OPENMC_CHAINS:
            msg = f"{chain} chain is not available for installation"
            raise KeyError(msg)
    for chain in chains:
        with tempfile.TemporaryDirectory() as tmpdir, chdir(tmpdir):
            url = OPENMC_CHAINS[chain]["url"]
            total = int(OPENMC_CHAINS[chain]["size"])
            r = requests.get(url, timeout=3600, stream=True)

            with Progress() as pbar:
                task = pbar.add_task(f"Downloading {chain}", total=total)
                p = NDMANAGER_CHAINS / "official" / f"{chain}.xml"
                p.parent.mkdir(exist_ok=True, parents=True)
                with p.open("wb") as f:
                    for data in r.iter_content(chunk_size=1024):
                        size = f.write(data)
                        pbar.update(task, advance=size)


@ndc.command(name="remove")
@click.argument("chains", nargs=-1, type=str)
def remove_command(chains: tuple[str, ...]) -> None:
    """Remove one or more installed OpenMC chain files.

    Args:
        chains (Tuple[str, ...]): Names of the chains to remove.

    """
    for chain in chains:
        p = NDMANAGER_CHAINS / "official" / f"{chain}.xml"
        if p.exists():
            p.unlink()


@ndc.command(name="copy")
@click.argument("source", type=str)
@click.argument("target", type=str)
def copy_command(source: str, target: str) -> None:
    """Copy a custom OpenMC chain file to a new location.

    Args:
        source (str): Name of the source chain file
        target (str): Name of the target chain file

    """
    src = NDMANAGER_CHAINS / f"{source}.xml"
    tgt = NDMANAGER_CHAINS / f"{target}.xml"
    if not src.exists():
        msg = f"Source chain file {src} does not exist."
        raise FileNotFoundError(msg)
    if tgt.exists():
        msg = f"Target chain file {tgt} already exists."
        raise FileExistsError(msg)
    tgt.parent.mkdir(exist_ok=True, parents=True)
    with src.open("rb") as fsrc, tgt.open("wb") as ftgt:
        ftgt.write(fsrc.read())


@ndc.command(name="build")
@click.argument("filename", type=str)
def build_command(filename: str) -> None:
    """Build an OpenMC depletion chain from a YAML descriptive file.

    Args:
        filename (str): The name of the YAML file describing the target depletion chain

    """
    with Path(filename).open(encoding="utf-8") as f:
        inputs = yaml.safe_load(f)
    name = inputs["name"]

    target = NDMANAGER_CHAINS / f"{name}.xml"
    if target.exists():
        msg = "A chain with that name already exists"
        raise FileExistsError(msg)

    decay = list(list_endf6("decay", inputs["decay"]).values())
    n = list(list_endf6("n", inputs["n"]).values())
    nfpy = list(list_endf6("nfpy", inputs["nfpy"]).values())
    reactions = inputs.get("reactions")

    if reactions is None:
        chain = Chain.from_endf(decay, nfpy, n)
    elif reactions == "ALL":
        chain = Chain.from_endf(decay, nfpy, n, REACTIONS)
    else:
        chain = Chain.from_endf(decay, nfpy, n, reactions)

    if "branching_ratios" in inputs:
        ratios = BRANCHING_RATIOS[inputs["branching_ratios"]]
        for reaction, br in ratios.items():
            chain.set_branch_ratios(
                branch_ratios=br,
                reaction=reaction,
                strict=False,
            )

    chain.export_to_xml(target)
