#!/usr/bin/env pytest

import json
import os
import shutil
import subprocess

TEST_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "test.mp4"))


def run_command(cmd):
    """
    Run a command directly
    """
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode == 0:
        return stdout.decode("utf-8"), stderr.decode("utf-8")
    else:
        raise RuntimeError(
            "[error] running command {}: {}".format(
                " ".join(cmd), stderr.decode("utf-8")
            )
        )


class TestOutput:
    def test_json_output(self):
        """
        Test JSON output
        """
        stdout, _ = run_command(["python3", "-m", "scenecut_extractor", TEST_FILE])
        output = json.loads(stdout)

        expected_output = [
            {"frame": 24, "pts": 12288.0, "pts_time": 0.96, "score": 1.0},
            {"frame": 49, "pts": 25088.0, "pts_time": 1.96, "score": 1.0},
            {"frame": 74, "pts": 37888.0, "pts_time": 2.96, "score": 1.0},
            {"frame": 99, "pts": 50688.0, "pts_time": 3.96, "score": 1.0},
            {"frame": 124, "pts": 63488.0, "pts_time": 4.96, "score": 1.0},
            {"frame": 149, "pts": 76288.0, "pts_time": 5.96, "score": 1.0},
            {"frame": 174, "pts": 89088.0, "pts_time": 6.96, "score": 1.0},
        ]

        assert output == expected_output

    def test_csv_output(self):
        """
        Test CSV output
        """
        stdout, _ = run_command(
            ["python3", "-m", "scenecut_extractor", TEST_FILE, "-of", "csv"]
        )
        stdout = stdout.strip()

        expected_output = "frame,pts,pts_time,score\n24,12288.0,0.96,1.0\n49,25088.0,1.96,1.0\n74,37888.0,2.96,1.0\n99,50688.0,3.96,1.0\n124,63488.0,4.96,1.0\n149,76288.0,5.96,1.0\n174,89088.0,6.96,1.0"

        assert stdout == expected_output

    def test_splitting(self):
        """
        Test if we can split the input file
        """
        try:
            stdout, _ = run_command(
                [
                    "python3",
                    "-m",
                    "scenecut_extractor",
                    TEST_FILE,
                    "-of",
                    "json",
                    "-x",
                    "-d",
                    "tmp",
                ]
            )

            scenecuts = json.loads(stdout)
            scenecuts.insert(0, {"frame": 0, "pts": 0.0, "pts_time": 0.0, "score": 1.0})

            for scenecut, next_scenecut in zip(scenecuts[:-1], scenecuts[1:]):
                assert os.path.exists(
                    os.path.join(
                        "tmp",
                        f"test_{scenecut['pts_time']:.3f}-{next_scenecut['pts_time']:.3f}.mkv",
                    )
                )
        finally:
            shutil.rmtree("tmp")
