import multiprocessing as mp
import shutil
from pathlib import Path

from rich.progress import Progress

from ndmanager._vendor.omc_data import DataLibrary, Evaluation, get_thermal_name
from ndmanager.input_parser import InputParser
from ndmanager.nuclide import Nuclide
from ndmanager.processors import process_neutron, process_photon, process_tsl


def sorting_key(entry: dict) -> tuple[int, int | str]:
    """Generate a sorting key for library entries.

    Orders entries by type (neutron, photon, then thermal) and then by
    ZAM identifier for neutron/photon or by material name for thermal.

    Args:
        entry (dict): A library entry dictionary with 'type' and 'materials' keys

    Returns:
        tuple[int, int | str]: A tuple where the first element determines the
            primary sort order (0=neutron, 1=photon, 2=thermal) and the second
            element is either the ZAM identifier (int) or material name (str)

    """
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
        """Build photon data library by processing all photon elements.

        Processes photon data files either serially (jobs=1) or in parallel
        (jobs>1) with a progress bar display. Registers each processed file
        to the library.

        Args:
            jobs (int): Number of parallel jobs to use for processing

        Raises:
            ValueError: Raised if jobs is less than 1

        """
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
        """Build neutron data library by processing all nuclides.

        Processes neutron data files from NJOY tapes either serially (jobs=1)
        or in parallel (jobs>1) with a progress bar display. Registers each
        processed file to the library.

        Args:
            jobs (int): Number of parallel jobs to use for processing. Defaults to 1.

        Raises:
            ValueError: Raised if jobs is less than 1

        """
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
        """Build thermal scattering law (TSL) data library.

        Processes TSL data files either serially (jobs=1) or in parallel
        (jobs>1) with a progress bar display. Registers each processed file
        to the library.

        Args:
            jobs (int): Number of parallel jobs to use for processing. Defaults to 1.

        Raises:
            ValueError: Raised if jobs is less than 1

        """
        with Progress() as pbar:
            task = pbar.add_task("Processing TSL", total=len(self.tsl_data))

            if jobs < 1:
                msg = f"Number of jobs must be at least 1, got {jobs}"
                raise ValueError(msg)
            if jobs == 1:
                for neutron, tsl in self.tsl_data.values():
                    name = get_thermal_name(Evaluation(tsl).target["zsymam"].replace(" ", ""))
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

    def export_to_xml(self) -> None:
        """Export the library to an XML cross sections file.

        Writes the library configuration to the cross_sections.xml file
        at the library's root directory path.

        Returns:
            The result of the parent class's export_to_xml method

        """
        return super().export_to_xml(self.path)

    def remove(self) -> None:
        """Remove the library by deleting its root directory.

        Recursively deletes the library's root directory and all its
        contents if it exists. This includes all processed data files,
        logs, and the cross_sections.xml file.

        """
        if self.root.exists():
            shutil.rmtree(self.root)
