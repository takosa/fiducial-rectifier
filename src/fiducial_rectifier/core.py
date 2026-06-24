import numpy as np

import cv2
from PIL import Image, ImageDraw
from pathlib import Path

MM_PER_INCH = 25.4
DPI = 300
LINE_WIDTH_MM = .5

def make_template_pdf(
    marker_type: str,
    width_mm: float,
    height_mm: float,
    marker_size_mm: float,
    padding_mm: float,
    margin_mm: float,
) -> Image.Image:
    """
    Generate a PDF template with fiducial markers.

    Parameters:
    - output: The filename for the generated PDF.
    - page_size: The size of the PDF page (e.g., "A4", "Letter").
    - marker_type: The type of fiducial marker to use (e.g., "aruco").
    - marker_ids: A list of marker IDs to include in the template.

    Returns:
    - Image.Image: The generated template as a PIL Image object.
    """

    
    margin_px = round(margin_mm / MM_PER_INCH * DPI)
    padding_px = round(padding_mm / MM_PER_INCH * DPI)
    marker_size_px = round(marker_size_mm / MM_PER_INCH * DPI)
    width_px = round(width_mm / MM_PER_INCH * DPI)
    height_px = round(height_mm / MM_PER_INCH * DPI)
    line_width_px = round(LINE_WIDTH_MM / MM_PER_INCH * DPI)
    line_half_width_px = round(line_width_px / 2)

    if marker_type == "aruco":
        n_markers = 8
        marker_size = 4
        marker_dict = cv2.aruco.extendDictionary(nMarkers=n_markers, markerSize=marker_size)
        markers = [cv2.aruco.generateImageMarker(dictionary=marker_dict, id=i, sidePixels=marker_size_px) for i in range(n_markers)]
    else:
        raise ValueError(f"Unsupported marker type: {marker_type}")
    
    fig_width_px = width_px + 2 * (margin_px + marker_size_px + padding_px)
    fig_height_px = height_px + 2 * (margin_px + marker_size_px + padding_px)
    out_img = Image.new("RGB", (fig_width_px, fig_height_px), "white")

    # paste markers from top-left, top-center, top-right, middle-left, middle-center, ...
    top_y = margin_px
    left_x = margin_px
    right_x =  margin_px + marker_size_px + padding_px + width_px + padding_px
    bottom_y = margin_px + marker_size_px + padding_px + height_px + padding_px
    center_x = round(margin_px + marker_size_px + padding_px + (width_px - marker_size_px) / 2)
    middle_y = round(margin_px + marker_size_px + padding_px + (height_px - marker_size_px) / 2)
    positions = [
        (left_x, top_y), # top-left
        (right_x, top_y), # top-right
        (right_x, bottom_y), # bottom-right
        (left_x, bottom_y), # bottom-left
        (center_x, top_y), # top-center
        (right_x, middle_y), # middle-right
        (center_x, bottom_y), # bottom-center
        (left_x, middle_y), # middle-left
    ]
    for pos, marker in zip(positions, markers):
        marker_image = Image.fromarray(marker)
        out_img.paste(marker_image, pos)

    draw = ImageDraw.Draw(out_img)
    inner_base = margin_px + marker_size_px + padding_px + line_half_width_px
    draw.rectangle(
        (inner_base, inner_base, inner_base + width_px - line_width_px, inner_base + height_px - line_width_px),
        outline=(128, 128, 128),
        width=line_width_px,
    )

    
    draw.text(
        (inner_base + width_px / 4, inner_base),
        f"{width_mm} mm x {height_mm} mm (m: {marker_size_mm} mm, p: {padding_mm} mm)",
        fill=(128, 128, 128),
        anchor="mb",
        font_size=marker_size_px // 3
    )


    pdf_width_mm = width_mm + 2 * (marker_size_mm + padding_mm + margin_mm)
    pdf_height_mm = height_mm + 2 * (marker_size_mm + padding_mm + margin_mm)
    print(f"PDF size: {pdf_width_mm} mm x {pdf_height_mm} mm, Marker size: {marker_size_mm} mm, Padding: {padding_mm} mm Margin: {margin_mm} mm")

    return out_img


