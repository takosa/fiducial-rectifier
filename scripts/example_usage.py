from fiducial_rectifier import rectify_image
import cv2
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt 

PX_PER_MM = 5

def process_image(input_path):
    input_img = cv2.imread(str(input_path), cv2.IMREAD_IGNORE_ORIENTATION+cv2.IMREAD_COLOR)
    img = rectify_image(
        input_image=input_img,
        marker_type='aruco',
        width_mm=234,
        height_mm=168,
        marker_size_mm=10,
        padding_mm=5,
        output_px_per_mm=PX_PER_MM,
        include_markers=False,
        include_padding=True,
    )

    img = np.array(img)
    img = cv2.GaussianBlur(img, (5, 5), 10)
    _, a, _ = cv2.split(cv2.cvtColor(img, cv2.COLOR_RGB2Lab))
    _, mask = cv2.threshold(a, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    
    for contour in contours:
        area_px = cv2.contourArea(contour)
        if area_px < 1000 or area_px > 100000:
            continue
        ellipse = cv2.fitEllipse(contour)
        (x, y), (minor, major), angle = ellipse
        if abs(major - minor) > 10:
            continue
        cv2.ellipse(
            img,
            (int(x), int(y)),
            (int(minor // 2), int(major // 2)),
            angle,
            0,
            360,
            (0, 255, 0),
            3
        )
        radius_px = (minor + major) / 2 / 2
    
        area_mm = area_px / PX_PER_MM / PX_PER_MM
        radius_mm = radius_px / PX_PER_MM
    
        cv2.putText(img, f"{radius_mm:.2f} mm", (int(x), int(y)+10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
        print(f"Area: {area_mm} mm^2, Radius: {radius_mm} mm")
    
    input_path = Path(input_path)
    output_path = input_path.parent / (input_path.stem + '_rectified.jpg')
    return img


import sys
args = sys.argv

if len(args) <= 1:
    print("Please specify some files.", file=sys.stderr)
    sys.exit(1)

fig, axes = plt.subplots(len(args) - 1, 2, figsize=(10, 4 * (len(args) - 1)), squeeze=False)
for arg, ax1, ax2 in zip(args[1:], axes[:, 0], axes[:, 1]):
    input_path = Path(arg)
    if not input_path.exists():
        continue
    if not input_path.suffix.lower() in ['.png', '.jpg', '.jpeg',]:
        continue
    img_in = cv2.imread(str(input_path), cv2.IMREAD_IGNORE_ORIENTATION+cv2.IMREAD_COLOR)
    img_in = cv2.cvtColor(img_in, cv2.COLOR_BGR2RGB)
    img_out = process_image(input_path)
    ax1.imshow(img_in)
    ax1.set_title(f"Input: {input_path.name}")
    ax1.axis('off')
    ax2.axis('off')
    ax2.imshow(img_out)
    ax2.set_title(f"Output: {input_path.stem}_rectified.jpg")

plt.savefig("output.png", bbox_inches='tight')
