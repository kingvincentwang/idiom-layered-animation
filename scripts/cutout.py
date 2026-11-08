"""Remove a pure-white background by flood-filling near-white pixels connected to the image border,
then crop to the character. Output is a transparent PNG.

    python cutout.py <in.jpg> <out.png> [x0 x1] [--open-holes]

x0 x1         keep only this horizontal range of the source (fractions), e.g. 0 0.5 when Gemini drew a
              front view and a side view next to each other, or to split a sheet of several poses.
--open-holes  also make large enclosed pure-white areas transparent (the gap between an arm and the body).
              Do NOT use it for characters with large white beards or white clothes.
"""
import sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

src, out = sys.argv[1], sys.argv[2]
args=[a for a in sys.argv if not a.startswith('--')]
x0, x1 = (float(args[3]), float(args[4])) if len(args) > 4 else (0, 1)
im = Image.open(src).convert('RGB')
W, H = im.size
im = im.crop((int(x0 * W), 0, int(x1 * W), H))
a = np.asarray(im).astype(int)
white = (a.min(axis=2) > 232) & (a.max(axis=2) - a.min(axis=2) < 18)
lab, n = ndimage.label(white)
border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
bg = np.isin(lab, list(border))
fg = ~bg
fg = ndimage.binary_fill_holes(fg)          # keep enclosed white areas (eyes, beard) opaque
if '--open-holes' in sys.argv:              # but re-open big pure-white gaps (between arm and body)
    holes = fg & white
    hl, hn = ndimage.label(holes)
    if hn:
        hs = ndimage.sum(holes, hl, range(1, hn + 1))
        fg &= ~np.isin(hl, [i + 1 for i, v in enumerate(hs) if v > 1500])
# drop tiny specks
lab2, n2 = ndimage.label(fg)
if n2:
    sizes = ndimage.sum(fg, lab2, range(1, n2 + 1))
    keep = np.isin(lab2, [i + 1 for i, s in enumerate(sizes) if s > 2000])
    fg = keep
alpha = Image.fromarray((fg * 255).astype('uint8')).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1))
rgba = im.convert('RGBA')
rgba.putalpha(alpha)
bbox = alpha.getbbox()
rgba = rgba.crop(bbox)
rgba.save(out)
print(out, rgba.size)
