"""Turn a photo into a glowing, multi-color laser-style line drawing."""

import argparse

import cv2
import numpy as np


def _to_neon(bgr):
    """Boost a BGR color to full saturation and brightness."""
    hsv = cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2HSV)[0][0].astype(np.int32)
    hsv[1] = 255
    hsv[2] = 255
    return cv2.cvtColor(np.uint8([[hsv]]), cv2.COLOR_HSV2BGR)[0][0]


def create_laser_art(
    input_path,
    output_path,
    num_colors=8,
    low_thresh=40,
    high_thresh=130,
    glow_strength=10,
    line_thickness=1,
    background="black",
    max_dim=1400,
):
    """Convert an image into neon colored edges with a soft laser glow."""
    if num_colors < 2:
        raise ValueError("num_colors must be at least 2")
    if line_thickness < 1:
        raise ValueError("line_thickness must be at least 1")
    if glow_strength < 0:
        raise ValueError("glow_strength cannot be negative")

    img = cv2.imread(input_path)
    if img is None:
        raise FileNotFoundError(f"Could not load image: {input_path}")

    height, width = img.shape[:2]
    scale = min(1.0, max_dim / max(height, width))
    if scale < 1.0:
        img = cv2.resize(
            img,
            (int(width * scale), int(height * scale)),
            interpolation=cv2.INTER_AREA,
        )

    smooth = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)

    pixels = smooth.reshape((-1, 3)).astype(np.float32)
    criteria = (
        cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
        20,
        1.0,
    )
    _, labels, centers = cv2.kmeans(
        pixels,
        num_colors,
        None,
        criteria,
        attempts=6,
        flags=cv2.KMEANS_PP_CENTERS,
    )
    labels = labels.reshape(smooth.shape[:2])
    neon_palette = np.array(
        [_to_neon(center.astype(np.uint8)) for center in centers],
        dtype=np.uint8,
    )

    gray = cv2.cvtColor(smooth, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, low_thresh, high_thresh)

    if line_thickness > 1:
        kernel = np.ones((line_thickness, line_thickness), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)

    color_map = neon_palette[labels.reshape(-1)].reshape(img.shape)
    canvas = np.zeros_like(img)
    edge_mask = edges > 0
    canvas[edge_mask] = color_map[edge_mask]

    glow_small = cv2.GaussianBlur(
        canvas, (0, 0), sigmaX=glow_strength, sigmaY=glow_strength
    )
    glow_large = cv2.GaussianBlur(
        canvas,
        (0, 0),
        sigmaX=glow_strength * 2.5,
        sigmaY=glow_strength * 2.5,
    )

    result = canvas.astype(np.float32)
    result += glow_small.astype(np.float32) * 0.9
    result += glow_large.astype(np.float32) * 0.5
    result = np.clip(result, 0, 255).astype(np.uint8)

    if background == "dim":
        dim_background = (img.astype(np.float32) * 0.15).astype(np.uint8)
        result = cv2.add(dim_background, result)

    if not cv2.imwrite(output_path, result):
        raise OSError(f"Could not save output image: {output_path}")
    return result


def _parse_args():
    parser = argparse.ArgumentParser(
        description="Convert a photo into laser-style line art."
    )
    parser.add_argument("input", help="Path to the input image (png/jpg)")
    parser.add_argument("output", help="Path to save the output image")
    parser.add_argument("--colors", type=int, default=8)
    parser.add_argument("--low", type=int, default=40)
    parser.add_argument("--high", type=int, default=130)
    parser.add_argument("--glow", type=float, default=10)
    parser.add_argument("--thick", type=int, default=1)
    parser.add_argument("--bg", choices=["black", "dim"], default="black")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    create_laser_art(
        args.input,
        args.output,
        num_colors=args.colors,
        low_thresh=args.low,
        high_thresh=args.high,
        glow_strength=args.glow,
        line_thickness=args.thick,
        background=args.bg,
    )
    print(f"Saved: {args.output}")
