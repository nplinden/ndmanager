import time
from contextlib import chdir
from multiprocessing import Pool
from pathlib import Path

import yaml

from ndmanager.API.data import ENDF6_PATH, OPENMC_NUCLEAR_DATA, TSL_NEUTRON
from ndmanager.API.nuclide import Nuclide
from ndmanager.API.utils import clear_line


def process_neutron(directory, path, temperatures):
    import openmc.data

    # print(f"Processing {path}")
    data = openmc.data.IncidentNeutron.from_njoy(path, temperatures=temperatures)
    h5_file = directory / f"{data.name}.h5"

    # print(f"Writing {h5_file} ...")
    data.export_to_hdf5(h5_file, "w")


def process_tsl(directory, neutron, thermal):
    import openmc.data

    data = openmc.data.ThermalScattering.from_njoy(neutron, thermal)
    h5_file = directory / f"{data.name}.h5"
    data.export_to_hdf5(h5_file)


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


def list_tsl(basis, tsl_in):
    ommit = tsl_in.get("ommit", "").split()
    add = tsl_in.get("add", {})
    substitute = tsl_in.get("substitute", {})

    for tsl in ommit:
        if tsl in add:
            raise ValueError("A tsl file can't be both ommited and added.")

    basis_paths = Path(f"{ENDF6_PATH}/{basis}/tsl").glob("*.dat")
    basis_paths = [p for p in basis_paths if p.name not in ommit]
    basis_neutrons = TSL_NEUTRON[basis]
    for k in basis_neutrons:
        if basis_neutrons[k] in substitute:
            basis_neutrons[k] = substitute[basis_neutrons[k]]
    basis_couples = [(basis_neutrons[t.name], t) for t in basis_paths]

    # Add custom evaluations.
    for guestlib, _tsl in add.items():
        guest_paths = Path(f"{ENDF6_PATH}/{guestlib}/tsl").glob("*.dat")
        guest_neutrons = TSL_NEUTRON[guestlib]
        for k in guest_neutrons:
            if guest_neutrons[k] in substitute:
                guest_neutrons[k] = substitute[guest_neutrons[k]]
        basis_couples += [(guest_neutrons(t.name), t) for t in guest_paths]

    return basis_couples


def list_photo(basis, photo_in):
    ommit = photo_in.get("ommit", "").split()
    add = photo_in.get("add", {})

    for nuclide in ommit:
        if nuclide in add:
            raise ValueError("A nuclide can't be both ommited and added.")

    basis_paths = Path(f"{ENDF6_PATH}/{basis}/photo").glob("*.dat")
    basis_dict = {Nuclide.from_file(p).name.rstrip("0"): p for p in basis_paths}

    # Remove unwanted evaluations
    for photo in ommit:
        basis_dict.pop(photo, None)

    # Add custom evaluations.
    # Overwrite if the main library already provides them.
    for guestlib, _photo in add.items():
        photo = _photo.split()
        guest_paths = Path(f"{ENDF6_PATH}/{guestlib}/photo").glob("*.dat")
        guest_endf6 = {
            Nuclide.from_file(n).name.rstrip("0"): n
            for n in guest_paths
            if Nuclide.from_file(n).name in photo
        }
        basis_dict |= guest_endf6

    return basis_dict


def list_ard(basis, ard_in):
    ommit = ard_in.get("ommit", "").split()
    add = ard_in.get("add", {})

    for nuclide in ommit:
        if nuclide in add:
            raise ValueError("A nuclide can't be both ommited and added.")

    basis_paths = Path(f"{ENDF6_PATH}/{basis}/ard").glob("*.dat")
    basis_dict = {Nuclide.from_file(p).name.rstrip("0"): p for p in basis_paths}

    # Remove unwanted evaluations
    for ard in ommit:
        basis_dict.pop(ard, None)

    # Add custom evaluations.
    # Overwrite if the main library already provides them.
    for guestlib, _ard in add.items():
        ard = _ard.split()
        guest_paths = Path(f"{ENDF6_PATH}/{guestlib}/ard").glob("*.dat")
        guest_endf6 = {
            Nuclide.from_file(n).name.rstrip("0"): n
            for n in guest_paths
            if Nuclide.from_file(n).name in ard
        }
        basis_dict |= guest_endf6

    return basis_dict


