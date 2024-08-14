import time
from multiprocessing import Pool

from ndmanager.API.utils import clear_line


def process(dest, library, processor, args, evaltype, key=lambda x: x):
    t0 = time.time()
    print(f"Processing {evaltype} evaluations: 0/{len(args)}")
    print(f"Time elapsed: 0 s.")
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
