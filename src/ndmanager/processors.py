import tempfile
from pathlib import Path

from ndmanager._vendor.omc_data import IncidentNeutron, IncidentPhoton, ThermalScattering
from ndmanager.merge import get_available_temperature, merge_neutron_file
from ndmanager.utils import get_logger


def process_neutron(target: Path, tape: Path, temperatures: set[int]) -> None:
    """Process neutron data file from NJOY tape.

    Args:
        target (Path): Target HDF5 file path
        tape (Path): NJOY tape file path
        temperatures (set[int]): Set of temperatures to process

    Raises:
        ValueError: Raised if no temperatures are specified or if input file does not exist

    """
    if not temperatures:
        msg = "No temperatures specified for processing"
        raise ValueError(msg)
    if not tape.exists():
        msg = f"Input NJOY tape '{tape}' does not exist"
        raise ValueError(msg)

    logpath = target.parent / f"logs/{target.stem}.log"
    logger = get_logger(logpath)
    logger.info("Processing neutron data for %s", target.stem)

    if not target.exists():
        logger.info("Target file does not exist, creating new file at %s", target)
        logger.info("New processing temperatures: %s", " ".join([str(t) for t in temperatures]))
        data = IncidentNeutron.from_njoy(tape, temperatures=temperatures)
        data.export_to_hdf5(target, "w")
    else:
        target_temps = get_available_temperature(target)
        remaining_temps = temperatures - target_temps

        if not remaining_temps:
            logger.info("No new processing is necessary, exiting")
            return target

        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            logger.info("New processing temperatures: %s", " ".join([str(t) for t in remaining_temps]))
            xs = IncidentNeutron.from_njoy(tape, remaining_temps)
            xs.export_to_hdf5(temp_file.name, "w")
            merge_neutron_file(temp_file.name, target)
    return target


def process_photon(target: Path, photo: Path, ard: Path | None = None) -> None:
    """Process photon data file.

    Args:
        target (Path): Target HDF5 file path
        photo (Path): Photon ENDF6 file path
        ard (Path): Atomic relaxation data ENDF6 file path

    Raises:
        ValueError: Raised if input files do not exist

    """
    if not photo.exists():
        msg = f"Photon ENDF6 file '{photo}' does not exist"
        raise ValueError(msg)
    if ard is not None and not ard.exists():
        msg = f"Atomic relaxation data ENDF6 file '{ard}' does not exist"
        raise ValueError(msg)

    logpath = target.parent / f"logs/{target.stem}.log"
    logger = get_logger(logpath)
    logger.info("Processing photon data for %s", target.stem)

    if not target.exists():
        logger.info("Target file does not exist, creating new file at %s", target)
        logger.info("Photon ENDF6 file: %s", photo)
        logger.info("Atomic relaxation data ENDF6 file: %s", ard)
        data = IncidentPhoton.from_endf(photo, ard)
        data.export_to_hdf5(target, "w")
    else:
        logger.info("Target file already exists at %s, no processing necessary", target)
    return target


def process_tsl(target: Path, neutron: Path, tsl: Path) -> None:
    """Process TSL data file.

    Args:
        target (Path): Target HDF5 file path
        neutron (Path): Neutron ENDF6 file path
        tsl (Path): TSL ENDF6 file path

    Raises:
        ValueError: Raised if input files do not exist

    """
    if not neutron.exists():
        msg = f"Neutron ENDF6 file '{neutron}' does not exist"
        raise ValueError(msg)
    if not tsl.exists():
        msg = f"TSL ENDF6 file '{tsl}' does not exist"
        raise ValueError(msg)

    logpath = target.parent / f"logs/{target.stem}.log"
    logger = get_logger(logpath)
    logger.info("Processing TSL data for %s", target.stem)

    if not target.exists():
        logger.info("Target file does not exist, creating new file at %s", target)
        logger.info("Neutron ENDF6 file: %s", neutron)
        logger.info("TSL ENDF6 file: %s", tsl)
        data = ThermalScattering.from_njoy(neutron, tsl)
        data.export_to_hdf5(target, "w")
    else:
        logger.info("Target file already exists at %s, no processing necessary", target)
    return target
