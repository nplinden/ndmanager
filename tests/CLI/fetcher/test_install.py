import pytest
import hashlib
from pathlib import Path


from ndmanager.CLI.fetcher.install import download_test
from ndmanager.data import ENDF6_PATH, TAPE_SHA1


# def test_download_test():
#     download_test()
#     BUF_SIZE = 65536
#     for sublib in Path(ENDF6_PATH / "test").glob("*"):
#         for tape in sublib.glob("*"):
#             sha1 = hashlib.sha1()
#             with open(tape, "rb") as f:
#                 while True:
#                     data = f.read(BUF_SIZE)
#                     if not data:
#                         break
#                     sha1.update(data)
#             key = f"test/{sublib.name}/{tape.stem}"
#             assert sha1.hexdigest() == TAPE_SHA1["test"][key]
