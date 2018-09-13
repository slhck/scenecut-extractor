#!/usr/bin/env python3
#
# Get scene cuts from a video file using ffmpeg.
#
# Author: Werner Robitza
# License: MIT

import argparse
import subprocess
import os
import json
import sys
import tempfile
import re

from .__init__ import __version__ as version


def run_command(cmd, dry=False, verbose=False):
    """
    Run a command directly
    """
    if dry or verbose:
        print("[cmd] " + " ".join(cmd))
        if dry:
            return

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode == 0:
        return stdout.decode("utf-8") + stderr.decode("utf-8")
    else:
        print("[error] running command: {}".format(" ".join(cmd)))
        print(stderr.decode("utf-8"))
        sys.exit(1)


def get_scenecuts(in_f, threshhold=0.3):

    temp_dir = tempfile.gettempdir()
    temp_file_name = os.path.join(
        temp_dir, next(tempfile._get_candidate_names()) + ".txt"
    )

    cmd = [
        "ffmpeg",
        "-loglevel",
        "error",
        "-y",
        "-i",
        in_f,
        "-vf",
        "select=gte(scene\,0),metadata=print:file=" + temp_file_name,
        "-an",
        "-f",
        "null",
        "-",
    ]

    ret = run_command(cmd)

    lines = []
    if os.path.isfile(temp_file_name):
        with open(temp_file_name, "r") as out_f:
            lines = out_f.readlines()
        os.remove(temp_file_name)

    frames = []
    last_frame_info = {}
    for line in lines:
        line = line.strip()
        if line.startswith("frame"):
            rex = r"frame:(?P<frame>\d+)\s+pts:(?P<pts>\d+)\s+pts_time:(?P<pts_time>[\d\.]+)"
            ret = re.match(rex, line)
            if ret:
                ret_matches = ret.groupdict()
                last_frame_info["frame"] = float(ret_matches["frame"])
                last_frame_info["pts"] = float(ret_matches["pts"])
                last_frame_info["pts_time"] = float(ret_matches["pts_time"])
            else:
                raise RuntimeError("Wrongly formatted line: " + line)
            continue
        if line.startswith("lavfi.scene_score"):
            splits = line.split("=")
            if len(splits):
                last_frame_info["score"] = float(splits[1])
            else:
                raise RuntimeError("Wrongly formatted line: " + line)
            frames.append(last_frame_info)
            last_frame_info = {}

    scenecuts = [f for f in frames if f["score"] >= threshhold]

    return scenecuts


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="scenecut_extractor v" + version,
    )
    parser.add_argument("input", help="input file")
    parser.add_argument(
        "-t",
        "--threshhold",
        type=float,
        default=0.3,
        help="threshold (between 0 and 1)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="all",
        choices=["all", "frames", "seconds"],
        help="output what",
    )
    parser.add_argument(
        "-of",
        "--output-format",
        type=str,
        default="json",
        choices=["json", "csv"],
        help="output in which format",
    )

    cli_args = parser.parse_args()

    scenecuts = get_scenecuts(cli_args.input, cli_args.threshhold)

    if cli_args.output == "all":
        if cli_args.output_format == "csv":
            print(",".join(scenecuts[0].keys()))
            print(
                "\n".join(
                    [",".join([str(r) for r in row.values()]) for row in scenecuts]
                )
            )
        else:
            print(json.dumps(scenecuts, indent=2))

    else:
        if cli_args.output == "frames":
            data = [str(s["frame"]) for s in scenecuts]
        elif cli_args.output == "seconds":
            data = [str(s["pts_time"]) for s in scenecuts]
        print("\n".join(data))


if __name__ == "__main__":
    main()
