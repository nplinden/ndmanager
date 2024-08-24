"""A function that encapsulates nuclear data processing from OpenMC"""

import time
from multiprocessing import Pool
from pathlib import Path
from typing import Callable, Tuple

import openmc.data

from ndmanager.format import clear_line


def process(
    dest: Path,
    library: openmc.data.DataLibrary,
    processor: Callable,
    args: Tuple,
    evaltype: str,
    key: Callable = lambda x: x,
):
    """Encapsulation fo the nuclear data processing capabilities of OpenMC

    Args:
        dest (Path): The directory to write the files to
        library (openmc.data.DataLibrary): The library object
        processor (function): The function use to process the data
        args (Tuple): The list of arguments to pass to the processor
        evaltype (str): The desired type of evaluation
        key (_type_, optional): The sort key for the cross_sections.xml file. Defaults to lambdax:x.
    """
    t0 = time.time()
    print(f"Processing {evaltype} evaluations: 0/{len(args)}")
    print("Time elapsed: 0 s.")
    with Pool() as p:
        results = [p.apply_async(processor, arg) for arg in args]
        while 1:
            time.sleep(0.5)
            isdone = [r.ready() for r in results]
            ndone = sum(isdone)
            clear_line(2)
            print(f"Processing {evaltype} evaluations: {ndone:4d}/{len(isdone)}")
            print(f"Time elapsed: {time.time() - t0:.1f} s.")
            if ndone == len(isdone):
                break
        for path in sorted(dest.glob("*.h5"), key=key):
            library.register_file(path)
    clear_line(2)
    print(f"Processing {evaltype} evaluations: {ndone:4d}/{len(isdone)}")
    print(f"Time elapsed: {time.time() - t0:.1f} s.")
