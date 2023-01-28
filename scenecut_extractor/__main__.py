#!/usr/bin/env python3
#
# Get scene cuts from a video file using ffmpeg.
#
# Author: Werner Robitza
# License: MIT

import argparse
import logging
import os
import sys

from .__init__ import __version__ as version
from ._log import CustomLogFormatter
from ._scenecut_extractor import ScenecutExtractor

logger = logging.getLogger("scenecut-extractor")


def setup_logger(level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger("scenecut-extractor")
    logger.setLevel(level)

    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(level)

    ch.setFormatter(CustomLogFormatter())

    logger.addHandler(ch)

    return logger


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="scenecut_extractor v" + version,
    )
    parser.add_argument("input", help="input file")
    parser.add_argument(
        "-t",
        "--threshold",
        type=float,
        default=ScenecutExtractor.DEFAULT_THRESHOLD,
        help="threshold (between 0 and 1)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="all",
        choices=["all", "frames", "seconds"],
        help="output which information",
    )
    parser.add_argument(
        "-of",
        "--output-format",
        type=str,
        default="json",
        choices=["json", "csv"],
        help="output in which format",
    )
    parser.add_argument(
        "-x", "--extract", action="store_true", help="extract the scene cuts"
    )
    parser.add_argument(
        "-d",
        "--output-directory",
        help="Set the output directory. Default is the current working directory.",
    )
    parser.add_argument(
        "--no-copy",
        action="store_true",
        help="Don't stream-copy, but re-encode the video.",
    )
    parser.add_argument(
        "-p", "--progress", action="store_true", help="Show a progress bar on stderr"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Print verbose info to stderr"
    )

    cli_args = parser.parse_args()

    setup_logger(logging.DEBUG if cli_args.verbose else logging.INFO)

    logger.info("Calculating scene cuts ...")
    se = ScenecutExtractor(cli_args.input)
    se.calculate_scenecuts(
        cli_args.threshold,
        progress=cli_args.progress,
    )

    scenecuts = se.get_scenecuts()

    if cli_args.output == "all":
        if cli_args.output_format == "csv":
            print(se.get_as_csv())
        else:
            print(se.get_as_json())

    else:
        if cli_args.output == "frames":
            data = [str(s["frame"]) for s in scenecuts]
        elif cli_args.output == "seconds":
            data = [str(s["pts_time"]) for s in scenecuts]
        else:
            raise RuntimeError(f"No such output format: {cli_args.output}")
        print("\n".join(data))

    if cli_args.extract:
        logger.info("Extracting scenes ...")
        se.extract_scenes(
            output_directory=cli_args.output_directory
            if cli_args.output_directory
            else os.getcwd(),
            no_copy=cli_args.no_copy,
            progress=cli_args.progress,
        )


if __name__ == "__main__":
    main()
