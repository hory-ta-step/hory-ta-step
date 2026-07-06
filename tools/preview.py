# -*- coding: utf-8 -*-
"""Рендер зразків: fonts/*.ttf -> docs/preview-<назва>.png"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / 'fonts'
DOCS = ROOT / 'docs'

LINES = [
    "Реве та стогне Дніпр широкий,",
    "сердитий вітер завива.",
    "М'яч, джміль, дзвін, щастя, її мрія!",
]
BG, INK, CAPTION = '#1B2A23', '#D3AE62', '#93A98F'


def main():
    DOCS.mkdir(exist_ok=True)
    ttfs = sorted(FONTS.glob('*.ttf'))
    if not ttfs:
        raise SystemExit('Спершу зберіть шрифти: make build')
    for ttf in ttfs:
        font = ImageFont.truetype(str(ttf), 64)
        cap = ImageFont.load_default(24)
        img = Image.new('RGB', (1280, 60 + 170 * len(LINES)), BG)
        d = ImageDraw.Draw(img)
        y = 40
        for ln in LINES:
            d.text((50, y), ln, font=font, fill=INK)
            d.text((50, y + 108), ln, font=cap, fill=CAPTION)
            y += 170
        out = DOCS / f'preview-{ttf.stem}.png'
        img.save(out)
        print(f'  ✓ {out.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
