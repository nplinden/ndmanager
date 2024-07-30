import os
import openmc
from multiprocessing import Pool
from pathlib import Path
from ndfetcher.data import TSL_NEUTRON, nuclide_from_file, ND_PATH, ENDF6_PATH
from pprint import pprint
import argparse as ap
from contextlib import chdir
import yaml

def process_neutron(directory, path, temperatures):
    print(f"Processing {path}")
    data = openmc.data.IncidentNeutron.from_njoy(
        path, temperatures=temperatures)
    h5_file = directory / f"{data.name}.h5"

    print(f"Writing {h5_file} ...")
    data.export_to_hdf5(h5_file, "w")


def process_tsl(directory, neutron, thermal):
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
    basis_dict = {nuclide_from_file(p): p for p in basis_paths}

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
            nuclide_from_file(n): n
            for n in guest_paths
            if nuclide_from_file(n) in nuclides
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
        tsl = _tsl.split()
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
    basis_dict = {nuclide_from_file(p).rstrip("0"): p for p in basis_paths}

    # Remove unwanted evaluations
    for photo in ommit:
        basis_dict.pop(photo, None)

    # Add custom evaluations.
    # Overwrite if the main library already provides them.
    for guestlib, _photo in add.items():
        photo = _photo.split()
        guest_paths = Path(f"{ENDF6_PATH}/{guestlib}/photo").glob("*.dat")
        guest_endf6 = {
            nuclide_from_file(n).rstrip("0"): n
            for n in guest_paths
            if nuclide_from_file(n) in photo
        }
        basis_dict |= guest_endf6

    return basis_dict


def list_ard(basis, photo_in):
    ommit = photo_in.get("ommit", "").split()
    add = photo_in.get("add", {})

    for nuclide in ommit:
        if nuclide in add:
            raise ValueError("A nuclide can't be both ommited and added.")

    basis_paths = Path(f"{ENDF6_PATH}/{basis}/ard").glob("*.dat")
    basis_dict = {nuclide_from_file(p).rstrip("0"): p for p in basis_paths}

    # Remove unwanted evaluations
    for photo in ommit:
        basis_dict.pop(photo, None)

    # Add custom evaluations.
    # Overwrite if the main library already provides them.
    for guestlib, _photo in add.items():
        photo = _photo.split()
        guest_paths = Path(f"{ENDF6_PATH}/{guestlib}/ard").glob("*.dat")
        guest_endf6 = {
            nuclide_from_file(n).rstrip("0"): n
            for n in guest_paths
            if nuclide_from_file(n) in photo
        }
        basis_dict |= guest_endf6

    return basis_dict


def generate(ymlpath, dryrun=False):
    inputs = yaml.safe_load(open(ymlpath))

    name = ND_PATH / inputs["name"]
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
        neutron = list_neutron(basis, n_in)
        dest = Path("neutron")
        dest.mkdir(parents=True, exist_ok=True)
        args = [(dest, neutron[n], temperatures) for n in neutron]
        if dryrun:
            for arg in args:
                print(arg[0], str(arg[1]), str(arg[2]))
        else:
            with Pool() as p:
                for a in args:
                    print(a)
                p.starmap(process_neutron, args)

                for p in sorted(dest.glob("*.h5")):
                    library.register_file(p)

        # THERMAL SCATTERING LAW
        tsl_in = inputs.get("tsl", {})
        if isinstance(tsl_in, str):
            # In this case this is a ndlib name
            tsl = list_tsl(tsl_in, {})
        else:
            tsl = list_tsl(basis, tsl_in)
        dest = Path("tsl")
        dest.mkdir(parents=True, exist_ok=True)
        args = [(dest, neutron[t[0]], t[1]) for t in tsl]
        if dryrun:
            for arg in args:
                print(arg[0], str(arg[1]), str(arg[2]))
        else:
            with Pool() as p:
                p.starmap(process_tsl, args)
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

        dest = Path("photon")
        dest.mkdir(parents=True, exist_ok=True)
        if dryrun:
            pprint(photo)
            pprint(ard)
        for atom in photo:
            data = openmc.data.IncidentPhoton.from_endf(
                photo[atom],
                ard.get(atom, None),
            )

            atomname = atom.rstrip("0")
            data.export_to_hdf5(dest / f"{atomname}.h5", "w")

        for p in sorted(dest.glob("*.h5")):
            library.register_file(p)

        library.export_to_xml("cross_sections.xml")

def chain(ymlpath):
    if ENDF6_PATH is None:
        raise EnvironmentError("The $ENDF6_PATH must be set.")

    inputs = yaml.safe_load(open(ymlpath))

    name = ND_PATH / inputs["name"]
    name.mkdir(parents=True, exist_ok=True)
    with chdir(name):
        basis = inputs["basis"]

        neutron = (ENDF6_PATH / basis / "n").glob("*.dat")
        decay = (ENDF6_PATH / basis / "decay").glob("*.dat")
        nfpy = (ENDF6_PATH / basis / "nfpy").glob("dat")

        chain = openmc.deplete.Chain.from_endf(
            neutron_files=neutron,
            decay_files=decay,
            fpy_files=nfpy,
            reactions=list(openmc.deplete.chain.REACTIONS.keys())
        )

        chain.export_to_xml("chain.xml")

def generate_cmd(args: ap.Namespace):
    chain(args.filename)
    generate(args.filename, args.dryrun)