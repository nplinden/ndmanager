from pathlib import Path

import yaml

from ndmanager.data import TSL_NEUTRON
from ndmanager.endf6 import get_endf6
from ndmanager.env import NDMANAGER_ENDF6, NDMANAGER_HDF5


class InputParser:
    """Parse an input yml file into a dictionary."""

    def __init__(self, filepath: Path | str) -> None:
        """Initialize the InputParser.

        Args:
            filepath (Path): The path to the input yml file

        """
        self.filepath = Path(filepath)
        with self.filepath.open() as f:
            self.input_dict = yaml.safe_load(f)

        self.name = self.input_dict.get("name", "")
        self.summary = self.input_dict.get("summary", "")
        self.description = self.input_dict.get("description", "")

        self.root = NDMANAGER_HDF5 / self.name

        if "neutron" in self.input_dict:
            self.neutron_data, self.neutron_temps = self.list_neutrons()
        else:
            self.neutron_data, self.neutron_temps = None, None

        if "photon" in self.input_dict:
            self.photon_data = self.list_photons()
        else:
            self.photon_data = None

        if "tsl" in self.input_dict:
            if self.neutron_data is None:
                msg = "TSL section found without neutron section"
                raise ValueError(msg)
            self.tsl_data = self.list_tsl()
        else:
            self.tsl_data = None

    def list_neutrons(self) -> tuple[dict[str, Path], set[int]]:
        """List the neutron ENDF6 tapes and temperatures from a library yml file.

        Args:
            filepath (Path): The path to the library yml file

        """
        if "neutron" not in self.input_dict:
            msg = f"No neutron section found in {self.filepath}"
            raise ValueError(msg)

        data = self.input_dict["neutron"]

        if "temperatures" not in data:
            msg = f"No temperatures found in neutron section of {self.filepath}"
            raise ValueError(msg)

        tmp = data.get("temperatures", "")
        temperatures = [tmp] if isinstance(tmp, int) else [int(t) for t in data.get("temperatures", "").split()]
        base = data.get("base")
        add = data.get("add", {})
        omit = set(data.get("omit", "").split())
        reuse = data.get("reuse", {})

        tapes = {}
        if base is not None:
            base_path = NDMANAGER_ENDF6 / base / "n"
            if not base_path.exists():
                msg = f"Neutron base path '{base_path}' does not exist"
                raise ValueError(msg)

            tapes = {p.stem: p for p in base_path.glob("*.endf6") if p.name not in omit | set(reuse)}

        # Remove neutron evaluations if they are present.
        tapes.pop("n1", None)
        tapes.pop("nn1", None)
        tapes.pop("N1", None)

        for guestlib, nuclides in add.items():
            for nuclide in nuclides.split():
                tapes[nuclide] = get_endf6(guestlib, "n", nuclide)

        return tapes, set(temperatures)

    def list_photons(self) -> dict[str, tuple[Path, Path]]:
        """List the photon ENDF6 tapes from a library yml file.

        Args:
            filepath (Path): The path to the library yml file

        """
        if "photon" not in self.input_dict:
            msg = f"No photon section found in {self.filepath}"
            raise ValueError(msg)

        data = self.input_dict["photon"]
        base = data.get("base")
        add = data.get("add", {})
        omit = set(data.get("omit", "").split())
        reuse = data.get("reuse", {})

        photon = {}
        if base is not None:
            photo_base = NDMANAGER_ENDF6 / base / "photo"
            if not photo_base.exists():
                msg = f"Photon base path '{photo_base}' does not exist"
                raise ValueError(msg)

            ard_base = NDMANAGER_ENDF6 / base / "ard"
            if not ard_base.exists():
                msg = f"ARD base path '{ard_base}' does not exist"
                raise ValueError(msg)

            photo = {p.stem: p for p in photo_base.glob("*.endf6") if p.name not in omit | set(reuse)}
            ard = {p.stem: p for p in ard_base.glob("*.endf6") if p.name not in omit | set(reuse)}
            photon |= {nuc: (photo[nuc], ard.get(nuc)) for nuc in photo}

        for guestlib, nuclides in add.items():
            for nuclide in nuclides.split():
                photo = get_endf6(guestlib, "photo", nuclide)
                ard = get_endf6(guestlib, "ard", nuclide)
                photon[nuclide] = (photo, ard)

        return photon

    def list_tsl(self) -> dict[str, Path]:
        """List the TSL ENDF6 tapes from a library yml file.

        Args:
            filepath (Path): The path to the library yml file

        """
        if "tsl" not in self.input_dict:
            msg = f"No tsl section found in {self.filepath}"
            raise ValueError(msg)

        data = self.input_dict["tsl"]
        base = data.get("base")
        add = data.get("add", {})
        omit = set(data.get("omit", "").split())
        reuse = data.get("reuse", {})

        tsl = {}
        if base is not None:
            base_path = NDMANAGER_ENDF6 / base / "tsl"
            if not base_path.exists():
                msg = f"No tsl tapes for base library '{base}'"
                raise ValueError(msg)

            for tsl_tape in base_path.glob("*.endf6"):
                if tsl_tape.stem in omit or tsl_tape.stem in reuse:
                    continue

                if tsl_tape.name not in TSL_NEUTRON[base]:
                    msg = f"No nuclide mapping found for TSL tape '{tsl_tape.stem}' in library '{base}'"
                    raise ValueError(msg)

                nuclide_tape = self.neutron_data[TSL_NEUTRON[base][tsl_tape.name]]
                tsl[tsl_tape.stem] = (tsl_tape, nuclide_tape)

        for guestlib, pair in add.items():
            for tsl_name, nuclide in pair.items():
                nuclide_tape = self.neutron_data[nuclide]
                tsl_tape = get_endf6(guestlib, "tsl", tsl_name)
                tsl[tsl_name] = (nuclide_tape, tsl_tape)

        return tsl
