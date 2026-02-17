import subprocess
import signal
import sys

WIDTH = 1280
HEIGHT = 720
FPS = 25
DEVICE = "/dev/video40"

cmd = [
    "rpicam-vid",
    "--inline",
    "--timeout", "0",
    "--width", str(WIDTH),
    "--height", str(HEIGHT),
    "--framerate", str(FPS),
    "--codec", "yuv420",
    "-o", "-"
]

ffmpeg_cmd = [
    "ffmpeg",
    "-loglevel", "error",
    "-f", "rawvideo",
    "-pix_fmt", "yuv420p",
    "-s", f"{WIDTH}x{HEIGHT}",
    "-r", str(FPS),
    "-i", "-",
    "-f", "v4l2",
    DEVICE
]

rpicam = subprocess.Popen(cmd, stdout=subprocess.PIPE)
ffmpeg = subprocess.Popen(ffmpeg_cmd, stdin=rpicam.stdout)

def cleanup(sig, frame):
    rpicam.terminate()
    ffmpeg.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

rpicam.wait()
