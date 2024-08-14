import shutil
import subprocess as sp
import tempfile
import zipfile
from contextlib import chdir
from pathlib import Path

from ndmanager.API.data import ENDF6_LIBS, ENDF6_PATH
from ndmanager.API.nuclide import Nuclide


def download(libname, sublib):
    with tempfile.TemporaryDirectory() as tmpdir:
        with chdir(tmpdir):
            fancyname = ENDF6_LIBS[libname]["fancyname"]
            cmds = [
                "wget",
                "-r",
                "--no-parent",
                '--user-agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:26.0) Gecko/20100101 Firefox/26.0"',
                '--reject html,htm,txt,tmp,"index*","robots*"',
                f"https://www-nds.iaea.org/public/download-endf/{fancyname}/{sublib}/",
            ]

            code = sp.call(
                args=" ".join(cmds), shell=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL
            )
            if code != 0:
                return "✕"

            source = Path(
                f"www-nds.iaea.org/public/download-endf/{fancyname}/{sublib}/"
            )
            for p in source.glob("*zip"):
                with zipfile.ZipFile(p, "r") as zf:
                    zf.extractall(p.parent)
                p.unlink()

            target = ENDF6_PATH / f"{libname}/{sublib}"
            target.parent.mkdir(exist_ok=True, parents=True)
            shutil.rmtree(target, ignore_errors=True)
            shutil.move(source, target)
            if sublib not in ["tsl"]:
                for p in Path(target).glob("*.dat"):
                    nuclide = Nuclide.from_file(p)
                    name = Nuclide.from_file(p).name
                    if nuclide.A == 0:
                        name += "0"
                    p.rename(p.parent / f"{name}.endf6")

    # Some erratafiles
    if libname == "endfb8" and sublib == "n":
        B10 = ENDF6_PATH / f"{libname}/{sublib}" / "B10.endf6"
        with tempfile.TemporaryDirectory() as tmpdir:
            with chdir(tmpdir):
                cmds = [
                    "wget",
                    '--user-agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:26.0) Gecko/20100101 Firefox/26.0"',
                    "https://www.nndc.bnl.gov/endf-b8.0/erratafiles/n-005_B_010.endf",
                ]
                sp.call(
                    args=" ".join(cmds),
                    shell=True,
                    stdout=sp.DEVNULL,
                    stderr=sp.DEVNULL,
                )
                source = Path("n-005_B_010.endf")
                shutil.move(source, B10)
    if libname == "jeff33" and sublib == "tsl":
        tape = ENDF6_PATH / f"{libname}/{sublib}" / "tsl_0026_4-Be.dat"
        lines = open(tape).readlines()
        lines[1] = (
            " 1.260000+2 8.934800+0         -1          0          2          0  26 1451    1\n"
        )
        with open(tape, "w") as f:
            print("".join(lines), file=f)
    if libname == "cendl31" and sublib == "n":
        tape = ENDF6_PATH / f"{libname}/{sublib}" / "Ti47.endf6"
        lines = open(tape).readlines()
        lines[205] = (
            " 8) YUAN Junqian,WANG Yongchang,etc.               ,16,(1),57,92012228 1451  205\n"
        )
        with open(tape, "w") as f:
            print("".join(lines), file=f)

        tape = ENDF6_PATH / f"{libname}/{sublib}" / "B10.endf6"
        lines = open(tape).readlines()
        lines[203] = (
            "21)   Day R.B. and Walt M.  Phys.rev.117,1330 (1960)               525 1451  203\n"
        )
        with open(tape, "w") as f:
            print("".join(lines), file=f)

    return "✓"
