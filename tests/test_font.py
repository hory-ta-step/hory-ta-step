# -*- coding: utf-8 -*-
"""Smoke-тести зібраних шрифтів."""
from pathlib import Path

import pytest
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
TTFS = sorted((ROOT / 'fonts').glob('*.ttf'))

UKR = "абвгґдежзиійклмнопрстуфхцчшщьюяєї"


@pytest.fixture(params=TTFS, ids=[p.stem for p in TTFS])
def font(request):
    return TTFont(request.param)


def test_fonts_built():
    assert TTFS, 'fonts/*.ttf відсутні — запустіть make build'


def test_ukrainian_coverage(font):
    cmap = font.getBestCmap()
    missing = [ch for ch in UKR + UKR.upper() if ord(ch) not in cmap]
    assert not missing, f'Немає гліфів для: {missing}'


def test_punctuation_and_space(font):
    cmap = font.getBestCmap()
    for ch in " .,!?-:'’":
        assert ord(ch) in cmap, f'Немає гліфа для {ch!r}'


def test_ligatures_present(font):
    assert 'GSUB' in font, 'Відсутня таблиця GSUB'
    glyph_order = font.getGlyphOrder()
    assert 'dzhe' in glyph_order and 'dze' in glyph_order


def test_unicase(font):
    cmap = font.getBestCmap()
    for ch in UKR:
        assert cmap[ord(ch)] == cmap[ord(ch.upper())], \
            f'Велика і мала {ch} мають різні гліфи'


def test_outlines_nonempty(font):
    glyf = font['glyf']
    cmap = font.getBestCmap()
    for ch in UKR:
        g = glyf[cmap[ord(ch)]]
        assert g.numberOfContours > 0, f'Порожній контур для {ch}'


def test_metrics(font):
    hmtx = font['hmtx']
    cmap = font.getBestCmap()
    widths = {hmtx[cmap[ord(ch)]][0] for ch in UKR}
    assert all(w > 0 for w in widths)
