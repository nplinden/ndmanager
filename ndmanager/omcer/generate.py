from multiprocessing import Pool
import time
from pathlib import Path
from ndmanager.data import TSL_NEUTRON, OPENMC_NUCLEAR_DATA, ENDF6_PATH
from ndmanager.nuclide import Nuclide
from ndmanager.utils import clear_line
from pprint import pprint
from contextlib import chdir
import yaml


def process_neutron(directory, path, temperatures):
    import openmc.data

    # print(f"Processing {path}")
    data = openmc.data.IncidentNeutron.from_njoy(
        path, temperatures=temperatures)
    h5_file = directory / f"{data.name}.h5"

    # print(f"Writing {h5_file} ...")
    data.export_to_hdf5(h5_file, "w")


def process_tsl(directory, neutron, thermal):
    import openmc.data

    data = openmc.data.ThermalScattering.from_njoy(neutron, thermal)
    h5_file = directory / f"{data.name}.h5"
    data.export_to_hdf5(h5_file)


def list_neutron(basis, n_in):
    ommit = n_in.get("ommit", "").split()
    add = n_in.get("add", {})

    for nuclide in ommit:
        if nuclide in add:
            raise ValueError("A nuclide can't be both ommited and added.")

    basis_paths = Path(f"{ENDF6_PATH}/{basis}/n").glob("*.dat")
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
    for guestlib, _nuclides in add.items():
        nuclides = _nuclides.split()
        guest_paths = Path(f"{ENDF6_PATH}/{guestlib}/n").glob("*.dat")
        guest_endf6 = {
            Nuclide.from_file(n).name: n
            for n in guest_paths
            if Nuclide.from_file(n).name in nuclides
        }
        basis_dict |= guest_endf6

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

        basis = inputs["basis"]
        temperatures = inputs.get("temperatures", 0)
        if isinstance(temperatures, int) or isinstance(temperatures, float):
            temperatures = [int(temperatures)]
        else:
            temperatures = [int(t) for t in temperatures.split()]
        n_in = inputs.get("n", {})

        # NEUTRONS
        print("Processing neutron evaluations")
        t0 = time.time()
        neutron = list_neutron(basis, n_in)
        dest = Path("neutron")
        dest.mkdir(parents=True, exist_ok=True)
        args = [(dest, neutron[n], temperatures) for n in neutron]
        if dryrun:
            for arg in args:
                print(arg[0], str(arg[1]), str(arg[2]))
        else:
            with Pool() as p:
                results = [p.apply_async(process_neutron, a) for a in args]
                while 1:
                    time.sleep(0.5)
                    isdone = [r.ready() for r in results]
                    ndone = sum(isdone)
                    print(f"Progress: {ndone:4d}/{len(isdone)}")
                    clear_line(1)
                    if ndone == len(isdone):
                        break

                for path in sorted(dest.glob("*.h5")):
                    library.register_file(path)
        print(f"Processing time: {time.time()-t0:.1f}")

        # THERMAL SCATTERING LAW
        print("Processing Thermal Scattering Laws (TSL)")
        tsl_in = inputs.get("tsl", {})
        if isinstance(tsl_in, str):
            # In this case this is a ndlib name
            tsl = list_tsl(tsl_in, {})
        else:
            tsl = list_tsl(basis, tsl_in)
        if tsl:
            dest = Path("tsl")
            dest.mkdir(parents=True, exist_ok=True)
            args = [(dest, neutron[t[0]], t[1]) for t in tsl]
            if dryrun:
                for arg in args:
                    print(arg[0], str(arg[1]), str(arg[2]))
            else:
                with Pool() as p:
                    results = [p.apply_async(process_tsl, a) for a in args]
                    while 1:
                        time.sleep(0.5)
                        isdone = [r.ready() for r in results]
                        ndone = sum(isdone)
                        print(f"Progress: {ndone:4d}/{len(isdone)}")
                        clear_line(1)
                        if ndone == len(isdone):
                            break
                    # p.starmap(process_tsl, args)
                for p in sorted(dest.glob("*.h5")):
                    library.register_file(p)

        # PHOTONS
        photo_in = inputs.get("photo", {})
        if isinstance(photo_in, str):
            # In this case this is a ndlib name
            photo = list_photo(photo_in, {})
        else:
            photo = list_photo(basis, photo_in)
        dest.mkdir(parents=True, exist_ok=True)

        # ATOMIC RELAXATION
        ard_in = inputs.get("ard", {})
        if isinstance(ard_in, str):
            # In this case this is a ndlib name
            ard = list_ard(ard_in, {})
        else:
            ard = list_ard(basis, ard_in)

        if photo and ard:
            dest = Path("photon")
            dest.mkdir(parents=True, exist_ok=True)
            if dryrun:
                pprint(photo)
                pprint(ard)
            for atom in photo:
                data = openmc.data.IncidentPhoton.from_endf(
                    str(photo[atom]),
                    ard.get(atom, None),
                )

                atomname = atom.rstrip("0")
                data.export_to_hdf5(str(dest / f"{atomname}.h5"), "w")

            for p in sorted(dest.glob("*.h5")):
                library.register_file(p)

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
            progress=False
        )

        chainfile.export_to_xml("chain.xml")
