#!/usr/bin/env python3

from cleanup import cleanup
import video

cleanup()
video.convert(
    file = "input.mp4",
    output = "output.mkv",
    start = "00:10:00",
    end = "00:14:00"
)
