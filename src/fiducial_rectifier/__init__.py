import cv2

from .core import make_template_pdf, rectify_image

__all__ = ["make_template_pdf", "rectify_image"]


import typer
from typing import Annotated
from pathlib import Path
from .core import make_template_pdf, rectify_image, DPI

# Defaoult values for the CLI options
MARKER_TYPE_DEFAULT = "aruco"
WIDTH_MM_DEFAULT = 234
HEIGHT_MM_DEFAULT = 168
MARKER_SIZE_MM_DEFAULT = 10
PADDING_MM_DEFAULT = 5
MARGIN_MM_DEFAULT = 3
OUTPUT_PX_PER_MM_DEFAULT = 5


app = typer.Typer()
@app.command()
def template(
    output_path: Annotated[Path, typer.Argument(help="Output PDF file path")],
    marker_type: Annotated[
        str,
        typer.Option(help="Type of fiducial marker"),
    ] = MARKER_TYPE_DEFAULT,
    width_mm: Annotated[
        float,
        typer.Option(help="Width of the output image in millimeters"),
    ] = WIDTH_MM_DEFAULT,
    height_mm: Annotated[
        float,
        typer.Option(help="Height of the output image in millimeters")
    ] = HEIGHT_MM_DEFAULT,
    marker_size_mm: Annotated[
        float,
        typer.Option(help="Size of the fiducial markers in millimeters")
    ] = MARKER_SIZE_MM_DEFAULT,
    padding_mm: Annotated[
        float,
        typer.Option(help="Padding around the fiducial markers in millimeters")
    ] = PADDING_MM_DEFAULT,
    margin_mm: Annotated[
        float,
        typer.Option(help="Margin around the entire template in millimeters")
    ] = MARGIN_MM_DEFAULT,
) -> None:
    
    if output_path.suffix.lower() != ".pdf":
        raise ValueError("Output file must have a .pdf extension")
    
    img = make_template_pdf(
        marker_type=marker_type,
        width_mm = width_mm,
        height_mm = height_mm,
        marker_size_mm = marker_size_mm,
        padding_mm = padding_mm,
        margin_mm = margin_mm,
    )
    
    # img.save(Path(output_path).with_suffix(".png"), "PNG") # for debugging
    img.save(output_path, format="PDF", resolution=DPI)

@app.command()
def rectify(
    input_image_path: Annotated[Path, typer.Argument(help="Input image file path")],
    output_image_path: Annotated[
        Path,
        typer.Option(
            "--out",
            "-o",
            help="Output rectified image file path"
        ),
    ],
    marker_type: Annotated[
        str,
        typer.Option(help="Type of fiducial marker"),
    ] = MARKER_TYPE_DEFAULT,
    width_mm: Annotated[
        float,
        typer.Option(help="Width of the output image in millimeters"),
    ] = WIDTH_MM_DEFAULT,
    height_mm: Annotated[
        float,
        typer.Option(help="Height of the output image in millimeters")
    ] = HEIGHT_MM_DEFAULT,
    marker_size_mm: Annotated[
        float,
        typer.Option(help="Size of the fiducial markers in millimeters")
    ] = MARKER_SIZE_MM_DEFAULT,
    padding_mm: Annotated[
        float,
        typer.Option(help="Padding around the fiducial markers in millimeters")
    ] = PADDING_MM_DEFAULT,
    output_px_per_mm: Annotated[
        float,
        typer.Option(help="Output image resolution in pixels per millimeter")
    ] = OUTPUT_PX_PER_MM_DEFAULT,
    include_markers: Annotated[
        bool,
        typer.Option(help="Whether to include markers in the output image")
    ] = False,
    include_padding: Annotated[
        bool,
        typer.Option(help="Whether to include padding in the output image")
    ] = False,
) -> None:
    
    # Load the input image
    input_image = cv2.imread(str(input_image_path))
    if input_image is None:
        raise ValueError(f"Failed to read image: {input_image_path}")
    
    img = rectify_image(
        input_image=input_image,
        marker_type=marker_type,
        width_mm=width_mm,
        height_mm=height_mm,
        marker_size_mm=marker_size_mm,
        padding_mm=padding_mm,
        output_px_per_mm=output_px_per_mm,
        include_markers=include_markers,
        include_padding=include_padding,
    )

    print(f"Rectified image saved to {output_image_path}")
    img.save(output_image_path)


def main() -> None:
    app()