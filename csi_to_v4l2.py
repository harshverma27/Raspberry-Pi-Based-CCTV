import subprocess
import signal
import sys

WIDTH =  640
HEIGHT =  480
FPS = 30
DEVICE = "/dev/video40" #
"""
This dummy device must be a empty device created with v4l2loopback, e.g.:
sudo modprobe v4l2loopback devices=1 video_nr=40 card_label
Point to be taken care of, For Pi-4 and Pi-5, the /dev/video1 is not empty hence we used /dev/video40, But for Pi-0 /dev/video1 is empty."""

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
