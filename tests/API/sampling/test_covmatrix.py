import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from ndmanager.API.sampling.covmatrix import CovMatrix
from ndmanager import compute_file_sha1


def test_covmatrix(install):
    matrix = CovMatrix.from_tape(
        "pytest-artifacts/endf6/foo/n/H1.endf6", ign=3, kind=33
    )
    assert matrix.nuclide == "H1"
    reference = pd.read_csv(
        "tests/API/sampling/H1_covariance.csv", header=[0, 1, 2], index_col=[0, 1, 2]
    )
    assert np.all(np.isclose(matrix.data.to_numpy(), reference.to_numpy()))
    matrix.export_to_hdf5("pytest-artifacts/H1-cov.h5")
    sha1 = compute_file_sha1("pytest-artifacts/H1-cov.h5")
    assert sha1 == "5e67acd460fdec289d9ba3d76b0a702941f04c49"

    matrix = CovMatrix.from_hdf5("pytest-artifacts/H1-cov.h5")
    assert np.all(np.isclose(matrix.data.to_numpy(), reference.to_numpy()))

    p = Path("pytest-artifacts/H1-cov.png")
    matrix.plot(p)
    assert p.exists()

    submatrix = matrix.submatrix([2])
    reference = pd.read_csv(
        "tests/API/sampling/H1_covariance_MT2.csv",
        header=[0, 1, 2],
        index_col=[0, 1, 2],
    )
    assert np.all(np.isclose(submatrix.data.to_numpy(), reference.to_numpy()))

    p = Path("pytest-artifacts/H1-cov-MT2.png")
    matrix.plot_block(2, 2, p)
    assert p.exists()
