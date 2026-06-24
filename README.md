# fiducial-rectifier

Rectify perspective-distorted photos using printed ArUco markers for accurate mm-scale measurement. Currently, only ArUco is supported, but support for additional fiducial markers is planned.

## Overview

This tool corrects geometric distortion in photos using ArUco fiducial markers as reference points. By placing a printed template around your subject and photographing it from any angle, you get a rectified image with accurate real-world scale (mm).

```
[Photo with markers] → [Marker detection] → [Homography transform] → [Rectified image]
```

## Workflow

1. **Generate and print a template**  
   Specify the size of your target area to generate a PDF. Print it and place it around your subject.

2. **Photograph your subject**  
   Angle and handheld shots are fine.

3. **Rectify the image**  
   Pass the photo to the tool — it detects the markers, applies a homography transform, and outputs a corrected image at the specified scale.

## Installation

```bash
pip install uv
uv sync
```

## Usage

### CLI

**Generate a template PDF**

```bash
fiducial-rectifier template output.pdf \
  --width-mm 234 \
  --height-mm 168 \
  --marker-size-mm 10 \
  --padding-mm 5
```

**Rectify an image**

```bash
fiducial-rectifier rectify input.jpg -o output.jpg \
  --width-mm 234 \
  --height-mm 168 \
  --marker-size-mm 10 \
  --padding-mm 5 \
  --output-px-per-mm 5
```

Add `--include-markers` or `--include-padding` to include those regions in the output image.

### Python API

```python
from fiducial_rectifier import make_template_pdf, rectify_image
from pathlib import Path

# Generate template
img = make_template_pdf(
    marker_type="aruco",
    width_mm=234,
    height_mm=168,
    marker_size_mm=10,
    padding_mm=5,
    margin_mm=3,
)
img.save("template.pdf", format="PDF", resolution=300)

# Rectify image
rectified = rectify_image(
    input_image_path=Path("input.jpg"),
    marker_type="aruco",
    width_mm=234,
    height_mm=168,
    marker_size_mm=10,
    padding_mm=5,
    output_px_per_mm=5,
    include_markers=False,
    include_padding=False,
)
rectified.save("output.jpg")
```

## Parameters

| Parameter | Description |
|---|---|
| `width_mm` / `height_mm` | Width and height of the target area (mm) |
| `marker_size_mm` | Side length of each ArUco marker (mm) |
| `padding_mm` | Gap between markers and the target area (mm) |
| `margin_mm` | Outer margin of the template (mm) — template generation only |
| `output_px_per_mm` | Output image resolution (px/mm) |
