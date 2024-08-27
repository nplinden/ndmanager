"""Generation of environment modulefiles for use in HPC"""

from ndmanager.data import NDMANAGER_MODULEPATH


def chain_modulefile(filename, description, libpath):
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
setenv OPENMC_CHAIN_FILE "%s"
"""
    text = module_template % (description, description, str(libpath))

    p = NDMANAGER_MODULEPATH / "chains" / filename
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        print(text, file=f)
    return True