def generate(ymlpath, dryrun=False):
    import openmc.data

    inputs = yaml.safe_load(open(ymlpath))

    name = OPENMC_NUCLEAR_DATA / inputs["name"]
    name.mkdir(parents=True, exist_ok=True)
    with chdir(name):
        library = openmc.data.DataLibrary()

        # GET TARGET TEMPERATURES
        temperatures = inputs.get("temperatures", 273)
        if isinstance(temperatures, int) or isinstance(temperatures, float):
            temperatures = [int(temperatures)]
        else:
            temperatures = [int(t) for t in temperatures.split()]

        # NEUTRONS
        n_dict = inputs.get("n", {})
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
            with Pool() as p:
                results = [p.apply_async(process_neutron, a) for a in args]
                while 1:
                    time.sleep(0.5)
                    isdone = [r.ready() for r in results]
                    ndone = sum(isdone)
                    t = time.time() - t0
                    clear_line(1)
                    print(
                        f"Processing neutron evaluations: {ndone:4d}/{len(isdone)} t={t:.1f} s."
                    )
                    if ndone == len(isdone):
                        break
                for path in sorted(
                    dest.glob("*.h5"), key=lambda x: Nuclide.from_name(x.stem).zam
                ):
                    library.register_file(path)
        t = time.time() - t0
        print(f"Processing neutron evaluations: {len(isdone)}/{len(isdone)} {t:.1f}")

        # THERMAL SCATTERING LAW
        # print("Processing Thermal Scattering Laws (TSL)")
        # tsl_in = inputs.get("tsl", None)
        # if tsl_in is None:
        #     tsl = None
        # elif isinstance(tsl_in, str):
        #     # In this case this is a ndlib name
        #     tsl = list_tsl(tsl_in, {})
        # else:
        #     tsl = list_tsl(basis, tsl_in)
        # if tsl:
        #     dest = Path("tsl")
        #     dest.mkdir(parents=True, exist_ok=True)
        #     args = [(dest, neutron[t[0]], t[1]) for t in tsl]
        #     if dryrun:
        #         for arg in args:
        #             print(arg[0], str(arg[1]), str(arg[2]))
        #     else:
        #         with Pool() as p:
        #             results = [p.apply_async(process_tsl, a) for a in args]
        #             while 1:
        #                 time.sleep(0.5)
        #                 isdone = [r.ready() for r in results]
        #                 ndone = sum(isdone)
        #                 print(f"Progress: {ndone:4d}/{len(isdone)}")
        #                 clear_line(1)
        #                 if ndone == len(isdone):
        #                     break
        #             # p.starmap(process_tsl, args)
        #         for p in sorted(dest.glob("*.h5")):
        #             library.register_file(p)
        #
        # # PHOTONS
        # photo_in = inputs.get("photo", {})
        # if isinstance(photo_in, str):
        #     # In this case this is a ndlib name
        #     photo = list_photo(photo_in, {})
        # else:
        #     photo = list_photo(basis, photo_in)
        # dest.mkdir(parents=True, exist_ok=True)
        #
        # # ATOMIC RELAXATION
        # ard_in = inputs.get("ard", {})
        # if isinstance(ard_in, str):
        #     # In this case this is a ndlib name
        #     ard = list_ard(ard_in, {})
        # else:
        #     ard = list_ard(basis, ard_in)
        #
        # if photo and ard:
        #     dest = Path("photon")
        #     dest.mkdir(parents=True, exist_ok=True)
        #     if dryrun:
        #         pprint(photo)
        #         pprint(ard)
        #     for atom in photo:
        #         data = openmc.data.IncidentPhoton.from_endf(
        #             str(photo[atom]),
        #             ard.get(atom, None),
        #         )
        #
        #         atomname = atom.rstrip("0")
        #         data.export_to_hdf5(str(dest / f"{atomname}.h5"), "w")
        #
        #     for p in sorted(dest.glob("*.h5")):
        #         library.register_file(p)

        library.export_to_xml("cross_sections.xml")


def chain(ymlpath):
    import openmc.deplete

    inputs = yaml.safe_load(open(ymlpath))

    name = OPENMC_NUCLEAR_DATA / inputs["name"]
    name.mkdir(parents=True, exist_ok=True)
    with chdir(name):
        basis = inputs["basis"]

        neutron = (ENDF6_PATH / basis / "n").glob("*.dat")
        decay = (ENDF6_PATH / basis / "decay").glob("*.dat")
        nfpy = (ENDF6_PATH / basis / "nfpy").glob("dat")

        chainfile = openmc.deplete.Chain.from_endf(
            neutron_files=neutron,
            decay_files=decay,
            fpy_files=nfpy,
            reactions=list(openmc.deplete.chain.REACTIONS.keys()),
            progress=False,
        )

        chainfile.export_to_xml("chain.xml")
