"""A class to generate covariance matrix libraries"""

from itertools import product
from pathlib import Path
from typing import List

import h5py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sandy
import scipy.sparse

import ndmanager


class CovMatrix(sandy.CategoryCov):
    """A class to generate covariance matrix libraries"""

    def __init__(self, nuclide: str, data: pd.DataFrame):
        """Instantiate a covariance matrix using a nuclide name
        and a dataframe containing covariances.

        Args:
            nuclide (str): The name of the nuclide
            data (pd.DataFrame): The dataframe containing the covariances
        """
        self.nuclide = nuclide
        super().__init__(data)

    @classmethod
    def from_tape(
        cls, path: str | Path, ign: int = 3, kind: int = 33, **kwargs
    ) -> "CovMatrix":
        """Build a covariance matrix from an ENDF6 file, provided and group structure
        using NJOY's nomenclature.

        Args:
            path (str | Path): Path to an ENDF6 file
            ign (int, optional): The group structure using NJOY's ids. Defaults to 3.
            kind (int, optional): The kind of covariance matrix, only cross-sections
                                  (kind=33) is available for now. Defaults to 33.

        Raises:
            ValueError: If the requested matrix does not exist in the tape.

        Returns:
            CovMatrix: The covariance matrix object.
        """
        nuclide = ndmanager.Endf6(path).nuclide.name
        tape = sandy.endf6.Endf6.from_file(path)
        errorr = tape.get_errorr(errorr33_kws={"ign": ign}, **kwargs)
        if "errorr33" not in errorr:
            raise ValueError("No suitable MF33 found.")
        data = errorr["errorr33"].get_cov().data
        data.columns = data.columns.set_levels([nuclide], level=0)
        data.index = data.index.set_levels([nuclide], level=0)
        return cls(nuclide, data)

    def export_to_hdf5(self, path: str | Path) -> None:
        """Write the covariance matrix to an HDF5 format.

        Args:
            path (str | Path): The path to the HDF5 file to write.
        """
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

    @classmethod
    def from_hdf5(cls, path: str | Path) -> "CovMatrix":
        """Reads an HDF5 file to build a covariance matrix

        Args:
            path (str | Path): The path to the HDF5 file

        Returns:
            CovMatrix: A CovMatrix object
        """
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

    def submatrix(self, mts: List[int]) -> "CovMatrix":
        """Extract a submatrix from the covariance matrix

        Args:
            mts (List[int]): The list of reactions to include in the matrix

        Returns:
            CovMatrix: A new CovMatrix object
        """
        df = self.data.loc[self.nuclide][self.nuclide].loc[mts][mts]
        df = pd.concat({self.nuclide: df}, names=["MAT"])
        df = pd.concat({self.nuclide: df}, names=["MAT"], axis=1)
        return CovMatrix(self.nuclide, df)

    def plot_block(
        self, mtleft: int, mtright: int, path: str | Path = None, ax: plt.Axes = None
    ) -> None:
        """Plot the block corresponding the to covariances between reactions `mtleft`
        and `mtright`. If an Axes object is provided the matrix will be drawn on the ax.
        If a path is provided a matplotlib figure and ax will be created and the matrix
        will be saved to a file.

        Args:
            mtleft (int): The first reaction
            mtright (int): The second reaction
            path (str | Path, optional): The path to the plot file. Defaults to None.
            ax (plt.Axes, optional): A matplotlib ax to plot on. Defaults to None.

        Raises:
            ValueError: If neither path of ax is provided
            ValueError: If both path and ax are provided
        """
        data = self.get_corr().data.loc[self.nuclide][self.nuclide].loc[mtleft][mtright]

        if path is None and ax is None:
            raise ValueError("Either the path or ax argument must be provided")
        if path is not None and ax is not None:
            raise ValueError("Only one of ax of path can be provided at the same time")
        save = False
        if ax is None:
            fig, ax = plt.subplots(1, 1)
            save = True

        matrix = data.to_numpy()
        energies = [i.left for i in data.index] + [data.index[-1].right]
        energies = np.array(energies)

        ax.pcolormesh(
            energies, energies, matrix, cmap="RdBu", vmin=-1, vmax=1, norm=None
        )
        ax.set_aspect("equal")
        ax.set_xscale("log")
        ax.set_yscale("log")

        if save:
            ax.invert_yaxis()
            ax.set_xlabel("Energy [eV]")
            ax.set_ylabel("Energy [eV]")
            ax.set_title(f"{self.nuclide}[MT{mtleft}] × {self.nuclide}[MT{mtright}]")
            fig.savefig(path)

    def plot(self, path: str | Path) -> None:
        """Plot the covariance matrix and save the result to a file

        Args:
            path (str | Path): The path to save the image at
        """
        data = self.get_corr().data.loc[self.nuclide][self.nuclide]
        reactions = sorted(list(set(data.index.get_level_values(0))))

        fig, axes = plt.subplots(
            len(reactions), len(reactions), sharex=True, sharey=True, figsize=(7, 7)
        )

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

    def get_corr(self) -> "CovMatrix":
        """Extract correlation matrix. Copied from Sandy

        Returns:
            CovMatrix: The correlation matrix
        """
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

    def correct_lognormal(self):
        """Copied from sandy.cov.CategoryCov::correct_lognormal"""
        C = self.data.copy()

        # this condition limits covariances to max -100 %
        mask = C.values < -1

        if mask.any():
            size = (mask.size - mask.diagonal().size) // 2
            how_many_bad_values = mask.sum() // 2
            smallest_bad_value = C[mask].min().min()

            msg = f"""Condition COV + 1 > 0 for Lognormal sampling is not respected.
    {how_many_bad_values}/{size} covariance coefficients are set to -1+eps.
    The smallest covariance is {smallest_bad_value:.5f}
    """
            if "MT" in C.index.names:
                bad_mts = (
                    C.index[np.where(mask)[0]].get_level_values("MT").unique().tolist()
                )
                msg += f"The concerned MT numbers are {bad_mts}."

            C[mask] = -1 + np.finfo(np.float64).eps

        return self.__class__(self.nuclide, C)

    def transform_lognormal(self):
        """Copied from sandy.cov.CategoryCov::transform_lognormal"""
        C = self.data.copy()
        C = np.log(C + 1)
        return self.__class__(self.nuclide, C)

    def regularize(self, correction):
        """Copied from sandy.cov.CategoryCov::regularize"""
        C = self.data.copy()
        D = np.diag(C.values.diagonal() * correction)
        C += D
        return self.__class__(self.nuclide, C)