def rectify_image(
    input_image: numpy.ndarray,
    marker_type: str,
    width_mm: float,
    height_mm: float,
    marker_size_mm: float,
    padding_mm: float,
    output_px_per_mm: float,
    include_markers: bool,
    include_padding: bool,
) -> Image.Image:
    """
    Rectify an image using detected fiducial markers.

    Parameters:
    - input_image: The input image to rectify as a numpy array.
    - marker_type: The type of fiducial marker to detect (e.g., "aruco").
    - width_mm: The width of the output image in millimeters.
    - height_mm: The height of the output image in millimeters.
    - marker_size_mm: The size of the fiducial markers in millimeters.
    - padding_mm: The padding around the markers in millimeters.
    - output_px_per_mm: The output resolution in pixels per millimeter.
    - include_markers: Whether to include markers in the output image.
    - include_padding: Whether to include padding in the output image.

    Returns:
    - Image.Image: The rectified image as a PIL Image object.
    """

    if marker_type == "aruco":
        marker_dict = cv2.aruco.extendDictionary(nMarkers=8, markerSize=4)
        params = cv2.aruco.DetectorParameters()
        detector = cv2.aruco.ArucoDetector(marker_dict, params)
    else:
        raise ValueError(f"Unsupported marker type: {marker_type}")

    
    # Detect markers in the image
    corners, ids, rejected = detector.detectMarkers(input_image)

    if ids is None or len(ids) < 4:
        raise ValueError("Not enough markers detected. At least 4 markers are required for rectification.")
    
    sorted_indices = np.argsort(ids.flatten())
    corners = [corners[i] for i in sorted_indices]
    ids = ids[sorted_indices]

    padding_px = round(padding_mm * output_px_per_mm)
    width_px = round(width_mm * output_px_per_mm)
    height_px = round(height_mm * output_px_per_mm)
    marker_size_px = round(marker_size_mm * output_px_per_mm)
    
    left_x_mm = marker_size_mm / 2
    top_y_mm = marker_size_mm / 2
    right_x_mm = marker_size_mm + padding_mm + width_mm + padding_mm + marker_size_mm / 2
    bottom_y_mm = marker_size_mm + padding_mm + height_mm + padding_mm + marker_size_mm / 2
    center_x_mm = marker_size_mm + padding_mm + width_mm / 2
    middle_x_mm = marker_size_mm + padding_mm + height_mm / 2

    positions_mm = {
        0: (left_x_mm, top_y_mm), # top-left
        1: (right_x_mm, top_y_mm), # top-right
        2: (right_x_mm, bottom_y_mm), # bottom-right
        3: (left_x_mm, bottom_y_mm), # bottom-left
        4: (center_x_mm, top_y_mm), # top-center
        5: (right_x_mm, middle_x_mm), # middle-right
        6: (center_x_mm, bottom_y_mm), # bottom-center
        7: (left_x_mm, middle_x_mm), # middle-left
    }

    positions_mm_aligned = np.array([positions_mm[i] for i in ids.ravel()], dtype=np.float32)
    positions_px = positions_mm_aligned * output_px_per_mm
    corners_mean = np.array([corner.mean(axis=(0, 1)) for corner in corners], dtype=np.float32)

    if include_markers:
        output_width_px = width_px + 2 * (marker_size_px + padding_px)
        output_height_px = height_px + 2 * (marker_size_px + padding_px)
    elif include_padding:
        positions_px -= marker_size_px
        output_width_px = width_px + 2 * padding_px
        output_height_px = height_px + 2 * padding_px
    else:
        positions_px -= marker_size_px + padding_px
        output_width_px = width_px
        output_height_px = height_px
    
    if output_width_px > 5000 or output_height_px > 5000:
        raise ValueError(f"Output image size is too large: {output_width_px}px x {output_height_px}px. Please reduce the output size or increase the output_px_per_mm.")
    
    M, mask = cv2.findHomography(corners_mean, positions_px, method=cv2.RANSAC)
    rectified_img = cv2.warpPerspective(input_image, M, (int(output_width_px), int(output_height_px)))

    print(f"Output image size: {output_width_px}px x {output_height_px}px")

    return Image.fromarray(cv2.cvtColor(rectified_img, cv2.COLOR_BGR2RGB))


    
