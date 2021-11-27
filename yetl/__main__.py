import argparse
from .metaconf import Project
from .logging import getLogger
import os


def main(raw_args=None):

    parser = argparse.ArgumentParser("Description YETL cli")
    parser.add_argument(
        "-p",
        "--path",
        help="path to the YETL Projection Configuration. This can be a physical path or an OS varaibles that container a path.",
        required=True
    )
    parser.add_argument(
        "-v",
        "--pathisvar",
        help="indicates that the path is an OS variable",
        action='store_true'
    )

    args = vars(parser.parse_args(raw_args))

    path:str = args["path"]
    path_is_variable:bool = bool(args["pathisvar"])

    logger = getLogger(__name__)

    logger.info(f"building project path={path}, path_is_variable={path_is_variable}")

    project = Project(path, path_is_variable)


if __name__ == "__main__":
    main()