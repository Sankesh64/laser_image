# Ganesha Laser Art

This project turns a photo into a glowing, multi-color laser-style line drawing using OpenCV.

## Project structure

```text
ganesha_laser_project/
├── laser_image.py
├── requirements.txt
├── input/
│   └── ganesha.png
└── output/
```

Place the source image at `input/ganesha.png`.

## How it works

1. Smooths the photo with a bilateral filter.
2. Uses K-means to divide the image into color regions.
3. Detects edges with Canny.
4. Assigns each edge the neon version of its region color.
5. Adds two levels of Gaussian glow.
6. Renders the result on a black or dimmed background.

## Install

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

```powershell
python laser_image.py input/ganesha.png output/laser_art.png
```

With custom settings:

```powershell
python laser_image.py input/ganesha.png output/laser_art.png --colors 10 --glow 12 --bg dim
```

### Options

- `--colors`: Number of K-means color regions. Default: `8`.
- `--low`: Canny low threshold. Default: `40`.
- `--high`: Canny high threshold. Default: `130`.
- `--glow`: Glow blur strength. Default: `10`.
- `--thick`: Edge line thickness. Default: `1`.
- `--bg`: `black` or `dim`. Default: `black`.

The output is a regular PNG image suitable for previewing the laser-art effect. This project does not directly control laser hardware.
