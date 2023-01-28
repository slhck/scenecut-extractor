from __future__ import annotations

import json
import logging
import os
import re
import shlex
import tempfile
from typing import Literal, TypedDict, Union, cast

from ffmpeg_progress_yield import FfmpegProgress
from tqdm import tqdm

logger = logging.getLogger("scenecut-extractor")


class ScenecutInfo(TypedDict):
    frame: int
    """The frame number"""
    pts: int
    """The PTS of the frame"""
    pts_time: float
    """The PTS in wall clock time of the frame"""
    score: float
    """The scenecut detection score"""


class ScenecutExtractor:
    DEFAULT_THRESHOLD: float = 0.3

    def __init__(self, input_file: str) -> None:
        """
        Create a new ScenecutExtractor instance.

        Args:
            input_file (str): the input file
        """
        self.scenecuts: list[ScenecutInfo] = []
        self.input_file = input_file

    def get_as_csv(self) -> str:
        """
        Return the scene cuts as CSV.

        Returns:
            str: the scene cuts as CSV

        Raises:
            RuntimeError: if no scene cuts have been calculated yet
        """
        if len(self.scenecuts) == 0:
            raise RuntimeError("No scene cuts calculated yet")

        ret = ",".join(self.scenecuts[0].keys()) + "\n"
        ret += "\n".join(
            [",".join([str(r) for r in row.values()]) for row in self.scenecuts]
        )

        return ret

    def get_as_json(self) -> str:
        """
        Return the scene cuts as JSON.

        Returns:
            str: the scene cuts as JSON

        Raises:
            RuntimeError: if no scene cuts have been calculated yet
        """
        if len(self.scenecuts) == 0:
            raise RuntimeError("No scene cuts calculated yet")

        return json.dumps(self.scenecuts, indent=2)

    def get_scenecuts(self) -> list[ScenecutInfo]:
        """
        Get the scene cuts.

        Returns:
            list[ScenecutInfo]: the scene cuts
        """
        return self.scenecuts

    def calculate_scenecuts(
        self, threshold: float = DEFAULT_THRESHOLD, progress: bool = False
    ) -> None:
        """
        Calculate scene cuts with ffmpeg.

        Args:
            threshold (float): Threshold (between 0 and 1)
            progress (bool): Show a progress bar on stderr
        """
        if not (0 <= threshold <= 1):
            raise RuntimeError("Threshold must be between 0 and 1")

        temp_dir = tempfile.mkdtemp()
        temp_file_name = os.path.join(
            temp_dir, "scenecut-extractor-" + os.path.basename(self.input_file) + ".txt"
        )

        logger.debug("Writing to temp file: " + temp_file_name)

        try:
            cmd = [
                "ffmpeg",
                "-nostdin",
                "-loglevel",
                "error",
                "-y",
                "-i",
                self.input_file,
                "-vf",
                "select=gte(scene\,0),metadata=print:file=" + temp_file_name,
                "-an",
                "-f",
                "null",
                os.devnull,
            ]

            logger.debug(
                "Running ffmpeg command: " + " ".join([shlex.quote(c) for c in cmd])
            )

            ff = FfmpegProgress(cmd)
            if progress:
                with tqdm(total=100, position=1) as pbar:
                    for p in ff.run_command_with_progress():
                        pbar.update(p - pbar.n)
            else:
                for _ in ff.run_command_with_progress():
                    pass

            lines: list[str] = []
            if os.path.isfile(temp_file_name):
                with open(temp_file_name, "r") as out_f:
                    lines = out_f.readlines()

            frames: list[ScenecutInfo] = []
            last_frame_info: dict = {}
            for line in lines:
                line = line.strip()
                if line.startswith("frame"):
                    if ret := re.match(
                        r"frame:(?P<frame>\d+)\s+pts:(?P<pts>[\d\.]+)\s+pts_time:(?P<pts_time>[\d\.]+)",
                        line,
                    ):
                        ret_matches = ret.groupdict()
                        last_frame_info["frame"] = int(ret_matches["frame"])
                        last_frame_info["pts"] = float(ret_matches["pts"])
                        last_frame_info["pts_time"] = float(ret_matches["pts_time"])
                    else:
                        raise RuntimeError("Wrongly formatted line: " + line)
                    continue

                if line.startswith("lavfi.scene_score") and (splits := line.split("=")):
                    if len(splits):
                        last_frame_info["score"] = float(splits[1])
                    else:
                        raise RuntimeError("Wrongly formatted line: " + line)
                    frames.append(cast(ScenecutInfo, last_frame_info))
                    last_frame_info = {}

            self.scenecuts = [f for f in frames if f["score"] >= threshold]

        except Exception as e:
            raise e
        finally:
            if os.path.isfile(temp_file_name):
                logger.debug("Removing temp file: " + temp_file_name)
                os.remove(temp_file_name)

    def extract_scenes(
        self,
        output_directory: str,
        no_copy: bool = False,
        progress: bool = False,
    ):
        """
        Extract all scenes to individual files.

        Args:
            output_directory (str): Output directory.
            no_copy (bool, optional): Do not copy the streams, reencode them. Defaults to False.
            progress (bool, optional): Show progress bar. Defaults to False.
        """
        if len(self.scenecuts) == 0:
            raise RuntimeError("No scene cuts calculated yet")

        # insert one at the beginning
        scenecuts = self.scenecuts[:]
        scenecuts.insert(0, {"pts_time": 0, "pts": 0, "frame": 0, "score": 0})

        if not os.path.exists(output_directory):
            os.makedirs(output_directory, exist_ok=True)

        for scene, next_scene in zip(scenecuts, scenecuts[1:]):
            self.cut_part_from_file(
                self.input_file,
                output_directory,
                scene["pts_time"],
                next_scene["pts_time"],
                no_copy,
                progress,
            )

    @staticmethod
    def cut_part_from_file(
        input_file: str,
        output_directory: str,
        start: Union[float, None] = None,
        end: Union[float, None, Literal[""]] = None,
        no_copy: bool = False,
        progress: bool = False,
    ):
        """
        Cut a part of a video.

        Args:
            input_file (str): Input file.
            output_directory (str): Output directory.
            start (Union[float, None], optional): Start time. Defaults to None.
            end (Union[float, None, Literal[""]], optional): End time. Defaults to None.
            no_copy (bool, optional): Do not copy the streams, reencode them. Defaults to False.
            progress (bool, optional): Show progress bar. Defaults to False.

        FIXME: This has been copy-pasted from ffmpeg-black-split.
        """
        if start is None:
            start = 0

        if end is not None and end != "":
            to_args = ["-t", str(end - start)]
        else:
            end = ""
            to_args = []

        if no_copy:
            codec_args = ["-c:v", "libx264", "-c:a", "aac"]
        else:
            codec_args = ["-c", "copy"]

        suffix = f"{start:.3f}-{end:.3f}.mkv"
        prefix = os.path.splitext(os.path.basename(input_file))[0]
        output_file = os.path.join(output_directory, f"{prefix}_{suffix}")

        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-y",
            "-ss",
            str(start),
            "-i",
            input_file,
            *to_args,
            *codec_args,
            "-map",
            "0",
            output_file,
        ]

        cmd_q = " ".join([shlex.quote(c) for c in cmd])
        logger.debug("Running ffmpeg command: {}".format(cmd_q))

        ff = FfmpegProgress(cmd)
        if progress:
            with tqdm(total=100, position=1) as pbar:
                for p in ff.run_command_with_progress():
                    pbar.update(p - pbar.n)
        else:
            for _ in ff.run_command_with_progress():
                pass
