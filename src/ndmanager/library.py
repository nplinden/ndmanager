from ndmanager._vendor.omc_data import DataLibrary
from pathlib import Path
import shutil
import yaml
from ndmanager.env import NDMANAGER_HDF5
from ndmanager.nuclide import Nuclide
from ndmanager.input_parser import InputParser
from ndmanager.processors import process_photon, process_neutron, process_tsl
from rich.progress import Progress
import multiprocessing as mp
from ndmanager._vendor.omc_data import get_thermal_name, Evaluation


def sorting_key(entry: dict) -> tuple[int, int | str]:
    if entry["type"] == "neutron":
        return (0, Nuclide.from_name(entry["materials"][0]).zam)
    if entry["type"] == "photon":
        return (1, Nuclide.from_name(entry["materials"][0]).zam)
    return (2, entry["materials"][0])


class Library(DataLibrary, InputParser):
    """Subclassing OpenMC's DataLibrary object for processing."""

    def __init__(self, filepath: str | Path) -> None:
        """Create an NDMLibrary given a yaml input file.

        Args:
            filepath (str | Path): Path to a yaml input file

        """
        DataLibrary.__init__(self)
        InputParser.__init__(self, filepath=filepath)

        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "cross_sections.xml"

    def build(self, jobs: int = 1) -> None:
        """Build the library by processing all data.

        Args:
            jobs (int): Number of parallel jobs to use for processing

        """
        if self.neutron_data is not None:
            self.build_neutron(jobs)

        if self.photon_data is not None:
            self.build_photon(jobs)

        if self.tsl_data is not None:
            self.build_tsl(jobs)

        self.sort(key=sorting_key)

    def build_photon(self, jobs: int) -> None:
        with Progress() as pbar:
            task = pbar.add_task("Processing photons", total=len(self.photon_data))

            if jobs < 1:
                msg = f"Number of jobs must be at least 1, got {jobs}"
                raise ValueError(msg)
            if jobs == 1:
                for element, args in self.photon_data.items():
                    target = self.root / "photon" / f"{element}.h5"
                    process_photon(target, *args)
                    self.register_file(target)
                    pbar.update(task, description=f"Processed {element}", advance=1)
            else:

                def error_callback(e: Exception) -> None:
                    raise e

                def update_pbar(*args) -> None:
                    self.register_file(args[0])
                    pbar.update(task, advance=1)

                with mp.get_context("spawn").Pool(jobs) as p:
                    for element, args in self.photon_data.items():
                        target = self.root / "photon" / f"{element}.h5"
                        p.apply_async(
                            process_photon,
                            args=(target, *args),
                            callback=update_pbar,
                            error_callback=error_callback,
                        )
                    p.close()
                    p.join()

    def build_neutron(self, jobs: int = 1) -> None:
        with Progress() as pbar:
            task = pbar.add_task("Processing neutron", total=len(self.neutron_data))

            if jobs < 1:
                msg = f"Number of jobs must be at least 1, got {jobs}"
                raise ValueError(msg)
            if jobs == 1:
                for nuclide, tape in self.neutron_data.items():
                    target = self.root / "neutron" / f"{nuclide}.h5"
                    process_neutron(target, tape, self.neutron_temps)
                    self.register_file(target)
                    pbar.update(task, description=f"Processed {nuclide}", advance=1)
            else:

                def error_callback(e: Exception) -> None:
                    raise e

                def update_pbar(*args) -> None:
                    self.register_file(args[0])
                    pbar.update(task, advance=1)

                with mp.get_context("spawn").Pool(jobs) as p:
                    for nuclide, tape in self.neutron_data.items():
                        target = self.root / "neutron" / f"{nuclide}.h5"
                        p.apply_async(
                            process_neutron,
                            args=(target, tape, self.neutron_temps),
                            callback=update_pbar,
                            error_callback=error_callback,
                        )
                    p.close()
                    p.join()

    def build_tsl(self, jobs: int = 1) -> None:
        with Progress() as pbar:
            task = pbar.add_task("Processing TSL", total=len(self.tsl_data))

            if jobs < 1:
                msg = f"Number of jobs must be at least 1, got {jobs}"
                raise ValueError(msg)
            if jobs == 1:
                for neutron, tsl in self.tsl_data.values():
                    name = get_thermal_name(Evaluation(tsl).target["zsymam"])
                    target = self.root / "tsl" / f"{name}.h5"
                    process_tsl(target, neutron, tsl)
                    self.register_file(target)
                    pbar.update(task, description=f"Processed {name}", advance=1)
            else:

                def error_callback(e: Exception) -> None:
                    raise e

                def update_pbar(*args) -> None:
                    self.register_file(args[0])
                    pbar.update(task, advance=1)

                with mp.get_context("spawn").Pool(jobs) as p:
                    for neutron, tsl in self.tsl_data.values():
                        name = get_thermal_name(Evaluation(tsl).target["zsymam"].replace(" ", ""))
                        target = self.root / "tsl" / f"{name}.h5"
                        p.apply_async(
                            process_tsl,
                            args=(target, neutron, tsl),
                            callback=update_pbar,
                            error_callback=error_callback,
                        )
                    p.close()
                    p.join()

    def export_to_xml(self):
        return super().export_to_xml(self.path)

    def remove(self):
        if self.root.exists():
            shutil.rmtree(self.root)
