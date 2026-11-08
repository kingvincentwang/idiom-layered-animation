"""Draw every mouth of a layered animation onto its pose (or plate) image at closed / half / full opening,
and save one contact sheet, so mouth placement can be checked without playing the animation.

    python check_layer_mouths.py <成語>分層版.html out.jpg

Reads each `<div class="pose" data-pose=...>` and `<div class="plate">` block that contains a `.mouth`,
stacks the body image and head image (if any), and draws the template's mouth shape
(dark interior, upper teeth, tongue, soft lip-red rim, no black outline).
"""
import os
import re
import sys
from PIL import Image, ImageDraw


def quad(p0, p1, p2, n=20):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
            for t in (k / n for k in range(n + 1))]


SHAPE = quad((2, 6), (50, -3), (98, 6)) + quad((98, 6), (86, 60), (50, 60)) + quad((50, 60), (14, 60), (2, 6))


def blocks(html):
    """Yield (label, [image paths], mouth dict) for every pose/plate that has a mouth."""
    # cut the HTML at each pose/plate opening tag; each chunk runs to the next one
    starts = [m.start() for m in re.finditer(r'<div class="(?:pose[^"]*|plate)"', html)]
    starts.append(len(html))
    for a, b in zip(starts, starts[1:]):
        chunk = html[a:b]
        m = re.search(r'<div class="mouth"([^>]*)>', chunk)
        if not m:
            continue
        attrs = dict(re.findall(r'data-(\w+)="([\d.]+)"', m.group(1)))
        imgs = re.findall(r'<img src="([^"]+)"', chunk[:m.start()])
        name = re.search(r'data-pose="(\w+)"', chunk)
        actor = None
        before = html[:a]
        am = list(re.finditer(r'<div class="actor" id="(\w+)"', before))
        if am:
            actor = am[-1].group(1)
        label = 'plate' if chunk.startswith('<div class="plate"') else f'{actor}:{name.group(1) if name else "?"}'
        yield label, imgs, {k: float(v) for k, v in attrs.items()}


def render(paths, m, o, base):
    first = Image.open(os.path.join(base, paths[0]))
    im = Image.new('RGBA', first.size, (235, 225, 200, 255))
    for p in paths:
        layer = Image.open(os.path.join(base, p)).convert('RGBA')
        if layer.size != im.size:
            layer = layer.resize(im.size)
        im.alpha_composite(layer)
    im = im.convert('RGB')
    W, H = im.size
    x, y, w, h = m['x'], m['y'], m['w'], m['h']
    cw = max(w * 3.5, .2)                    # crop a bit more than the mouth, at least 20% of the width
    box = (int(max(0, x - cw / 2) * W), int(max(0, y - cw * .45 * W / H) * H),
           int(min(1, x + cw / 2) * W), int(min(1, y + cw * .35 * W / H) * H))
    S = 4
    c = im.crop(box).resize(((box[2] - box[0]) * S, (box[3] - box[1]) * S), Image.LANCZOS)
    if o:
        ox, oy = x * W - w * W / 2 - box[0], y * H - box[1]
        mw, mh = w * W, h * H * o
        pts = [((ox + px / 100 * mw) * S, (oy + py / 60 * mh) * S) for px, py in SHAPE]
        lay = Image.new('RGB', c.size, (58, 11, 8))
        d = ImageDraw.Draw(lay)
        d.rectangle([0, 0, c.width, (oy + 16 / 60 * mh) * S], fill=(243, 234, 216))
        d.ellipse([(ox + .24 * mw) * S, (oy + mh * 46 / 60) * S, (ox + .76 * mw) * S, (oy + mh * 66 / 60) * S], fill=(180, 75, 66))
        mask = Image.new('L', c.size, 0)
        ImageDraw.Draw(mask).polygon(pts, fill=255)
        c.paste(lay, (0, 0), mask)
        ImageDraw.Draw(c).line(pts, fill=(180, 87, 78), width=max(2, S // 2))
    return c.resize((240, max(1, int(240 * c.height / c.width))))


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    html_path, out = sys.argv[1], sys.argv[2]
    base = os.path.dirname(os.path.abspath(html_path))
    rows = list(blocks(open(html_path, encoding='utf-8').read()))
    if not rows:
        sys.exit('no mouths found')
    tiles = []
    for label, paths, m in rows:
        for o in (0, .5, 1):
            t = render(paths, m, o, base)
            ImageDraw.Draw(t).text((3, 3), f'{label} {o}', fill=(255, 255, 0))
            tiles.append(t)
    th = max(t.height for t in tiles)
    sheet = Image.new('RGB', (720, th * len(rows)), 'black')
    for n, t in enumerate(tiles):
        sheet.paste(t, ((n % 3) * 240, (n // 3) * th))
    sheet.save(out)
    print(out, len(rows), 'mouths')


if __name__ == '__main__':
    main()
