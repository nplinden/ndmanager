We vendor the `data` module from `openmc` to avoid the issue of OpenMC not being installable directly from PyPI.

OpenMC is available from: https://github.com/openmc-dev/openmc

Slight changes were made to the module:
- All import path were renamed from `openmc.data.*` to `ndmanager._vendor.omc_data.*`
- The `deplete.nuclide` and `deplete.chain` modules were also added to allow the generation of depletion chains
- The `mixin.py`, `exceptions.py`, `_xml.py` and `openmc/stats/univariate.py` were partially copied

The OpenMC license is reproduced verbatim in this directory.
