# -*- coding: utf-8 -*-
"""Розгортання штрихових SVG-контурів у замкнені полігони для шрифту.

Підтримувані команди шляху: M, L, H, V, Q.
Капи: 'round' (рукопис) та 'butt' (друк).
"""
import math
import re

_TOKEN = re.compile(r'([MLHVQ])|(-?\d+\.?\d*)')


def parse_subpaths(d, samples=12):
    """SVG path -> список полілайнів [(x, y), ...]."""
    toks = [(m.group(1), float(m.group(2)) if m.group(2) else None)
            for m in _TOKEN.finditer(d)]
    i = 0
    sub, subs = [], []
    cx = cy = 0.0

    def nums(n):
        nonlocal i
        out = []
        while len(out) < n:
            _, v = toks[i]
            i += 1
            if v is not None:
                out.append(v)
        return out

    while i < len(toks):
        cmd, _ = toks[i]
        if cmd is None:
            i += 1
            continue
        i += 1
        if cmd == 'M':
            if sub:
                subs.append(sub)
            cx, cy = nums(2)
            sub = [(cx, cy)]
        elif cmd == 'L':
            cx, cy = nums(2)
            sub.append((cx, cy))
        elif cmd == 'H':
            cx = nums(1)[0]
            sub.append((cx, cy))
        elif cmd == 'V':
            cy = nums(1)[0]
            sub.append((cx, cy))
        elif cmd == 'Q':
            qx, qy, ex, ey = nums(4)
            x0, y0 = cx, cy
            for k in range(1, samples + 1):
                t = k / samples
                bx = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * qx + t * t * ex
                by = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * qy + t * t * ey
                sub.append((bx, by))
            cx, cy = ex, ey
    if sub:
        subs.append(sub)
    return subs


def _dedupe(pts, eps=1e-6):
    out = [pts[0]]
    for p in pts[1:]:
        if math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > eps:
            out.append(p)
    return out


def stroke_poly(pts, r, cap='round'):
    """Полілайн -> замкнений полігон-обвід товщиною 2r."""
    pts = _dedupe(pts)
    if len(pts) < 2:
        c = pts[0]
        return [(c[0] + r * math.cos(a), c[1] + r * math.sin(a))
                for a in (k * math.pi / 8 for k in range(16))]
    n = len(pts)

    def seg_dir(a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        return (dx / length, dy / length)

    left, right = [], []
    for i, p in enumerate(pts):
        if i == 0:
            d = seg_dir(pts[0], pts[1])
        elif i == n - 1:
            d = seg_dir(pts[-2], pts[-1])
        else:
            d1 = seg_dir(pts[i - 1], pts[i])
            d2 = seg_dir(pts[i], pts[i + 1])
            dx, dy = d1[0] + d2[0], d1[1] + d2[1]
            length = math.hypot(dx, dy)
            d = (dx / length, dy / length) if length > 1e-6 else d1
        nx, ny = -d[1], d[0]
        if 0 < i < n - 1:
            d1 = seg_dir(pts[i - 1], pts[i])
            cosh = max(0.34, abs(nx * (-d1[1]) + ny * d1[0]))
            k = min(1.0 / cosh, 2.6)  # мітер з обмеженням
        else:
            k = 1.0
        left.append((p[0] + nx * r * k, p[1] + ny * r * k))
        right.append((p[0] - nx * r * k, p[1] - ny * r * k))

    def round_cap(center, frm, to, direction):
        a0 = math.atan2(frm[1] - center[1], frm[0] - center[0])
        a1 = math.atan2(to[1] - center[1], to[0] - center[0])
        best = None
        for sweep in (a1 - a0, a1 - a0 - 2 * math.pi, a1 - a0 + 2 * math.pi):
            mid = a0 + sweep / 2
            score = math.cos(mid) * direction[0] + math.sin(mid) * direction[1]
            if best is None or score > best[0]:
                best = (score, sweep)
        sweep = best[1]
        return [(center[0] + r * math.cos(a0 + sweep * t / 7.0),
                 center[1] + r * math.sin(a0 + sweep * t / 7.0))
                for t in range(1, 7)]

    d_end = seg_dir(pts[-2], pts[-1])
    d_start = seg_dir(pts[1], pts[0])
    poly = left[:]
    if cap == 'round':
        poly += round_cap(pts[-1], left[-1], right[-1], d_end)
    poly += right[::-1]
    if cap == 'round':
        poly += round_cap(pts[0], right[0], left[0], d_start)
    return poly
