import time
from multiprocessing import Pool
from pathlib import Path


from ndmanager.API.data import ENDF6_PATH
from ndmanager.API.nuclide import Nuclide
from ndmanager.API.utils import clear_line


def process_neutron(directory, path, temperatures):
    import openmc.data

    # print(f"Processing {path}")
    data = openmc.data.IncidentNeutron.from_njoy(path, temperatures=temperatures)
    h5_file = directory / f"{data.name}.h5"

    # print(f"Writing {h5_file} ...")
    data.export_to_hdf5(h5_file, "w")


def list_neutron(neutron_params):
    """List the paths to neutron ENDF6 evaluations necessary to build the
    neutron HDF5 libraries.

    Args:
        neutron_params (Dict[str, str]): The neutron parameters in the form of a dictionnary.

    Returns:
        Dict[str, Path]: A dictionnary that associates nuclide names to ENDF6 paths.
    """
    basis = neutron_params["basis"]
    ommit = neutron_params.get("ommit", "").split()
    add = neutron_params.get("add", {})

    for nuclide in ommit:
        if nuclide in add:
            raise ValueError("A nuclide can't be both ommited and added.")

    basis_paths = (ENDF6_PATH / basis / "n").glob("*.endf6")
    basis_dict = {Nuclide.from_file(p).name: p for p in basis_paths}

    # Remove unwanted evaluations
    for nuclide in ommit:
        basis_dict.pop(nuclide, None)

    # Remove neutron evaluations if they are present.
    basis_dict.pop("n1", None)
    basis_dict.pop("nn1", None)
    basis_dict.pop("N1", None)

    # Add custom evaluations.
    # Overwrite if the main library already provides them.
    guest_dict = {}
    for guestlib, _nuclides in add.items():
        nuclides = _nuclides.split()
        for nuclide in nuclides:
            p = ENDF6_PATH / guestlib / "n" / f"{nuclide}.endf6"
            if not p.exists():
                raise ValueError(
                    f"Nuclide {nuclide} is not available in the {guestlib} library."
                )
            guest_dict[nuclide] = p
        basis_dict |= guest_dict

    return basis_dict


def generate_neutron(n_dict, temperatures, dryrun, library):
    # NEUTRONS
    t0 = time.time()
    neutron = list_neutron(n_dict)
    dest = Path("neutron")
    dest.mkdir(parents=True, exist_ok=True)
    args = [(dest, neutron[n], temperatures) for n in neutron]
    if dryrun:
        for arg in args:
            print(arg[0], str(arg[1]), str(arg[2]))
    else:
        print(f"Processing neutron evaluations: 0/{len(args)}")
        print(f"Time elapsed: 0 s.")
        with Pool() as p:
            results = [p.apply_async(process_neutron, a) for a in args]
            while 1:
                time.sleep(0.5)
                isdone = [r.ready() for r in results]
                ndone = sum(isdone)
                clear_line(2)
                print(f"Processing neutron evaluations: {ndone:4d}/{len(isdone)}")
                print(f"Time elapsed: {time.time() - t0:.1f} s.")
                if ndone == len(isdone):
                    break
            for path in sorted(
                dest.glob("*.h5"), key=lambda x: Nuclide.from_name(x.stem).zam
            ):
                library.register_file(path)
        clear_line(2)
        print(f"Processing neutron evaluations: {ndone:4d}/{len(isdone)}")
        print(f"Time elapsed: {time.time() - t0:.1f} s.")
