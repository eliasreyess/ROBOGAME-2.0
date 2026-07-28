#!/usr/bin/env python3
"""
Set UVC camera controls using v4l2-ctl.

Requires: v4l-utils installed (`sudo apt install v4l-utils`)
Usage:
    python3 set_camera_settings.py                 # uses /dev/video0
    python3 set_camera_settings.py --device /dev/video2
"""

import argparse
import subprocess
import sys

# Controls to set: v4l2-ctl control name -> desired value
CONTROLS = {
    "brightness": 0,
    "contrast": 32,
    "saturation": 64,
    "hue": 0,
    "white_balance_automatic": 1,
    "gamma": 100,
    "gain": 0,
    "power_line_frequency": 2,      # 2 = 60 Hz
    "sharpness": 3,
    "backlight_compensation": 1,
    "auto_exposure": 3,             # 3 = Aperture Priority Mode
    "exposure_dynamic_framerate": 0,
    "pan_absolute": 0,
    "tilt_absolute": 0,
    "zoom_absolute": 0,
}

# Format / resolution / framerate settings
VIDEO_FORMAT = {
    "width": 800,
    "height": 600,
    "pixelformat": "YUYV",
}
FPS = 15


def run(cmd):
    """Run a command, print it, and return (success, output)."""
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  -> FAILED: {result.stderr.strip()}", file=sys.stderr)
        return False, result.stderr
    if result.stdout.strip():
        print(f"  -> {result.stdout.strip()}")
    return True, result.stdout


def set_controls(device, controls):
    # v4l2-ctl can take a comma-separated list of ctrl=value pairs in one call
    ctrl_str = ",".join(f"{name}={value}" for name, value in controls.items())
    run(["v4l2-ctl", "-d", device, "--set-ctrl", ctrl_str])


def set_format(device, fmt, fps):
    run([
        "v4l2-ctl", "-d", device,
        "--set-fmt-video",
        f"width={fmt['width']},height={fmt['height']},pixelformat={fmt['pixelformat']}",
    ])
    run(["v4l2-ctl", "-d", device, "--set-parm", str(fps)])


def show_current(device):
    run(["v4l2-ctl", "-d", device, "--all"])


def main():
    parser = argparse.ArgumentParser(description="Apply UVC camera control settings.")
    parser.add_argument("--device", default="/dev/video0", help="Video device (default: /dev/video0)")
    parser.add_argument("--skip-format", action="store_true", help="Only set controls, skip resolution/fps")
    parser.add_argument("--show", action="store_true", help="Print full control listing before/after")
    args = parser.parse_args()

    if args.show:
        show_current(args.device)

    set_controls(args.device, CONTROLS)

    if not args.skip_format:
        set_format(args.device, VIDEO_FORMAT, FPS)

    if args.show:
        show_current(args.device)


if __name__ == "__main__":
    main()