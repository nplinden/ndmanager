import subprocess as sp
from pathlib import Path
import argparse as ap
import zipfile
import tempfile
from contextlib import chdir
import shutil
from itertools import product
from multiprocessing import Pool
from ndfetcher.data import NSUB, NDLIBS

def download(libname, reaction):
    current = Path(".").absolute()
    with tempfile.TemporaryDirectory() as tmpdir:
        with chdir(tmpdir):
            fancyname = NDLIBS[libname]
            cmds = [
                "wget",
                "-r",
                "--no-parent",
                '--user-agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:26.0) Gecko/20100101 Firefox/26.0"',
                '--reject html,htm,txt,tmp,"index*","robots*"',
                f'https://www-nds.iaea.org/public/download-endf/{fancyname}/{reaction}/',
            ]

            code = sp.call(args=" ".join(cmds), shell=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
            if code != 0:
                print(f"{libname:10} {reaction:4} None")
                return

            source = Path(f"www-nds.iaea.org/public/download-endf/{fancyname}/{reaction}/")
            for p in source.glob("*zip"):
                with zipfile.ZipFile(p, "r") as zf:
                    zf.extractall(p.parent)
                p.unlink()

            target = current / f"{libname}/{reaction}"
            target.parent.mkdir(exist_ok=True, parents=True)
            shutil.rmtree(target, ignore_errors=True)
            shutil.move(source, target)
    print(f"{libname:10} {reaction:4} {target}")
    return target

def download_cli():
    parser = ap.ArgumentParser(
        prog="ndfetch",
        description="Fetch nuclear data",
    )
    parser.add_argument("libname", 
                        type=str,
                        help=f"The name of the library to download, from {{{list(NDLIBS.keys())}}}")
    parser.add_argument("nsub",
                        nargs="*",
                        type=str,
                        help=f"Sublibrary type, from {{{NSUB}}}")
    args = parser.parse_args()
    
    assert args.libname in NDLIBS
    if not args.nsub:
        stargs = list(product([args.libname], NSUB))
    else:
        for nsub in args.nsub:
            assert nsub in NSUB
        stargs = list(product([args.libname], args.nsub))

    print("Downloading: ")
    for s in stargs:
        print(f"\t{s[0]}/{s[1]}")
    with Pool() as p:
        p.starmap(download, stargs)


    #download(args.libname, args.nsub)

# if __name__=="__main__":
#     download_cli()

# if __name__=="__main__":
#     parser = ap.ArgumentParser(
#         prog="ndfetch",
#         description="Fetch nuclear data",
#     )
#     parser.add_argument("--libname", "-l", 
#                         type=str,
#                         help=f"The name of the library to download, from {{{list(NDLIBS.keys())}}}")
#     parser.add_argument("--nsub", "-n",
#                         type=str,
#                         help=f"Sublibrary type, from {{{NSUB}}}")