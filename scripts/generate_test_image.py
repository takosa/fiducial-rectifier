# 大きさ既知の円を印刷用PDFに描画するスクリプト。
# これを印刷して、マーカーの検出・rectify結果をもとにした大きさ推定の精度を確認するためのもの。

import cv2
from PIL import Image
import numpy as np

# 円の大きさ（mm）
CIRCLE_DIAMETER_MM = [10, 20, 30, 40, 50]

DPI = 300  # 印刷解像度（dots per inch）
MM_PER_INCH = 25.4  # 1インチあたりのミリ
PX_PER_MM = DPI / MM_PER_INCH # 画像の解像度（px/mm）

# 円の半径をピクセル単位で計算
circle_radius_px = [int((d / 2) * PX_PER_MM) for d in CIRCLE_DIAMETER_MM]

# 画像のサイズ（mm）
IMAGE_WIDTH_MM = 234
IMAGE_HEIGHT_MM = 168

# 画像のサイズをピクセル単位で計算
image_width_px = int(IMAGE_WIDTH_MM * PX_PER_MM)
image_height_px = int(IMAGE_HEIGHT_MM * PX_PER_MM)

# 白い背景の画像を作成
a = np.ones((image_height_px, image_width_px), dtype=np.uint8) * 255

# 円を描画
positions_mm = [
    (60, 40),
    (100, 40),
    (140, 40),
    (60, 100),
    (140, 100),
]
for pos, radius in zip(positions_mm, circle_radius_px):
    pos_px = (np.array(pos) * PX_PER_MM).astype(int)
    cv2.circle(a, pos_px, radius, (0,), thickness=-1)



l = np.ones((image_height_px, image_width_px), dtype=np.uint8) * 128
b = np.ones((image_height_px, image_width_px), dtype=np.uint8) * 128
image = cv2.cvtColor(cv2.merge([l, a, b,]), cv2.COLOR_LAB2RGB)

for pos, radius in zip(positions_mm, circle_radius_px):
    pos_px = (np.array(pos) * PX_PER_MM).astype(int)
    cv2.putText(
        image,
        f"{radius / PX_PER_MM:.1f}mm",
        (pos_px[0] - radius, pos_px[1] + radius + 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.5,
        (0, 0, 0,),
        3,
        cv2.LINE_AA,
    )
image = Image.fromarray(image)
image.save("test_circles.pdf", format="PDF", resolution=DPI)
image.save("test_circles.png", format="PNG")
