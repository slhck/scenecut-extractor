#!/usr/bin/env pytest

import json
import os
import shutil
import subprocess

import pytest

from scenecut_extractor import ScenecutExtractor

TEST_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "test.mp4"))
TEST_FILE_DURATION = 7.96
TEST_FILE_FRAMES = 199


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


def count_frames(path):
    """
    Count the video frames in a file with ffprobe
    """
    stdout, _ = run_command(
        [
            "ffprobe",
            "-v",
            "error",
            "-count_frames",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=nb_read_frames",
            "-of",
            "csv=p=0",
            path,
        ]
    )
    return int(stdout.strip())


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
        Test if we can split the input file.
        By default, the output extension should match the input file.
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
            scenecuts.append({"pts_time": TEST_FILE_DURATION})

            for scenecut, next_scenecut in zip(scenecuts[:-1], scenecuts[1:]):
                assert os.path.exists(
                    os.path.join(
                        "tmp",
                        f"test_{scenecut['pts_time']:.3f}-{next_scenecut['pts_time']:.3f}.mp4",
                    )
                )
        finally:
            shutil.rmtree("tmp")

    def test_splitting_with_output_extension(self):
        """
        Test if we can split the input file with a custom output extension.
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
                    "-e",
                    ".mkv",
                ]
            )

            scenecuts = json.loads(stdout)
            scenecuts.insert(0, {"frame": 0, "pts": 0.0, "pts_time": 0.0, "score": 1.0})
            scenecuts.append({"pts_time": TEST_FILE_DURATION})

            for scenecut, next_scenecut in zip(scenecuts[:-1], scenecuts[1:]):
                assert os.path.exists(
                    os.path.join(
                        "tmp",
                        f"test_{scenecut['pts_time']:.3f}-{next_scenecut['pts_time']:.3f}.mkv",
                    )
                )
        finally:
            shutil.rmtree("tmp")

    def test_output_file_json(self):
        """
        Test JSON output to file
        """
        output_file = "tmp_output.json"
        try:
            run_command(
                [
                    "python3",
                    "-m",
                    "scenecut_extractor",
                    TEST_FILE,
                    "-O",
                    output_file,
                ]
            )

            assert os.path.exists(output_file)

            with open(output_file, "r") as f:
                output = json.load(f)

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
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)

    def test_output_file_csv(self):
        """
        Test CSV output to file
        """
        output_file = "tmp_output.csv"
        try:
            run_command(
                [
                    "python3",
                    "-m",
                    "scenecut_extractor",
                    TEST_FILE,
                    "-of",
                    "csv",
                    "-O",
                    output_file,
                ]
            )

            assert os.path.exists(output_file)

            with open(output_file, "r") as f:
                content = f.read().strip()

            expected_output = "frame,pts,pts_time,score\n24,12288.0,0.96,1.0\n49,25088.0,1.96,1.0\n74,37888.0,2.96,1.0\n99,50688.0,3.96,1.0\n124,63488.0,4.96,1.0\n149,76288.0,5.96,1.0\n174,89088.0,6.96,1.0"

            assert content == expected_output
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)

    def test_splitting_with_crf_and_preset(self):
        """
        Test if re-encoding uses the given CRF value and preset.
        """
        try:
            _, stderr = run_command(
                [
                    "python3",
                    "-m",
                    "scenecut_extractor",
                    TEST_FILE,
                    "-x",
                    "-d",
                    "tmp",
                    "--no-copy",
                    "--crf",
                    "35",
                    "--preset",
                    "ultrafast",
                    "-v",
                ]
            )

            assert "-c:v libx264 -crf 35 -preset ultrafast" in stderr
            assert os.path.exists(os.path.join("tmp", "test_0.000-0.960.mp4"))
        finally:
            shutil.rmtree("tmp")

    def test_splitting_without_reencoding_ignores_crf(self):
        """
        Test that stream-copying does not pass CRF or preset to ffmpeg.
        """
        try:
            _, stderr = run_command(
                [
                    "python3",
                    "-m",
                    "scenecut_extractor",
                    TEST_FILE,
                    "-x",
                    "-d",
                    "tmp",
                    "--crf",
                    "35",
                    "-v",
                ]
            )

            assert "-c copy" in stderr
            assert "-crf" not in stderr
        finally:
            shutil.rmtree("tmp")

    @pytest.mark.parametrize("crf", ["-1", "52", "abc"])
    def test_invalid_crf_cli(self, crf):
        """
        Test that the CLI rejects CRF values outside 0-51.
        """
        with pytest.raises(RuntimeError, match="CRF"):
            run_command(
                [
                    "python3",
                    "-m",
                    "scenecut_extractor",
                    TEST_FILE,
                    "-x",
                    "--no-copy",
                    "--crf",
                    crf,
                ]
            )


class TestApi:
    def test_duration(self):
        """
        Test that the duration is calculated from the frame timestamps.
        """
        se = ScenecutExtractor(TEST_FILE)
        se.calculate_scenecuts()
        assert se.duration == TEST_FILE_DURATION

    def test_extract_scenes_includes_first_and_last_scene(self, tmp_path):
        """
        Test that N scene cuts give N+1 files, from the start to the end of the video.
        """
        se = ScenecutExtractor(TEST_FILE)
        se.calculate_scenecuts()
        scenecuts = se.get_scenecuts()
        se.extract_scenes(str(tmp_path), no_copy=True, preset="ultrafast")

        output_files = sorted(tmp_path.iterdir())
        assert len(output_files) == len(scenecuts) + 1
        assert output_files[0].name == "test_0.000-0.960.mp4"
        assert output_files[-1].name == "test_6.960-7.960.mp4"

        # first scene: frames 0-23; last scene: frames 174-198
        assert count_frames(str(output_files[0])) == scenecuts[0]["frame"]
        assert (
            count_frames(str(output_files[-1]))
            == TEST_FILE_FRAMES - scenecuts[-1]["frame"]
        )
        assert sum(count_frames(str(f)) for f in output_files) == TEST_FILE_FRAMES

    def test_extract_scenes_without_scenecuts(self, tmp_path):
        """
        Test that a video without scene cuts gives one file with the whole video.
        """
        se = ScenecutExtractor(TEST_FILE)
        se.calculate_scenecuts()
        se.scenecuts = []
        se.extract_scenes(str(tmp_path), no_copy=True, preset="ultrafast")

        output_files = list(tmp_path.iterdir())
        assert [f.name for f in output_files] == ["test_0.000-7.960.mp4"]
        assert count_frames(str(output_files[0])) == TEST_FILE_FRAMES

    def test_extract_scenes_with_scenecut_at_start(self, tmp_path):
        """
        Test that a scene cut at the start of the video does not give an empty scene.
        """
        se = ScenecutExtractor(TEST_FILE)
        se.calculate_scenecuts(threshold=0)
        se.scenecuts = [s for s in se.get_scenecuts() if s["pts_time"] in (0, 0.96)]
        se.extract_scenes(str(tmp_path), no_copy=True, preset="ultrafast")

        assert sorted(f.name for f in tmp_path.iterdir()) == [
            "test_0.000-0.960.mp4",
            "test_0.960-7.960.mp4",
        ]

    def test_invalid_crf_api(self, tmp_path):
        """
        Test that the API rejects CRF values outside 0-51.
        """
        se = ScenecutExtractor(TEST_FILE)
        se.calculate_scenecuts()
        for crf in [-1, 52]:
            with pytest.raises(RuntimeError, match="CRF must be between 0 and 51"):
                se.extract_scenes(str(tmp_path), no_copy=True, crf=crf)
        assert not any(tmp_path.iterdir())

    def test_invalid_preset_api(self, tmp_path):
        """
        Test that the API rejects unknown presets.
        """
        se = ScenecutExtractor(TEST_FILE)
        se.calculate_scenecuts()
        with pytest.raises(RuntimeError, match="Invalid preset"):
            se.extract_scenes(str(tmp_path), no_copy=True, preset="fastest")

    def test_extract_scenes_with_crf_api(self, tmp_path):
        """
        Test that the output files are encoded with the given CRF value.
        libx264 writes its settings (e.g. "crf=30.0") into the bitstream.
        """
        se = ScenecutExtractor(TEST_FILE)
        se.calculate_scenecuts()
        se.extract_scenes(str(tmp_path), no_copy=True, crf=30, preset="ultrafast")

        output_files = list(tmp_path.iterdir())
        assert len(output_files) == len(se.get_scenecuts()) + 1
        for output_file in output_files:
            assert b"crf=30.0" in output_file.read_bytes()

    def test_extract_scenes_default_crf_api(self, tmp_path):
        """
        Test that the default CRF value is 23.
        """
        se = ScenecutExtractor(TEST_FILE)
        se.calculate_scenecuts()
        se.extract_scenes(str(tmp_path), no_copy=True)

        for output_file in tmp_path.iterdir():
            assert b"crf=23.0" in output_file.read_bytes()
