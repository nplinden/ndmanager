import logging
from itertools import product
import matplotlib.pyplot as plt

import h5py
import numpy as np
import pandas as pd
import sandy
import scipy.sparse

import ndmanager


class CovMatrix(sandy.CategoryCov):
    def __init__(self, nuclide, data):
        self.nuclide = nuclide
        super().__init__(data)

    @classmethod
    def from_tape(cls, path, ign=3, kind=33, **kwargs):
        nuclide = ndmanager.Endf6(path).nuclide.name
        tape = sandy.endf6.Endf6.from_file(path)
        errorr = tape.get_errorr(errorr33_kws={"ign": ign}, **kwargs)
        if "errorr33" not in errorr:
            raise ValueError("No suitable MF33 found.")
        data = errorr["errorr33"].get_cov().data
        data.columns = data.columns.set_levels([nuclide], level=0)
        data.index = data.index.set_levels([nuclide], level=0)
        return cls(nuclide, data)

    def export_to_hdf5(self, path):
        if path is None:
            path = f"{self.nuclide}.h5"
        corr = self.get_corr()
        _, mts, energies = corr.data.index.levels
        with h5py.File(path, "w") as f:
            e = np.concatenate(
                [energies.left.to_numpy()[None, :], energies.right.to_numpy()[None, :]]
            )
            f[f"{self.nuclide}/ENERGIES"] = e
            matcov = corr.data[self.nuclide].loc[self.nuclide]
            for colmt in mts:
                std = self.get_std()[self.nuclide, colmt].to_numpy()
                f[f"{self.nuclide}/reactions/{colmt}/STD"] = std
                for rowmt in mts:
                    matrix = matcov[colmt].loc[rowmt]
                    # print(f"BLOCK: {colmt} <-> {rowmt}")
                    csr = scipy.sparse.csr_array(matrix)
                    f[f"{self.nuclide}/reactions/{colmt}/{rowmt}/DATA"] = csr.data
                    f[f"{self.nuclide}/reactions/{colmt}/{rowmt}/INDICES"] = csr.indices
                    f[f"{self.nuclide}/reactions/{colmt}/{rowmt}/INDPTR"] = csr.indptr
                    f[f"{self.nuclide}/reactions/{colmt}/{rowmt}/SHAPE"] = csr.shape

    def get_corr(self):
        cov = self.data.values
        with np.errstate(divide="ignore", invalid="ignore"):
            coeff = np.true_divide(1, self.get_std().values)
            coeff[~np.isfinite(coeff)] = 0  # -inf inf NaN
        corr = np.multiply(np.multiply(cov, coeff).T, coeff)
        df = pd.DataFrame(
            corr,
            index=self.data.index,
            columns=self.data.columns,
        )
        return self.__class__(self.nuclide, df)

    @classmethod
    def from_hdf5(cls, path):
        with h5py.File(path) as f:
            nuclide = list(f.keys())[0]
            mts = sorted([int(k) for k in f[f"{nuclide}/reactions"].keys()])
            energies = f[f"{nuclide}/ENERGIES"][...]
            intervals = [pd.Interval(left, right) for left, right in zip(*energies)]
            index = pd.MultiIndex.from_tuples(
                list(product([nuclide], mts, intervals)), names=["MAT", "MT", "E"]
            )
            df = pd.DataFrame(0.0, index=index, columns=index)
            for colmt, rowmt in product(mts, mts):
                colstd = f[f"{nuclide}/reactions/{colmt}/STD"][...]
                rowstd = f[f"{nuclide}/reactions/{rowmt}/STD"][...]
                data = f[f"{nuclide}/reactions/{colmt}/{rowmt}/DATA"][...]
                indices = f[f"{nuclide}/reactions/{colmt}/{rowmt}/INDICES"][...]
                indptr = f[f"{nuclide}/reactions/{colmt}/{rowmt}/INDPTR"][...]
                shape = f[f"{nuclide}/reactions/{colmt}/{rowmt}/SHAPE"]
                csr = scipy.sparse.csr_array((data, indices, indptr), shape)
                df.loc[(nuclide, rowmt), (nuclide, colmt)] = csr.toarray() * np.outer(
                    rowstd, colstd
                )
            return cls(nuclide, df)

    def submatrix(self, mts):
        df = (self.data.loc[self.nuclide][self.nuclide]
              .loc[mts][mts])
        df = pd.concat({self.nuclide: df}, names=["MAT"])
        df = pd.concat({self.nuclide: df}, names=["MAT"], axis=1)
        return CovMatrix(self.nuclide, df)

    def plot_block(self, mtleft, mtright, path=None, ax=None):
        data = (self.get_corr()
              .data.loc[self.nuclide][self.nuclide]
              .loc[mtleft][mtright])

        if path is None and ax is None:
            raise ValueError("either the path or ax argument must be provided")
        save = False
        if ax is None:
            fig, ax = plt.subplots(1, 1)
            save = True
        
        # data = self.get_corr().data.loc[self.nuclide][self.nuclide]
        matrix = data.to_numpy()
        energies = [i.left for i in data.index] + [data.index[-1].right]
        energies = np.array(energies)

        ax.pcolormesh(energies, energies, matrix, cmap="RdBu", vmin=-1, vmax=1, norm=None)
        ax.set_aspect("equal")
        ax.set_xscale("log")
        ax.set_yscale("log")

        if save:
            ax.invert_yaxis()
            ax.set_xlabel("Energy [eV]")
            ax.set_ylabel("Energy [eV]")
            ax.set_title(f"{self.nuclide}[MT{mtleft}] × {self.nuclide}[MT{mtright}]")
            fig.savefig(path)

    def plot(self, path):
        data = self.get_corr().data.loc[self.nuclide][self.nuclide]
        reactions = sorted(list(set(data.index.get_level_values(0))))
        
        fig, axes = plt.subplots(len(reactions), 
                                 len(reactions), 
                                 sharex=True, 
                                 sharey=True,
                                 figsize=(7, 7))

        for ileft, mtleft in enumerate(reactions):
            for iright, mtright in enumerate(reactions):
                ax = axes[ileft, iright]
                self.plot_block(mtleft, mtright, ax=ax)
                if ileft == len(reactions) - 1:
                    ax.set_xlabel(f"MT{mtright}")
                if iright == 0:
                    ax.set_ylabel(f"MT{mtleft}")

        axes[1, 0].invert_yaxis()
        for ax in axes.flatten():
            ax.set_xticks([])
            ax.set_yticks([])

        fig.suptitle(f"{self.nuclide} cross-section\ncovariances", fontsize=20)
        fig.subplots_adjust(wspace=0, hspace=0)
        fig.savefig(path)