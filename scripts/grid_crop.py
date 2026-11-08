"""Crop part of a scene image, enlarge it and draw a 0.02 grid labelled in image fractions.

Use it to read off a character's mouth position (x, y as fractions of the whole image)
for the MOUTHS table in the animation HTML.

    python grid_crop.py images/scene4.jpg 0.3 0.1 0.7 0.6 out.jpg
                        <image>          x0  y0  x1  y1  <output>
"""
import sys
from PIL import Image, ImageDraw


def main():
    if len(sys.argv) != 7:
        sys.exit(__doc__)
    src, x0, y0, x1, y1, out = sys.argv[1], *map(float, sys.argv[2:6]), sys.argv[6]
    im = Image.open(src).convert("RGB")
    W, H = im.size
    c = im.crop((int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H)))
    c = c.resize((c.width * 2, c.height * 2))
    d = ImageDraw.Draw(c)
    step = 0.02
    k = round(x0 / step)
    while k * step <= x1 + 1e-9:
        fx = k * step
        if fx >= x0:
            X = (fx - x0) / (x1 - x0) * c.width
            major = k % 5 == 0
            d.line([(X, 0), (X, c.height)], fill=(0, 255, 0) if major else (0, 120, 0))
            if major:
                d.text((X + 2, 2), f"{fx:.2f}", fill=(255, 255, 0))
        k += 1
    k = round(y0 / step)
    while k * step <= y1 + 1e-9:
        fy = k * step
        if fy >= y0:
            Y = (fy - y0) / (y1 - y0) * c.height
            major = k % 5 == 0
            d.line([(0, Y), (c.width, Y)], fill=(0, 255, 0) if major else (0, 120, 0))
            if major:
                d.text((2, Y + 2), f"{fy:.2f}", fill=(255, 255, 0))
        k += 1
    c.save(out)
    print(out)


if __name__ == "__main__":
    main()
