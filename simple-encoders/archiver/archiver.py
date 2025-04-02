import logging_config
logger = logging_config.get_logger(__name__)
logger.debug(f"start::{__name__}")
from cryptography.fernet import Fernet
from zipfile import ZipFile, ZIP_DEFLATED
from datetime import datetime
import os

def archiving(dir_path, arc_path):
    def walk():
        for path, _, files in os.walk(dir_path):
            for name in files:
                yield os.path.relpath(os.path.join(path, name), start=dir_path)
    with ZipFile(arc_path, "w", compression=ZIP_DEFLATED, compresslevel=3) as zf:
        for fn in walk():
            zf.write(os.path.join(dir_path,fn), fn)
        ok = zf.testzip()
        if ok is not None:
            logger.error(f"arc.testzip='{zf.testzip()}'")
    logger.info(f"archiv::{dir_path}::{arc_path}")

def unarchiving(arc_path, dir_path):
    if os.path.exists(dir_path):
        dir_path += f" @{datetime.now().timestamp()}"
    with ZipFile(arc_path, "r") as zf:
        zf.extractall(dir_path)
    logger.info(f"unarch::{dir_path}::{arc_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(prog='archiver.py')
    parser.add_argument('-u', action='store_true', help='turn on unarchiving mode')
    parser.add_argument('dir', type=str, help='Input directory for archiving')
    parser.add_argument('arc', type=str, help='Output archive file')
    args = parser.parse_args()
    dir_path = args.dir
    arc_path = args.arc
    if args.u:
        unarchiving(dir_path, arc_path)
    else:
        archiving(dir_path, arc_path)
    logger.debug(f"end::{__name__}")

    # FOR TESTING
    # python archiver.py "../../_dummy/root_folder/" "../../_dummy/dummy-storage.zip"


