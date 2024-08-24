"""Generation of environment modulefiles for use in HPC"""

from ndmanager.data import NDMANAGER_MODULEPATH


def xs_modulefile(filename: str, description: str, libpath: str):
    """Create a modulefile for use by environment modules

    Args:
        filename (str): The name of the modulefile
        description (str): A description of the module
        libpath (str): The path to the library to load
    """
    module_template = r"""#%%Module
proc ModulesHelp { } {
    puts stderr "%s"
}
module-whatis "%s\n"
setenv OPENMC_CROSS_SECTIONS "%s"
"""
    text = module_template % (description, description, str(libpath))
    (NDMANAGER_MODULEPATH / filename).parent.mkdir(parents=True, exist_ok=True)
    with open(NDMANAGER_MODULEPATH / filename, "w", encoding="utf-8") as f:
        print(text, file=f)
