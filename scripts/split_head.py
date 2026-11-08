"""Split a cutout character PNG into a head layer and a body layer (same canvas size, so they stack exactly).

    python split_head.py in.png neck_y [bx0 bx1 by1 [hx0 hx1]]
neck_y: fraction of height where the head ends (chin / collar line).
bx0 bx1 by1: optional beard box (x range, down to y); its light-coloured pixels also go to the head,
             so a long white beard moves with the head instead of tearing.
hx0 hx1: optional x range for the head, to keep a raised hand that sits above the neck line on the body.
Skip head-splitting for poses where a hand touches the head (scratching, cheering above the head).
Writes <name>_head.png and <name>_body.png. The head keeps a 2% band below the neck so a small
rotation never opens a gap; the body loses everything above the neck.
"""
import sys, os
import numpy as np
from PIL import Image, ImageFilter

src = sys.argv[1]; neck = float(sys.argv[2])
beard = tuple(map(float, sys.argv[3:6])) if len(sys.argv) >= 6 else None
hx = tuple(map(float, sys.argv[6:8])) if len(sys.argv) >= 8 else (0, 1)   # head x-range
im = Image.open(src).convert('RGBA'); W, H = im.size
a = np.asarray(im).astype(float)
yy, xx = np.mgrid[0:H, 0:W]
head = (yy < (neck + .02) * H) & (xx >= hx[0] * W) & (xx <= hx[1] * W)
if beard:
    x0, x1, y1 = beard
    rgb = a[..., :3]
    light = (rgb.min(axis=2) > 165) & ((rgb.max(axis=2) - rgb.min(axis=2)) < 45)
    head |= (xx >= x0 * W) & (xx <= x1 * W) & (yy < y1 * H) & light
headm = Image.fromarray((head * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.5))
bodym = Image.fromarray(((~head | ((yy >= neck * H) & (yy < (neck + .02) * H))) * 255).astype('uint8'))
alpha = im.getchannel('A')
base, _ = os.path.splitext(src)
for name, m in (('head', headm), ('body', bodym)):
    out = im.copy()
    out.putalpha(Image.fromarray(np.minimum(np.asarray(alpha), np.asarray(m)).astype('uint8')))
    out.save(f'{base}_{name}.png')
print(base, W, H)
