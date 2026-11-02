"""Find handwritten labels that overlap each other while both are on screen.
    python3 overlap_check.py osm_bp      (module with build())"""
import importlib
import sys

import board as B


def boxes(bd):
    gone_at = {}
    for te, de, ids in bd.erases:
        for i in ids:
            gone_at[i] = min(gone_at.get(i, 1e9), te)
    out = []
    for it in bd.items:
        if isinstance(it, B.Text):
            x0, y0 = it.px / B.BS, it.py / B.BS
            cols = it.cols
            if len(cols) == 0:
                continue
            x1 = x0 + (cols[0]) / B.BS
            x2 = x0 + (cols[-1] + 1) / B.BS
            h = it.img.height / B.BS
            out.append((it, (x1 + 2, y0 + h * 0.18, x2 - 2, y0 + h * 0.82), it.t, gone_at.get(id(it), 1e9)))
    return out


def check(bd):
    bx = boxes(bd)
    bad = []
    for i in range(len(bx)):
        for j in range(i + 1, len(bx)):
            a, ra, ta0, ta1 = bx[i]
            b, rb, tb0, tb1 = bx[j]
            if max(ta0, tb0) >= min(ta1, tb1):
                continue
            if ra[0] < rb[2] and rb[0] < ra[2] and ra[1] < rb[3] and rb[1] < ra[3]:
                bad.append((max(ta0, tb0), a, b))
    return bad


if __name__ == "__main__":
    mod = importlib.import_module(sys.argv[1])
    bd, sc = mod.build()
    bad = check(bd)
    for t, a, b in bad:
        print(f"{t:6.1f}s overlap: '{a.label}' <-> '{b.label}'")
    print("overlaps:", len(bad))
