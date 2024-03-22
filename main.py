import argparse
import os

from loguru import logger


parser = argparse.ArgumentParser()
parser.add_argument("--no-console", action="store_true")
parser.add_argument("--no-store-log", action="store_true")
args = parser.parse_args()


if __name__ == "__main__":
    if args.no_console:
        os.environ["CHITUNG_NO_CONSOLE"] = "1"

    import sys

    from chitung.library import launch
    from chitung.library.const import CHITUNG_ROOT
    from chitung.library.util import setup_logger

    os.chdir("chitung")
    sys.path.append(os.path.join(os.getcwd()))

    setup_logger(CHITUNG_ROOT / "log", 7, no_store_log=args.no_store_log)
    logger.info("Launching Chitung...")
    launch()
