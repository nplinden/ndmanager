from ndmanager.API.sampling.sampling import Sampling, SampleTapes
from ndmanager.API.utils import get_hdf5
from ndmanager.env import NDMANAGER_COV
from ndmanager.API.sampling.covmatrix import CovMatrix
import h5py
import numpy as np
import shutil

SUM_RULES = {1: [2, 3],
             3: [4, 5, 11, 16, 17, 22, 23, 24, 25, 27, 28, 29, 30, 32, 33, 34, 35,
                 36, 37, 41, 42, 44, 45, 152, 153, 154, 156, 157, 158, 159, 160,
                 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172,
                 173, 174, 175, 176, 177, 178, 179, 180, 181, 183, 184, 185,
                 186, 187, 188, 189, 190, 194, 195, 196, 198, 199, 200],
             4: list(range(50, 92)),
             16: list(range(875, 892)),
             18: [19, 20, 21, 38],
             27: [18, 101],
             101: [102, 103, 104, 105, 106, 107, 108, 109, 111, 112, 113, 114,
                   115, 116, 117, 155, 182, 191, 192, 193, 197],
             103: list(range(600, 650)),
             104: list(range(650, 700)),
             105: list(range(700, 750)),
             106: list(range(750, 800)),
             107: list(range(800, 850))}

class HDF5Sampling(Sampling):
    def __init__(self, yaml_path: str):
        """Instantiate a Sampling object given a path to a yaml input file

        Args:
            yaml_path (str): The path to the input file
        """
        super().__init__(yaml_path)

    def sample_one_nuclide(self, tape: SampleTapes, processes):
        nuclide = tape.nuclide
        matrix_lib, matrix_groups = tape.matrix_lib.split("@")
        covmatrix = CovMatrix.from_hdf5(NDMANAGER_COV / matrix_lib / matrix_groups / f"{nuclide}.h5")
        _, mts, _ = covmatrix.data.index.levels
        self.covmts = mts.to_numpy()
        self.nominal_path = get_hdf5(tape.xs_lib, "neutron", nuclide)
        self.groups = covmatrix.data.index.levels[2]
        with h5py.File(self.nominal_path, "r") as f:
            reactions = f[f"{nuclide}/reactions"]
            self.hdf5_mts = [int(k.split("_")[-1]) for k in reactions.keys()]

            self.energies = {}
            for temperature in f[f"{nuclide}/energy"]:
                self.energies[temperature] = f[f"{nuclide}/energy/{temperature}"][...]
        samples = covmatrix.sampling(self.nsmp, seed=1605844414)

        for n, s in samples.iterate_xs_samples():
            perturbed_path = self.rootpath / f"{nuclide}" / f"{n}.h5"
            perturbed_path.parent.mkdir(exist_ok=True, parents=True)
            shutil.copy(self.nominal_path, perturbed_path)
            with h5py.File(perturbed_path, "a") as f:
                df = s[nuclide]
                for T, E in self.energies.items():
                    masks = []
                    for intrvl in df.index:
                        # masks.append(np.ma.masked_inside(E, intrvl.left, intrvl.right).mask)
                        masks.append(np.ma.masked_where( (E > intrvl.left) & (E <= intrvl.right), E).mask)
                    for mt in self.covmts:
                        if mt in self.hdf5_mts:
                            perturbation = np.ones_like(E)
                            values = df[mt]
                            for value, mask in zip(values, masks):
                                perturbation[mask] *= value
                            dset_path = f"{nuclide}/reactions/reaction_{mt:03}/{T}/xs"
                            if dset_path in f:
                                dset = f[f"{nuclide}/reactions/reaction_{mt:03}/{T}/xs"]
                                threshold = dset.attrs["threshold_idx"]
                                dset[...] *= perturbation[threshold:]
                        if mt in SUM_RULES:
                            for sum_mt in SUM_RULES[mt]:
                                if sum_mt in self.hdf5_mts:
                                    perturbation = np.ones_like(E)
                                    values = df[mt]
                                    for value, mask in zip(values, masks):
                                        perturbation[mask] *= value
                                    dset_path = f"{nuclide}/reactions/reaction_{sum_mt:03}/{T}/xs"
                                    if dset_path in f:
                                        dset = f[f"{nuclide}/reactions/reaction_{sum_mt:03}/{T}/xs"]
                                        threshold = dset.attrs["threshold_idx"]
                                        dset[...] *= perturbation[threshold:]
