# Scenecut Extractor

Extract scenecuts from video files using ffmpeg.

Author: Werner Robitza <werner.robitza@gmail.com>

# Requirements

- Python 2.7 or 3.x
- FFmpeg:
    - download a static build from [their website](http://ffmpeg.org/download.html))
    - put the `ffmpeg` executable in your `$PATH`

# Installation

    pip install scenecut_extractor

Or clone this repository, then run the tool with `python -m scenecut_extractor`.

# Usage

Run:

    scenecut_extractor <input-file>

This will output a list of scene cuts in JSON format:

```json
[
  {
    "frame": 114,
    "pts": 114.0,
    "pts_time": 3.8,
    "score": 0.445904
  },
  {
    "frame": 159,
    "pts": 159.0,
    "pts_time": 5.3,
    "score": 0.440126
  }
]
```

You can use the `-t` parameter to set the threshhold that ffmpeg internally uses (between 0 and 1).

Or `scenecut_extractor -h` to find more options.

# License

bufferer, Copyright (c) 2017 Werner Robitza

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.