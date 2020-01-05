from app.cleanup import cleanup
import app.video

cleanup()
video.convert(
    file = "input.mp4",
    output = "output.mkv",
    start = "00:10:00",
    end = "00:14:00"
)
