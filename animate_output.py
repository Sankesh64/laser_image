"""Play a laser-art PNG as a colored ANSI animation in the terminal."""

import math
import shutil
import sys
import time

import cv2
import numpy as np


RESET = "\033[0m"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
CLEAR_HOME = "\033[2J\033[H"


def load_rgb(path):
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Could not load image: {path}")
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def fit_to_terminal(rgb, margin_rows=2):
    """Downscale the image to fit the current terminal."""
    cols, rows = shutil.get_terminal_size(fallback=(100, 40))
    max_w = cols
    max_h = max(rows - margin_rows, 5) * 2

    height, width = rgb.shape[:2]
    scale = min(max_w / width, max_h / height, 1.0)
    new_width = max(2, int(width * scale))
    new_height = max(2, int(height * scale))
    new_height -= new_height % 2
    return cv2.resize(rgb, (new_width, new_height), interpolation=cv2.INTER_AREA)


def rows_to_ansi(rgb, brightness=1.0):
    """Convert RGB pixels into ANSI half-block strings."""
    if brightness != 1.0:
        rgb = np.clip(rgb.astype(np.float32) * brightness, 0, 255).astype(np.uint8)

    height, width = rgb.shape[:2]
    lines = []
    for y in range(0, height, 2):
        top, bottom = rgb[y], rgb[y + 1]
        chars = [
            f"\033[38;2;{top[x, 0]};{top[x, 1]};{top[x, 2]}m"
            f"\033[48;2;{bottom[x, 0]};{bottom[x, 1]};{bottom[x, 2]}m▀"
            for x in range(width)
        ]
        lines.append("".join(chars) + RESET)
    return lines


def play(path, reveal_seconds=1.2, pulse_cycles=3, pulse_seconds=0.6):
    rgb = fit_to_terminal(load_rgb(path))
    full_lines = rows_to_ansi(rgb)
    blank_line = " " * rgb.shape[1]
    line_count = len(full_lines)

    print(HIDE_CURSOR, end="")
    try:
        steps = max(line_count, 1)
        for index in range(1, steps + 1):
            frame = full_lines[:index] + [blank_line] * (line_count - index)
            print(CLEAR_HOME + "\n".join(frame), end="", flush=True)
            time.sleep(reveal_seconds / steps)

        pulse_steps = 24
        for _ in range(pulse_cycles):
            for step in range(pulse_steps):
                phase = step / pulse_steps
                brightness = 0.75 + 0.35 * (0.5 + 0.5 * math.sin(phase * 2 * math.pi))
                frame = rows_to_ansi(rgb, brightness=brightness)
                print(CLEAR_HOME + "\n".join(frame), end="", flush=True)
                time.sleep(pulse_seconds / pulse_steps)

        print(CLEAR_HOME + "\n".join(full_lines))
    finally:
        print(SHOW_CURSOR, end="", flush=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python animate_output.py <path-to-output-image>")
        sys.exit(1)
    play(sys.argv[1])