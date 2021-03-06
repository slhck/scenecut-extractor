#!/usr/bin/env python3
#
# Get scene cuts from a video file using ffmpeg.
#
# Author: Werner Robitza
# License: MIT

import argparse
import os
import json
import sys
import tempfile
import re
import shlex
from tqdm import tqdm
from ffmpeg_progress_yield import FfmpegProgress

from .__init__ import __version__ as version

def get_scenecuts(in_f, threshold=0.3, progress=False, verbose=False):
    """
    Calculate scene cuts with ffmpeg.
    """
    if not (0 <= threshold <= 1):
        raise RuntimeError("Threshold must be between 0 and 1")

    try:
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

        if verbose:
            cmd_q = " ".join([shlex.quote(c) for c in cmd])
            print("Running ffmpeg command: {}".format(cmd_q), file=sys.stderr)

        ff = FfmpegProgress(cmd)
        if progress:
            with tqdm(total=100, position=1) as pbar:
                for progress in ff.run_command_with_progress():
                    pbar.update(progress - pbar.n)
        else:
            for _ in ff.run_command_with_progress():
                pass

        lines = []
        if os.path.isfile(temp_file_name):
            with open(temp_file_name, "r") as out_f:
                lines = out_f.readlines()

        frames = []
        last_frame_info = {}
        for line in lines:
            line = line.strip()
            if line.startswith("frame"):
                rex = r"frame:(?P<frame>\d+)\s+pts:(?P<pts>[\d\.]+)\s+pts_time:(?P<pts_time>[\d\.]+)"
                ret = re.match(rex, line)
                if ret:
                    ret_matches = ret.groupdict()
                    last_frame_info["frame"] = int(ret_matches["frame"])
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

        scenecuts = [f for f in frames if f["score"] >= threshold]

    except Exception as e:
        raise e
    finally:
        if os.path.isfile(temp_file_name):
            os.remove(temp_file_name)

    return scenecuts


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
    parser.add_argument(
        "-p", "--progress", action="store_true", help="Show a progress bar on stderr"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Print verbose info to stderr"
    )

    cli_args = parser.parse_args()

    scenecuts = get_scenecuts(
        cli_args.input,
        cli_args.threshold,
        progress=cli_args.progress,
        verbose=cli_args.verbose,
    )

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
        else:
            raise RuntimeError(f"No such output format: {cli_args.output}")
        print("\n".join(data))


if __name__ == "__main__":
    main()
