from ndmanager.data import NDMANAGER_MODULEPATH


def xs_modulefile(filename, description, libpath):
    module_template = r"""#%%Module
proc ModulesHelp { } {
    puts stderr "%s"
}
module-whatis "%s\n"
setenv OPENMC_CROSS_SECTIONS "%s"
"""
    text = module_template % (description, description, str(libpath))
    with open(NDMANAGER_MODULEPATH / filename, "w") as f:
        print(text, file=f)
    return True

