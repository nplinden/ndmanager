import pytest
import pandas as pd
import numpy as np

from ndmanager.API.sampling.covmatrix import CovMatrix
from ndmanager import compute_file_sha1

def test_covmatrix(install):
    matrix = CovMatrix.from_tape(
        "pytest-artifacts/endf6/foo/n/H1.endf6",
        ign=3,
        kind=33
    )
    assert matrix.nuclide == "H1"
    reference = pd.read_csv("tests/API/sampling/H1_covariance.csv",
                            header=[0, 1, 2],
                            index_col=[0, 1, 2])
    assert np.all(np.isclose(matrix.data.to_numpy(), reference.to_numpy()))
    matrix.export_to_hdf5("pytest-artifacts/H1-cov.h5")
    sha1 = compute_file_sha1("pytest-artifacts/H1-cov.h5")
    assert sha1 == "5e67acd460fdec289d9ba3d76b0a702941f04c49"

    matrix = CovMatrix.from_hdf5("pytest-artifacts/H1-cov.h5")
    assert np.all(np.isclose(matrix.data.to_numpy(), reference.to_numpy()))

    matrix.plot("pytest-artifacts/H1-cov.png")
    sha1 = compute_file_sha1("pytest-artifacts/H1-cov.png")
    assert sha1 == "2ceeaff698812a1788d27235b4304bc1e20b6663"

    submatrix = matrix.submatrix([2])
    reference = pd.read_csv("tests/API/sampling/H1_covariance_MT2.csv",
                            header=[0, 1, 2],
                            index_col=[0, 1, 2])
    assert np.all(np.isclose(submatrix.data.to_numpy(), reference.to_numpy()))

    matrix.plot_block(2, 2, "pytest-artifacts/H1-cov-MT2.png")
    sha1 = compute_file_sha1("pytest-artifacts/H1-cov-MT2.png")
    assert sha1 == "b9152f91e9292a8d5431750cfa3a4feebfb77c6d"





