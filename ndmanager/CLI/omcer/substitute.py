from ndmanager.CLI.omcer.edit import (find_negative_in_lib,
                                      find_nuclide_in_lib, overwrite,
                                      set_negative_to_zero)


def replace_negatives_in_lib(targetlib, sources, mt, dryrun=False, verbose=True):
    negatives = find_negative_in_lib(targetlib, mt)
    source_negatives = {source: find_negative_in_lib(source, mt) for source in sources}

    for nuclide in negatives:
        found = False
        source = None
        target = None
        for sourcelib, sn in source_negatives.items():
            source = find_nuclide_in_lib(sourcelib, nuclide)
            target = find_nuclide_in_lib(targetlib, nuclide)
            if source is None:
                continue
            elif nuclide in sn:
                continue
            else:
                found = True
                if verbose:
                    print(
                        f"Replacing\n\tnuclide={nuclide}\n\tmt={mt}\n\ttarget={target}\n\tsource={source}"
                    )
                if not dryrun:
                    overwrite(nuclide, mt, source, target)
                continue
        if not found:
            if verbose:
                print(
                    f"No replacement found\n\tnuclide={nuclide}\n\tmt={mt}\n\ttarget={target}\n\tsource={source}"
                )
            if not dryrun:
                set_negative_to_zero(target, nuclide, mt)
    return
