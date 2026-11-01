#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The ISP and MTE words of the triangle's state block: their fields by glossary name, the
coverage of the triangle's samples, the fitters and readers of what the 11.6 runs stored, and
the tables that vary the words on the laptop.

FIELDS names each word's fields as the glossary does (ISP0, ISP1, ISP2, OUTSEL, MTECTL and the
ISP registers whose fields are named); decode() splits a word into them and keeps the bits
outside every field as `<WORD>.rest`.

The coverage model: the triangle in sixteenths of a pixel, a sample at (a, b) / 16 from the
pixel's top-left corner inside when every edge function is positive, or zero on the left edge
(the edge that runs up the screen), the top-left rule; of that rule the 11.6 images show only
that a sample on the long edge is outside. cover() gives the pixels any of a set of samples
covers. Two readings of ISP0.SAMPLE_COVERAGE (Q031) are rule_cover()'s: "eight", any of
the four samples of CR_ISP_MULTISAMPLECTL and the four of CR_ISP_SAMPLE_POS; "centre", the four
of CR_ISP_SAMPLE_POS or the pixel centre, the centre inside on every edge.

The line model (E279): an x-major line covers column x when its span sample, x + 1/2 with
CR_ISP_LINE_SAMPLE_POS bit 0 set and x + 1 with it clear, lies in [start, end), and in that
column the rows r whose centre r + 1/2 lies in [y - w/2, y + w/2), y the line's y at the
column's centre x + 1/2 and w ISP1.LINE_WIDTH / 16; line_cover() gives those pixels.

The sample-layout fitter (Q030): a multisampled image is read as a layout of fx x fy target
pixels per source pixel, one sample a slot (side by side in x, in y, or 2x2); fit_layout() finds,
for each layout and slot, the sample position whose coverage of the known triangle matches the
slot's pixels best, and ranks the layouts by the pixels that still differ.

    isp_words.py decode WORD VALUE           the fields of one word
    isp_words.py table DIR                   write the 11.6 tables into DIR/<unit>/<feature>.toml
    isp_words.py rules RAW PROBE TABLE       Q031: each case against the two coverage rules
    isp_words.py layout RAW PROBE TABLE      Q030: each case's best layouts and sample positions
    isp_words.py lines RAW PROBE TABLE       each case's drawn columns, row by row, and the
                                             pixels the line model misses (lines)
    isp_words.py copies RAW PROBE TABLE      each case's pixels by the copy whose depth they carry
    isp_words.py counts RAW PROBE TABLE      each case's colours and their pixel counts
    isp_words.py unpack OUTPUT DIR           the scene script's dumps into DIR/*.bin
"""
from __future__ import annotations

import argparse
import base64
import collections
import gzip
import pathlib
import re
import struct
import sys
import tomllib
from fractions import Fraction

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pixels  # noqa: E402

BG = pixels.BG
SENTINEL = 0xdeadbeef
GREEN = 0xff00ff00
BLUE = 0xff0000ff

FIELDS = {
    "ISP0": [("SREF", 7, 0), ("ISP2_PRESENT", 8, 8), ("BIT9", 9, 9),
             ("TWO_SIDED", 11, 11), ("OBJ_TYPE", 17, 15), ("DWRITE_DISABLE", 20, 20),
             ("TAGWRITE_DISABLE", 21, 21), ("DCMP_MODE", 24, 22), ("PASS_TYPE", 27, 25),
             ("SAMPLE_COVERAGE", 28, 28)],
    "ISP1": [("VISREG", 2, 0), ("VISTEST", 3, 3), ("COLOUR_MASK", 7, 4), ("LINE_WIDTH", 15, 8),
             ("POLY_OFFSET", 23, 23), ("VALID_ID", 31, 26)],
    "ISP2": [("SW_MASK", 7, 0), ("SCMP_MASK", 15, 8), ("SOP3", 18, 16), ("SOP2", 21, 19),
             ("SOP1", 24, 22), ("SCMP_MODE", 27, 25)],
    "OUTSEL": [("PLANES", 7, 0), ("PSPRITE_SIZE_PRES", 8, 8), ("COLOUR_PRES", 11, 11),
               ("VTX_SIZE", 19, 16)],
    "MTECTL": [("CULL_MODE", 1, 0), ("NO_TRANSFORM", 6, 6), ("FLAT_VERTEX", 8, 7),
               ("ATTR_SMOOTH", 29, 10)],
    "CR_ISP_CTL": [("VALID_ID", 5, 0), ("PROCESS_EMPTY_TILES", 8, 8)],
    "CR_ISP_MSAA": [("MODE", 1, 0), ("ENABLE", 31, 31)],
    "CR_ISP_MULTISAMPLECTL": [(f"SAMPLE{k}_{ax}", 4 * (2 * k + i) + 3, 4 * (2 * k + i))
                              for k in range(4) for i, ax in enumerate("XY")],
}
# The state block of the triangle job (sgxfive_tri_block): word -> what it holds
BLOCK = {0: "PRESENCE", 1: "ISP0", 2: "ISP1", 3: "PDS secondary", 4: "PDS size",
         5: "PDS primary", 6: "VIEWPORT.X_OFFSET", 7: "VIEWPORT.X_SCALE", 8: "VIEWPORT.Y_OFFSET",
         9: "VIEWPORT.Y_SCALE", 10: "VIEWPORT.Z_OFFSET", 11: "VIEWPORT.Z_SCALE", 12: "wrap",
         13: "OUTSEL", 14: "WCLAMP", 15: "MTECTL", 16: "COORDSIZE", 17: "COORDFMT"}
ISP0_JOB, ISP1_JOB, OUTSEL_JOB = 0x01d00200, 0x10f0, 0x43000
CLIP = [(-0.75, -0.75), (0.75, -0.375), (-0.375, 0.75)]   # the library triangle in clip space


class IspError(Exception):
    pass


def _mask(hi: int, lo: int) -> int:
    return (1 << (hi + 1)) - (1 << lo)


def decode(word: str, value: int) -> dict:
    """{glossary name: field value} of one word, and `<word>.rest` the bits outside them."""
    if word not in FIELDS:
        raise IspError(f"no word {word}: one of {', '.join(FIELDS)}")
    out, rest = {}, value
    for name, hi, lo in FIELDS[word]:
        out[f"{word}.{name}"] = (value & _mask(hi, lo)) >> lo
        rest &= ~_mask(hi, lo)
    out[f"{word}.rest"] = rest
    return out


def f32(v: float) -> int:
    return struct.unpack("<I", struct.pack("<f", v))[0]


def float_of(u: int) -> float:
    return struct.unpack("<f", struct.pack("<I", u & 0xffffffff))[0]


# ---- the coverage model ---------------------------------------------------------------------

def samples(word: int) -> list[tuple[int, int]]:
    """The four samples a position word places: byte k is sample k, x in bits 3:0, y in 7:4."""
    return [((word >> 8 * k) & 0xf, (word >> (8 * k + 4)) & 0xf) for k in range(4)]


def default_tri(width: int, height: int) -> tuple:
    """The library triangle (8, 8), (56, 20), (20, 56) of a 64x64 target, scaled, in 1/16."""
    return tuple((round((cx + 1) * width / 2 * 16), round((cy + 1) * height / 2 * 16))
                 for cx, cy in CLIP)


def affine_target(x0: int, y0: int, size: int, k: int) -> tuple:
    """A right triangle with its left edge vertical at x0 + k/16 and its top edge horizontal at
    y0 + k/16, its legs size pixels long, in 1/16 (the layout probes' shape)."""
    a, b = x0 * 16 + k, y0 * 16 + k
    return ((a, b), (x0 * 16 + size * 16, b), (a, y0 * 16 + size * 16))


def affine_params(tri: tuple, width: int, height: int) -> tuple:
    """(A, B, C, D, E, F): x' = A x + B y + C, y' = D x + E y + F in clip space maps the
    library triangle's vertices onto tri (in 1/16 pixel) on a width x height target."""
    dst = [(p[0] / 16 / width * 2 - 1, p[1] / 16 / height * 2 - 1) for p in tri]
    m = [[cx, cy, 1.0] for cx, cy in CLIP]

    def solve(rhs):
        a = [row[:] + [r] for row, r in zip(m, rhs)]
        for i in range(3):
            piv = max(range(i, 3), key=lambda r: abs(a[r][i]))
            a[i], a[piv] = a[piv], a[i]
            for r in range(3):
                if r != i:
                    f = a[r][i] / a[i][i]
                    a[r] = [x - f * y for x, y in zip(a[r], a[i])]
        return [a[i][3] / a[i][i] for i in range(3)]
    return (*solve([d[0] for d in dst]), *solve([d[1] for d in dst]))


def _edge(a, b, p) -> int:
    return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])


def inside(tri: tuple, x16: int, y16: int, every_edge: bool = False) -> bool:
    """Whether the point (in 1/16 pixel) is inside: every edge function positive, zero allowed
    on an edge that runs up the screen (top-left rule), or on every edge. The coverage images
    (E278) fit with zero allowed or not on the library triangle's left edge and on its edge
    from (8, 8) to (56, 20): only the exclusion on its long edge is seen."""
    area = _edge(tri[0], tri[1], tri[2])
    for i in range(3):
        a, b = tri[i], tri[(i + 1) % 3]
        e = _edge(a, b, (x16, y16)) * (1 if area > 0 else -1)
        if e < 0:
            return False
        if e == 0 and not every_edge:
            dy = (b[1] - a[1]) * (1 if area > 0 else -1)
            if not (dy < 0 or (dy == 0 and (b[0] - a[0]) * (1 if area > 0 else -1) > 0)):
                return False
    return True


def cover(tri: tuple, width: int, height: int, smp: list, centre: bool = False) -> set:
    """The pixels (x, y) any of the samples covers; centre: the pixel centre too, inside on
    every edge."""
    xs = [p[0] for p in tri]
    ys = [p[1] for p in tri]
    out = set()
    for y in range(max(0, min(ys) // 16 - 1), min(height, max(ys) // 16 + 2)):
        for x in range(max(0, min(xs) // 16 - 1), min(width, max(xs) // 16 + 2)):
            if any(inside(tri, x * 16 + a, y * 16 + b) for a, b in smp) or (
                    centre and inside(tri, x * 16 + 8, y * 16 + 8, every_edge=True)):
                out.add((x, y))
    return out


RULES = ("eight", "centre", "0520", "04c8", "single")


def rule_cover(rule: str, tri: tuple, width: int, height: int, m04c8: int, m0520: int) -> set:
    """ISP0.SAMPLE_COVERAGE's coverage under one reading: eight (both words' samples), centre
    (0x0520's and the centre), 0520 or 04c8 (one word's samples); single, the coverage with
    the bit clear: byte 0 of 0x04c8 alone."""
    if rule == "eight":
        return cover(tri, width, height, samples(m04c8) + samples(m0520))
    if rule == "centre":
        return cover(tri, width, height, samples(m0520), centre=True)
    if rule == "single":
        return cover(tri, width, height, samples(m04c8)[:1])
    if rule in ("0520", "04c8"):
        return cover(tri, width, height, samples(m0520 if rule == "0520" else m04c8))
    raise IspError(f"no rule {rule}: one of {', '.join(RULES)}")


def image_of(covered: set, width: int, height: int, colour: int = GREEN) -> list[int]:
    return [colour if (x, y) in covered else BG for y in range(height) for x in range(width)]


def binary(img: list[int], colour: int = GREEN) -> list[int | None]:
    """1 where the image holds colour, 0 where the background, None elsewhere."""
    return [1 if v == colour else 0 if v == BG else None for v in img]


def fit_rules(img: list[int], m04c8: int, m0520: int, width: int, height: int,
              colour: int = GREEN, tri: tuple | None = None) -> dict:
    """{rule: pixels the image and the rule disagree on} for each reading of RULES."""
    tri = tri or default_tri(width, height)
    got = {(i % width, i // width) for i, v in enumerate(binary(img, colour)) if v}
    return {r: len(got ^ rule_cover(r, tri, width, height, m04c8, m0520)) for r in RULES}


# ---- the line model ---------------------------------------------------------------------------

LINE = 0x84c00002            # VDM word 2 of the line probes: index list type 1, two indices
LINE_END = ((-0.75, -0.75), (0.75, -0.375))   # vertices 0 and 1 of the library triangle


def line_ends(blk: dict, width: int = 64, height: int = 64) -> tuple:
    """The line's ends in pixels (Fractions) as the state block's viewport words place them:
    x = X_OFFSET + X_SCALE cx (blk:6, blk:7), y = Y_OFFSET + Y_SCALE cy (blk:8, blk:9), the
    job's values where blk does not set them."""
    def word(k, v):
        return Fraction(float_of(blk[k])) if k in blk else Fraction(v)
    xo, xs, yo, ys = (word(6, width // 2), word(7, width // 2), word(8, height // 2),
                      word(9, height // 2))
    return tuple((xo + xs * Fraction(cx), yo + ys * Fraction(cy)) for cx, cy in LINE_END)


def line_cover(ends: tuple, sample_pos: int = 1, line_width: int = 0x10,
               row_at: Fraction | None = None, width: int = 64, height: int = 64) -> set:
    """The pixels an x-major line covers (E279): column x when its span sample (x + 1/2 with
    CR_ISP_LINE_SAMPLE_POS bit 0 set, x + 1 clear) lies in [start, end); in it the rows whose
    sample r + row_at lies in [y - w/2, y + w/2), y the line's y at x + row_at and w =
    ISP1.LINE_WIDTH / 16; row_at is 1/2, the pixel centre. row_at = 1 with bit 0 clear is the
    far-corner reading E279 first gave, kept to show that the images refute it."""
    (x0, y0), (x1, y1) = sorted(ends)
    if abs(x1 - x0) < abs(y1 - y0):
        raise IspError("line_cover: a y-major line is not modelled")
    span = Fraction(1, 2) if sample_pos & 1 else Fraction(1)
    row_at = Fraction(1, 2) if row_at is None else row_at
    half = Fraction(line_width, 32)
    out = set()
    for x in range(width):
        if not x0 <= x + span < x1:
            continue
        y = y0 + (y1 - y0) * (x + row_at - x0) / (x1 - x0)
        out |= {(x, r) for r in range(height) if y - half <= r + row_at < y + half}
    return out


def line_setting(case_set: dict) -> tuple[dict, int, int]:
    """(state-block words, CR_ISP_LINE_SAMPLE_POS, ISP1.LINE_WIDTH) of one case of a line
    probe; 0x0418 is 1 and the width 0x10 in the job."""
    blk = {int(k): v for k, v in case_set.get("blk", {}).items()}
    pos = int(next((k.split("=")[1] for k in case_set.get("kpoke", [])
                    if k.startswith("rd:26=")), "1"), 0)
    return blk, pos, decode("ISP1", blk.get(2, ISP1_JOB))["ISP1.LINE_WIDTH"]


# ---- the sample-layout fitter -----------------------------------------------------------------

LAYOUTS = ((1, 1), (2, 1), (1, 2), (2, 2), (4, 1), (1, 4))


def layout_image(tri: tuple, width: int, height: int, layout: tuple, pos: list) -> list[int]:
    """The image a layout stores: target pixel (fx px + i, fy py + j) holds sample i + fx j of
    source pixel (px, py), at position pos[i + fx j]."""
    fx, fy = layout
    img = [BG] * (width * height)
    for k, (a, b) in enumerate(pos):
        i, j = k % fx, k // fx
        for px, py in cover(tri, width // fx, height // fy, [(a, b)]):
            img[(py * fy + j) * width + px * fx + i] = GREEN
    return img


def covers_alike(tri: tuple, width: int, height: int, p: tuple, q: tuple) -> bool:
    return cover(tri, width, height, [p]) == cover(tri, width, height, [q])


def _edge_pixels(tri: tuple, width: int, height: int) -> tuple[set, set]:
    """(pixels some position covers, pixels every position covers) of a width x height grid."""
    some, every = set(), set()
    corners = [(a, b) for a in (0, 15) for b in (0, 15)]
    for x, y in cover(tri, width, height, corners + [(a, b) for a in range(16)
                                                     for b in range(0, 16, 15)] +
                      [(a, b) for a in range(0, 16, 15) for b in range(16)]):
        some.add((x, y))
        if all(inside(tri, x * 16 + a, y * 16 + b) for a, b in corners):
            every.add((x, y))
    return some, every


def binned_tiles(tri: tuple, tile: int = 16) -> set:
    """The tile x tile tiles the triangle's bounding box meets, in single-sample pixels: the
    tiles the tiling engine bins it into without its anti-aliasing bits (the bounding box is
    an upper bound of the region test)."""
    xs = [p[0] for p in tri]
    ys = [p[1] for p in tri]
    return {(tx, ty) for tx in range(min(xs) // 16 // tile, (max(xs) - 1) // 16 // tile + 1)
            for ty in range(min(ys) // 16 // tile, (max(ys) - 1) // 16 // tile + 1)}


def tile_mask(tiles: set, width: int, height: int, tile: int = 16) -> set:
    """The target pixels of those tiles: a multisampled render stores each binned tile's
    samples at the tile's place, in sample units."""
    return {(x, y) for y in range(height) for x in range(width)
            if (x // tile, y // tile) in tiles}


def _slot_obs(bits, width, height, fx, fy, k, mask):
    w, h = width // fx, height // fy
    i, j = k % fx, k // fx
    obs = {}
    for py in range(h):
        for px in range(w):
            x, y = px * fx + i, py * fy + j
            v = bits[y * width + x]
            if v is not None and (mask is None or (x, y) in mask):
                obs[(px, py)] = v
    return obs


def fit_layout_joint(cases: list, width: int, height: int, colour: int = GREEN,
                     layouts=LAYOUTS, masked: bool = True) -> list[dict]:
    """Every case (image, triangle) of one setting at once: per layout and slot, the sample
    positions that miss fewest pixels over all the cases (the positions do not move between
    cases), each case read only inside the tiles its triangle is binned into when masked."""
    out = []
    for fx, fy in layouts:
        w, h = width // fx, height // fy
        slots, total = [], 0
        for k in range(fx * fy):
            score = collections.Counter()
            for img, tri in cases:
                bits = binary(img, colour)
                mask = tile_mask(binned_tiles(tri), width, height) if masked else None
                obs = _slot_obs(bits, width, height, fx, fy, k, mask)
                for a in range(16):
                    for b in range(16):
                        score[(a, b)] += sum(1 for (x, y), v in obs.items()
                                             if v != inside(tri, x * 16 + a, y * 16 + b))
            best = min(score.values())
            slots.append((best, sorted(p for p, n in score.items() if n == best)))
            total += best
        out.append({"layout": (fx, fy), "slots": slots, "mismatch": total})
    return sorted(out, key=lambda r: (r["mismatch"], r["layout"][0] * r["layout"][1]))


def fit_layout(img: list[int], tri: tuple, width: int, height: int, colour: int = GREEN,
               layouts=LAYOUTS) -> list[dict]:
    """Per layout: each slot's best sample position (a, b) and the pixels it misses; sorted
    by the total missed. Pixels holding neither colour nor background are left out."""
    bits = binary(img, colour)
    out = []
    for fx, fy in layouts:
        w, h = width // fx, height // fy
        some, every = _edge_pixels(tri, w, h)
        border = sorted(some - every)
        best_pos, total, unread = [], 0, 0
        for k in range(fx * fy):
            i, j = k % fx, k // fx
            obs = {}
            for py in range(h):
                for px in range(w):
                    v = bits[(py * fy + j) * width + px * fx + i]
                    if v is None:
                        unread += 1
                    else:
                        obs[(px, py)] = v
            fixed = sum(1 for p, v in obs.items() if p not in some and v) + \
                sum(1 for p, v in obs.items() if p in every and not v)
            best = None
            for a in range(16):
                for b in range(16):
                    miss = sum(1 for (x, y) in border if (x, y) in obs and
                               obs[(x, y)] != inside(tri, x * 16 + a, y * 16 + b))
                    if best is None or miss < best[0]:
                        best = (miss, (a, b))
            best_pos.append(best[1])
            total += best[0] + fixed
        out.append({"layout": (fx, fy), "samples": best_pos, "mismatch": total,
                    "unread": unread})
    return sorted(out, key=lambda r: (r["mismatch"], r["layout"][0] * r["layout"][1]))


# ---- readers ----------------------------------------------------------------------------------

def spans(img: list[int], width: int, colour: int) -> dict:
    """{row: (first column, last column, pixels)} of the rows holding colour."""
    out = {}
    for y in range(len(img) // width):
        xs = [x for x in range(width) if img[y * width + x] == colour]
        if xs:
            out[y] = (xs[0], xs[-1], len(xs))
    return out


def copy_of(v: int) -> int | None:
    """The copy c whose depth c/16 a pixel carries (vtx_z.s, pix_pa0), or None."""
    if v in (BG, SENTINEL):
        return None
    c = float_of(v) * 16
    return round(c) if abs(c - round(c)) < 1e-3 and 0 <= c < 64 else None


def case_images(raw: str, probe_name: str) -> tuple[dict, dict]:
    img, fail = pixels.parse(raw)
    pre = f"{probe_name}__"
    return ({int(k[len(pre):]): v for k, v in img.items() if k.startswith(pre)},
            {int(k[len(pre):]): v for k, v in fail.items() if k.startswith(pre)})


def pb_unpack(text: str, out: pathlib.Path) -> list[pathlib.Path]:
    """The base64 gzip blocks of the scene script's output ("#### param NAME" or "#### tadata
    NAME", the block, "#### end") written to out/NAME.param.bin and out/NAME.tadata.bin."""
    files, cur, buf = [], None, []
    for line in text.splitlines():
        m = re.match(r"#### (param|tadata) (\S+)$", line)
        if m:
            cur, buf = f"{m[2]}.{m[1]}.bin", []
        elif line == "#### end" and cur:
            p = pathlib.Path(out) / cur
            p.write_bytes(gzip.decompress(base64.b64decode("".join(buf))))
            files.append(p)
            cur = None
        elif cur:
            buf.append(line.strip())
    return files


# ---- the tables -------------------------------------------------------------------------------

POS4 = 0xeaa26e26            # the sample positions of the 4x runs (E210)
TE_AA = 0xe0000000           # the TE anti-aliasing bits of those runs
STENCIL_S0 = 0x0f            # the background stencil of the op probes


def _toml(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
    if isinstance(v, int):
        return f"0x{v:x}" if v > 9 else str(v)
    if isinstance(v, list):
        return "[" + ", ".join(_toml(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{ " + ", ".join(f"{k} = {_toml(x)}" for k, x in v.items()) + " }"
    raise IspError(f"no TOML for {v!r}")


def table_text(unit: str, title: str, about: str, ps: list[dict], needs=("render", "kpoke"),
               head: dict | None = None, open_: list | None = None) -> str:
    lines = ["# SPDX-License-Identifier: MIT", "# SPDX-FileCopyrightText: 2026 Josep Torra",
             f"# {unit} {title}: {len(ps)} probes (written by tools/usse-asm/isp_words.py).",
             f"# {about}", f"needs = {_toml(list(needs))}"]
    if open_:
        lines.append(f"open = {_toml(open_)}")
    for k, v in (head or {}).items():
        lines.append(f"{k} = {_toml(v)}")
    for p in ps:
        lines.append("\n[[probe]]")
        lines += [f"{k} = {_toml(v)}" for k, v in p.items()]
    return "\n".join(lines) + "\n"


def _pix(colour: int = GREEN) -> list[str]:
    return [f"mov.skipinv.end o0, #0x{colour:08X}"]


def _probe(name: str, question: str, cases: list, labels: list, *, source="pix_op.s",
           slot="pixel", inputs=("OP",), **kw) -> dict:
    p = {"name": name, "question": question, "source": source, "host": "tri", "slot": slot}
    p.update(kw)
    p.setdefault("size", [64, 64])
    p["pixels"] = True
    p["inputs"] = list(inputs)
    p["labels"], p["cases"] = labels, cases
    return p


def _sets(sets: list[dict]) -> list[dict]:
    """case_set entries with string keys (TOML tables)."""
    return [{k: ({str(w): v for w, v in val.items()} if isinstance(val, dict) else val)
             for k, val in s.items()} for s in sets]


def coverage_probes() -> list[dict]:
    """Q031: ISP0 bit 28 with CR_ISP_MULTISAMPLECTL (cmd:16) and CR_ISP_SAMPLE_POS (rd:19)."""
    pairs = [(0x88, 0), (0xcccccccc, 0xcccccccc), (0xeeeeeeee, 0xeeeeeeee),
             (0xcccccccc, 0), (0xeeeeeeee, 0), (0x88, 0xcccccccc), (0x88, 0xeeeeeeee),
             (0, 0xcccccccc)]
    for k in range(4):
        pairs.append((0xcccccccc & ~(0xff << 8 * k), 0xcccccccc))
    for k in range(4):
        pairs.append((0xcccccccc, 0xcccccccc & ~(0xff << 8 * k)))
    for word in (0x0000000f, 0x000000f0, 0x0000f000, 0x00f00000, 0xf0000000, 0x000f0000):
        pairs.append((0x88, word))
    out = []
    for run in ("", "-r2"):
        out.append(_probe(
            f"isp-coverage-samples-bit28{run}",
            "with ISP word 0 bit 28 set, which samples of 0x04c8 (cmd:16) and 0x0520 (rd:19) "
            "decide a pixel's coverage", [_pix() for _ in pairs],
            [f"04c8 0x{m:08x} 0520 0x{s:08x}" for m, s in pairs],
            blk={"1": ISP0_JOB | 1 << 28},
            case_set=_sets([{"cmd": {16: m}, "kpoke": [f"rd:19=0x{s:x}"]} for m, s in pairs])))
    single = [(0xcccccccc, 0xcccccccc), (0x000000cc, 0), (0x88, 0xcccccccc),
              (0xcccccc88, 0)]
    out.append(_probe(
        "isp-coverage-samples-single", "the same words with bit 28 clear: which sample decides",
        [_pix() for _ in single], [f"04c8 0x{m:08x} 0520 0x{s:08x}" for m, s in single],
        case_set=_sets([{"cmd": {16: m}, "kpoke": [f"rd:19=0x{s:x}"]} for m, s in single])))
    return out


def coverage_byte_probes() -> list[dict]:
    """Q031 follow-up: bytes 1-3 of CR_ISP_MULTISAMPLECTL at (15, 0) and (0, 15) one at a time,
    the rest at (12, 12), with CR_ISP_SAMPLE_POS at 0xcccccccc: is each byte x in 3:0, y in
    7:4."""
    pairs = [((0xcccccccc & ~(0xff << 8 * k)) | v << 8 * k, 0xcccccccc)
             for k in (1, 2, 3) for v in (0x0f, 0xf0)]
    return [_probe(f"isp-coverage-bytes-bit28{run}", "with ISP word 0 bit 28 set, the nibble "
                   "order of bytes 1-3 of 0x04c8", [_pix() for _ in pairs],
                   [f"04c8 0x{m:08x} 0520 0x{s:08x}" for m, s in pairs],
                   blk={"1": ISP0_JOB | 1 << 28},
                   case_set=_sets([{"cmd": {16: m}, "kpoke": [f"rd:19=0x{s:x}"]}
                                   for m, s in pairs])) for run in ("", "-r2")]


def _hexf(v: float) -> str:
    return f"0x{f32(v):08X}"


def layout_probes() -> list[dict]:
    """Q030: a right triangle whose left and top edges move by k/16 (vtx_affine.s), under
    CR_ISP_MSAA modes 0-2, without and with the TE anti-aliasing bits; then modes 1 and 2 with
    CR_ISP_MSAA bit 31 clear and set, the render memory dumped."""
    ks = list(range(0, 16, 2))
    out = []
    for te in (0, TE_AA):
        for n in (0, 1, 2):
            cases = [[_hexf(v) for v in affine_params(affine_target(4, 4, 10, k), 64, 64)]
                     for k in ks]
            out.append(_probe(
                f"isp-msaa-layout-m{n}-te{1 if te else 0}",
                f"what CR_ISP_MSAA mode {n} stores of a triangle whose left and top edges sit "
                f"at 4 + k/16 ({'with' if te else 'without'} the TE anti-aliasing bits)",
                cases, [f"k = {k}" for k in ks], source="vtx_affine.s", slot="vtxuse",
                inputs=("A", "B", "C", "D", "E", "F"), slots={"pixel": "pix_green.s"},
                temps=8, cmd={"1": te, "10": POS4, "13": 0x80000000 | n, "16": POS4}))
    for run in ("", "-r2"):
        for n in (1, 2):
            for b31 in (0, 1):
                out.append(_probe(
                    f"isp-msaa-layout-enable-m{n}-b31{b31}{run}",
                    f"CR_ISP_MSAA mode {n} with bit 31 {'set' if b31 else 'clear'}: the image "
                    "and the render memory", [_pix()], [f"mode {n}, bit 31 {b31}"],
                    cmd={"10": POS4, "13": b31 << 31 | n, "16": POS4}, dump_render=True))
    return out


def msaa_position_probes() -> list[dict]:
    """Q030 follow-up: which register places the multisampled samples. Mode 2 over the k
    triangles with the ISP's word (cmd:16, 0x04c8) and the MTE's (cmd:10) told apart, and with
    CR_ISP_SAMPLE_POS (rd:19) at another word."""
    ks = list(range(0, 16, 2))
    cases = [[_hexf(v) for v in affine_params(affine_target(4, 4, 10, k), 64, 64)] for k in ks]
    out = []
    for name, c16, c10, kp in (("isp", POS4, 0x88888888, None), ("mte", 0x88888888, POS4, None),
                               ("other", 0x2e62a6ea, POS4, None),
                               ("0520", POS4, POS4, 0x2e62a6ea)):
        kw = {"kpoke": [f"rd:19=0x{kp:x}"]} if kp else {}
        out.append(_probe(
            f"isp-msaa-positions-{name}", f"mode 2 with cmd:16 0x{c16:08x}, cmd:10 0x{c10:08x}"
            + (f", 0x0520 0x{kp:08x}" if kp else ""), cases, [f"k = {k}" for k in ks],
            source="vtx_affine.s", slot="vtxuse", inputs=("A", "B", "C", "D", "E", "F"),
            slots={"pixel": "pix_green.s"}, temps=8,
            cmd={"10": c10, "13": 0x80000002, "16": c16}, **kw))
    return out


def msaa_te_probes() -> list[dict]:
    """Q030 follow-up: the TE anti-aliasing bits (cmd:1, CR_TE_AA bits 31:29) one and more at a
    time under CR_ISP_MSAA modes 0, 1 and 2, on the library triangle."""
    tes = [0x80000000, 0x40000000, 0x20000000, 0xc0000000, 0xa0000000, 0x60000000, 0xe0000000]
    return [_probe(f"isp-msaa-te-m{n}", f"the TE anti-aliasing bits under CR_ISP_MSAA mode {n}",
                   [_pix() for _ in tes], [f"TE_AA 0x{t:08x}" for t in tes],
                   cmd={"10": POS4, "13": 0x80000000 | n, "16": POS4},
                   case_set=_sets([{"cmd": {1: t}} for t in tes])) for n in (0, 1, 2)]


def tagwrite_probes() -> list[dict]:
    """ISP0 bit 21: does an object that draws no colour write depth? The first object (copy 0)
    with and without the bit, depth less with writes; the second (copy 1, blue) depth less."""
    return [_probe(f"isp-tag-write-b21{b}", f"ISP0 bit 21 {'set' if b else 'clear'} on the first "
                   "of two objects: does the second still draw behind it", [_pix()],
                   [f"bit 21 {b}"], vertices=6, blk={"1": 0x00400200 | b << 21},
                   obj2={"first": 3, "blk": {"1": 0x00400200}, "pixel": "pix_blue.s"})
            for b in (0, 1)]


def line_probes() -> list[dict]:
    """E181/E202: the line (8, 8)-(56, 20) moved by the viewport's x offset (blk:6) in 1/16,
    with 0x0418 (rd:26) at 1 and 0; x and y together by quarters; the triangle as a control; and
    ISP1.LINE_WIDTH at nine values."""
    line = {"blk": {"1": 0x01d08200}, "vdm": {"2": 0x84c00002}}
    out = []
    for run in ("", "-r2"):
        sets, labels = [], []
        for r26 in (1, 0):
            for k in range(16):
                sets.append({"blk": {6: f32(32 + k / 16)}, "kpoke": [f"rd:26={r26}"]})
                labels.append(f"0418 {r26}, x + {k}/16")
        out.append(_probe(f"isp-line-sample-x{run}", "where a line's end pixels fall as the "
                          "viewport moves it by sixteenths, 0x0418 at 1 and 0",
                          [_pix() for _ in sets], labels, case_set=_sets(sets), **line))
    sets, labels = [], []
    for r26 in (1, 0):
        for q in range(4):
            sets.append({"blk": {6: f32(32 + q / 4), 8: f32(32 + q / 4)},
                         "kpoke": [f"rd:26={r26}"]})
            labels.append(f"0418 {r26}, x and y + {q}/4")
    out.append(_probe("isp-line-sample-xy", "the line moved in x and y together by quarters",
                      [_pix() for _ in sets], labels, case_set=_sets(sets), **line))
    sets, labels = [], []
    for r26 in (1, 0):
        for k in (0, 5, 8, 15):
            sets.append({"blk": {6: f32(32 + k / 16), 8: f32(32 + k / 16)},
                         "kpoke": [f"rd:26={r26}"]})
            labels.append(f"triangle, 0418 {r26}, x and y + {k}/16")
    out.append(_probe("isp-line-sample-tri", "whether the triangle reads 0x0418 at sub-pixel "
                      "offsets", [_pix() for _ in sets], labels, case_set=_sets(sets)))
    widths = (0x00, 0x04, 0x08, 0x10, 0x18, 0x20, 0x40, 0x80, 0xff)
    out.append(_probe("isp-line-sample-width", "how many rows the line covers per column at "
                      "each ISP1.LINE_WIDTH", [_pix() for _ in widths],
                      [f"LINE_WIDTH 0x{w:02x}" for w in widths],
                      case_set=_sets([{"blk": {2: w << 8 | 0xf0}} for w in widths]), **line))
    return out


def line_bias_probes() -> list[dict]:
    """E202: the other reading of 0x0418, a depth-bias format. A triangle whose depth slopes
    with x (vtx_zx.s; 0.5 + 0.5 x) against the clear depth 0.5, depth less, ISP1's polygon
    offset on, units (rd:5) and factor (rd:6) at four settings, 0x0418 (rd:26) at 1 and 0."""
    sets, labels = [], []
    for units, factor in ((0, 0.0), (1 << 20, 0.0), (0, 4.0), (0, 64.0)):
        for r26 in (1, 0):
            sets.append({"kpoke": [f"rd:5=0x{units:x}", f"rd:6=0x{f32(factor):x}",
                                   f"rd:26={r26}"]})
            labels.append(f"units 0x{units:x}, factor {factor}, 0418 {r26}")
    return [_probe(f"isp-line-bias-{run}", "whether 0x0418 changes the polygon offset of a "
                   "sloped depth", [_pix() for _ in sets], labels, case_set=_sets(sets),
                   blk={"1": 0x00500200, "2": ISP1_JOB | 1 << 23}, cmd={"14": f32(0.5)},
                   vtx_coords=2, slots={"vtxuse": "vtx_zx.s"}) for run in ("r1", "r2")]


def _vtx_op(lines: list[str], n: int = 6) -> list[str]:
    body = [f"        {s}" for s in lines] + ["        nop"] * (n - len(lines))
    return ["\n".join(body)]


def _o(reg: str, v: float) -> str:
    return f"mov.skipinv {reg}, #0x{f32(v):08X}"


def clip_probes() -> list[dict]:
    """Q039: user clip plane 1 alone with a 6-dword vertex (0x63002) at both signs, a 7-dword
    vertex (0x73002, then plane 2 alone, 0x73004) with one distance at -1 at a time, and fdpc
    cp1 in the 6-dword vertex."""
    out = []
    for run in ("", "-r2"):
        six = [(1, 1), (-1, -1), (1, -1), (-1, 1)]
        out.append(_probe(f"mte-clip-plane1-six{run}", "plane 1 alone, 6-dword vertex: which "
                          "dword it reads", [_vtx_op([_o("o4", a), _o("o5", b)]) for a, b in six],
                          [f"o4 {a:+d}, o5 {b:+d}" for a, b in six], source="vtx_fdpc.s",
                          slot="vtxuse", temps=12, vtx_coords=2, blk={"13": 0x63002}))
        seven = [(-1, 1, 1), (1, -1, 1), (1, 1, -1), (1, 1, 1), (-1, -1, -1)]
        for planes in (0x2, 0x4):
            out.append(_probe(
                f"mte-clip-plane1-seven-p{planes:x}{run}",
                f"OUTSEL planes 0x{planes:x} alone, 7-dword vertex: which dword decides",
                [_vtx_op([_o("o4", a), _o("o5", b), _o("o6", c)]) for a, b, c in seven],
                [f"o4 {a:+d}, o5 {b:+d}, o6 {c:+d}" for a, b, c in seven], source="vtx_fdpc.s",
                slot="vtxuse", temps=12, vtx_coords=3, blk={"13": 0x73000 | planes}))
    fd = []
    for cp, w in (("cp1", -1.0), ("cp1", 1.0), ("cp0", -1.0)):
        fd.append(_vtx_op([_o("o4", 1), _o("o5", 1), _o("r4", 0), _o("r5", 0), _o("r6", 0),
                           _o("r7", w), f"fdpc.skipinv.repeat4 r8, {cp}, pa0, r4"], 10))
    out.append(_probe("mte-clip-plane1-fdpc", "fdpc's cp1 with plane 1 alone (0x63002), o4 "
                      "and o5 at +1", fd, ["fdpc cp1, plane -w (outside)",
                                           "fdpc cp1, plane +w (inside)",
                                           "fdpc cp0, plane -w (outside)"],
                      source="vtx_fdpc10.s", slot="vtxuse", temps=16, vtx_coords=2,
                      blk={"13": 0x63002}))
    return out


def _fdpc(cp: str | None, w: float, outs: list[str]) -> list[str]:
    lines = list(outs) + [_o("r4", 0), _o("r5", 0), _o("r6", 0), _o("r7", w)]
    if cp:
        lines.append(f"fdpc.skipinv.repeat4 r8, {cp}, pa0, r4")
    return _vtx_op(lines, 10)


def clip_state_probes() -> list[dict]:
    """Q039 follow-up: whether a plane's state outlives the job that set it. Planes 1 and 2
    alone and plane 0, each a run of jobs in order: none setting the plane, one whose fdpc puts
    every vertex outside it (-w) or inside (+w), then none again."""
    out = []
    groups = (
        ("p1", 0x63002, 2, ["o4", "o5"], "cp1"),
        ("p2", 0x73004, 3, ["o4", "o5", "o6"], "cp2"),
        ("p0", 0x53001, 1, ["o4"], "cp0"))
    seq = [(None, 1.0), ("x", -1.0), (None, 1.0), ("x", 1.0), (None, 1.0), ("x", -1.0),
           (None, 1.0)]
    for run in ("", "-r2"):
        for name, outsel, coords, regs, cp in groups:
            outs = [_o(r, 1.0) for r in regs]
            cases = [_fdpc(cp if c else None, w, outs) for c, w in seq]
            labels = [f"{i}: " + (f"fdpc {cp}, plane {'+' if w > 0 else '-'}w" if c else
                                  "no fdpc") for i, (c, w) in enumerate(seq)]
            out.append(_probe(
                f"mte-clip-plane-state-{name}{run}",
                f"OUTSEL 0x{outsel:05x}, the distances at +1: does {cp}'s state outlive its job",
                cases, labels, source="vtx_fdpc10.s", slot="vtxuse", temps=16,
                vtx_coords=coords, blk={"13": outsel}))
    return out


def clip_dist_probes() -> list[dict]:
    """Q039 follow-up: with each plane's state first set inside (fdpc +w), whether the
    vertex's distance dwords still decide: plane 0 (0x53001) with o4 at -1 and +1, plane 1
    alone (0x63002) and planes 0 and 1 (0x63003) with o4 and o5 at each sign; then the state
    set outside (fdpc -w) with the dwords at +1; each a run of jobs in order."""
    out = []
    groups = (("p0", 0x53001, 1, ["o4"], ["cp0"]),
              ("p1", 0x63002, 2, ["o4", "o5"], ["cp1"]),
              ("p01", 0x63003, 2, ["o4", "o5"], ["cp0", "cp1"]))
    for run in ("", "-r2"):
        for name, outsel, coords, regs, cps in groups:
            signs = [[1.0] * len(regs)] + [[-1.0 if i == j else 1.0 for i in range(len(regs))]
                                            for j in range(len(regs))] + [[-1.0] * len(regs)]
            cases, labels = [], []
            for cp in cps:
                cases.append(_fdpc(cp, 1.0, [_o(r, 1.0) for r in regs]))
                labels.append(f"fdpc {cp}, plane +w, distances +1")
            for sg in signs:
                cases.append(_fdpc(None, 1.0, [_o(r, v) for r, v in zip(regs, sg)]))
                labels.append("no fdpc, " + ", ".join(f"{r} {v:+.0f}" for r, v in zip(regs, sg)))
            for cp in cps:
                cases.append(_fdpc(cp, -1.0, [_o(r, 1.0) for r in regs]))
                labels.append(f"fdpc {cp}, plane -w, distances +1")
                cases.append(_fdpc(None, 1.0, [_o(r, 1.0) for r in regs]))
                labels.append("no fdpc, distances +1")
                cases.append(_fdpc(cp, 1.0, [_o(r, 1.0) for r in regs]))
                labels.append(f"fdpc {cp}, plane +w, distances +1")
            out.append(_probe(
                f"mte-clip-plane-dist-{name}{run}",
                f"OUTSEL 0x{outsel:05x}: the distance dwords with the planes' state inside",
                cases, [f"{i}: {lab}" for i, lab in enumerate(labels)], source="vtx_fdpc10.s",
                slot="vtxuse", temps=16, vtx_coords=coords, blk={"13": outsel}))
    return out


def outsel_probes() -> list[dict]:
    """Q069: OUTSEL bits 13:12 at 3 (the job's), 2, 1 and 0 with no coordinate set, one set of
    two components and two sets (vtx_zx.s writes x, y to o4, o5; vtx_xy4.s to o4-o7), the render
    memory dumped."""
    out = []
    for run in ("", "-r2"):
        for name, kw, base in (
                ("none", {}, 0x43000),
                ("one", {"vtx_coords": 2, "slots": {"vtxuse": "vtx_zx.s",
                                                    "pixpds": "pds_iter_done.s"}}, 0x63000),
                ("two", {"vtx_coords": 4, "slots": {"vtxuse": "vtx_xy4.s",
                                                    "pixpds": "pds_iter_done.s"}}, 0x83000)):
            vals = [base, base & ~0x1000, base & ~0x2000, base & ~0x3000]
            blk = {"16": 0x12} if name == "two" else {}
            op = ["mov.skipinv.end o0, pa0"] if name != "none" else _pix()
            out.append(_probe(
                f"mte-outsel-bits-{name}{run}",
                f"OUTSEL bits 13:12 with {name} coordinate set(s): the image and the object",
                [op for _ in vals], [f"OUTSEL 0x{v:05x}" for v in vals],
                case_set=_sets([{"blk": {13: v}} for v in vals]), dump_render=True,
                temps=4, blk=blk, **kw))
    return out


def presence_probes() -> list[dict]:
    """Q069: the state block's presence word (0xdf43) with each of bits 16-31 set, four per
    probe so that a hang stops few cases."""
    out = []
    for g in range(4):
        bits = range(16 + 4 * g, 20 + 4 * g)
        out.append(_probe(
            f"mte-presence-high-{g}", "the presence word's bits 16-31 set one at a time",
            [_pix() for _ in bits], [f"presence bit {b}" for b in bits],
            case_set=_sets([{"blk": {0: 0xdf43 | 1 << b}} for b in bits])))
    return out


def depth_range_probes() -> list[dict]:
    """Q069: depth outside [0, 1]: a flat triangle at clip z from -2 to 2 and sloped (z = A x +
    B, vtx_zab.s), and the viewport's z offset (blk:10) past 0 and 1; depth test always, every
    pixel read."""
    flat = [-2.0, -1.5, -1.01, -1.0, -0.5, 0.0, 0.5, 1.0, 1.01, 1.5, 2.0]
    slope = [(2.0, 0.0), (4.0, 0.0), (2.0, 1.0), (2.0, -1.0)]
    cases = [[_hexf(0.0), _hexf(z)] for z in flat] + [[_hexf(a), _hexf(b)] for a, b in slope]
    labels = [f"clip z {z}" for z in flat] + [f"clip z = {a} x + {b}" for a, b in slope]
    out = [_probe("mte-depth-range-clip", "which clip-space depths the MTE removes", cases,
                  labels, source="vtx_zab.s", slot="vtxuse", inputs=("A", "B"), temps=8,
                  vtx_coords=2, slots={"pixel": "pix_green.s"})]
    offs = [-0.5, -0.01, 0.0, 1.0, 1.01, 1.5]
    out.append(_probe("mte-depth-range-viewport", "the viewport's z offset past 0 and 1 on the "
                      "flat triangle", [_pix() for _ in offs], [f"z offset {o}" for o in offs],
                      case_set=_sets([{"blk": {10: f32(o)}} for o in offs])))
    out.append(_probe("mte-depth-range-viewport-less", "the same with depth test less against "
                      "the clear depth 1.0", [_pix() for _ in offs],
                      [f"z offset {o}, less" for o in offs],
                      case_set=_sets([{"blk": {10: f32(o), 1: 0x00400200}} for o in offs])))
    return out


def depth_range2_probes() -> list[dict]:
    """Q069 again: the clip-space depths with vtx_zab.s's phase index fixed (the first run's
    program jumped to the wrong second phase and hung); and whether the viewport's depth past 0
    and 1 is clamped: depth greater against a clear depth of 1.0 and less against 0.0."""
    out = depth_range_probes()[:1]
    out[0] = dict(out[0], name="mte-depth-range2-clip")
    sets, labels = [], []
    for off, isp0, clear, what in ((1.5, 0x01100200, 1.0, "greater"),
                                   (1.01, 0x01100200, 1.0, "greater"),
                                   (0.9, 0x01100200, 0.8, "greater"),
                                   (-0.5, 0x00500200, 0.0, "less"),
                                   (-0.01, 0x00500200, 0.0, "less"),
                                   (0.1, 0x00500200, 0.2, "less")):
        sets.append({"blk": {10: f32(off), 1: isp0}, "cmd": {14: f32(clear)}})
        labels.append(f"z offset {off}, {what} than the clear {clear}")
    out.append(_probe("mte-depth-range2-clamp", "whether the depth past 0 and 1 is clamped",
                      [_pix() for _ in sets], labels, case_set=_sets(sets)))
    return out


_COPIES = {"vertices": 15, "copy_depth": True, "vtx_coords": 2, "temps": 4,
           "slots": {"pixpds": "pds_iter_done.s", "vtxuse": "vtx_z.s"}}
_PA0 = ["mov.skipinv.end o0, pa0"]


def depth_probes() -> list[dict]:
    """ISP0.DCMP_MODE and ISP0.DWRITE_DISABLE over five copies at depths c/16 (each pixel
    carries its copy's z), against the clear depth 1.0 and 0.0; and the other ISP0 bits
    flipped from depth less with writes."""
    out = []
    for run in ("", "-r2"):
        for bg in (1.0, 0.0):
            vals = [d << 22 | w << 20 | 0x200 for w in (0, 1) for d in range(8)]
            out.append(_probe(
                f"isp-depth-compare-bg{int(bg)}{run}",
                f"ISP0 bits 24:22 and 20 over five copies, clear depth {bg}",
                [_PA0 for _ in vals],
                [f"DCMP {v >> 22 & 7}, bit 20 {v >> 20 & 1}" for v in vals],
                case_set=_sets([{"blk": {1: v}} for v in vals]), cmd={"14": f32(bg)},
                **_COPIES))
    base = 1 << 22 | 0x200
    bits = (9, 10, 12, 13, 14, 19, 21, 29, 30, 31)
    out.append(_probe("isp-depth-compare-bits", "ISP0's other bits flipped from depth less "
                      "with writes, five copies", [_PA0 for _ in bits],
                      [f"ISP0 bit {b}" for b in bits],
                      case_set=_sets([{"blk": {1: base ^ 1 << b}} for b in bits]), **_COPIES))
    return out


def _isp2(cmp: int, sop1=0, sop2=0, sop3=0, cmask=0xff, wmask=0xff) -> int:
    return cmp << 25 | sop1 << 22 | sop2 << 19 | sop3 << 16 | cmask << 8 | wmask


def _two(name, question, cases_isp2, labels, ref2, *, s0=STENCIL_S0, isp0=0x00400355,
         cmp2=2, cmask2=0xff, case_isp0=None) -> dict:
    """The first object (copy 0, green) with ISP word 2 per case; the second (copy 1, blue,
    depth always) draws where the stencil compares cmp2 (2 equal) with ref2."""
    sets = []
    for i, w in enumerate(cases_isp2):
        blk = {3: w, 1: case_isp0[i] if case_isp0 else isp0}
        sets.append({"blk": blk, "kpoke": [f"rd:17=0x{0x300 | s0:x}"]})
    return _probe(name, question, [_pix() for _ in cases_isp2], labels, vertices=6, temps=4,
                  isp2=_isp2(7), case_set=_sets(sets),
                  obj2={"first": 3, "blk": {"1": 0x01d00300 | ref2,
                                            "3": _isp2(cmp2, cmask=cmask2, wmask=0)},
                        "pixel": "pix_blue.s"})


def stencil_probes() -> list[dict]:
    """Q071: ISP word 2's fields. The compare on one object against the background stencil
    (CR_ISP_BGOBJVALS, rd:17); the ops and the write mask through a second object that draws
    where the stencil equals a value."""
    out = []
    s0 = 0x55
    sets, labels = [], []
    for cmp in range(8):
        for ref in (s0 - 1, s0, s0 + 1):
            sets.append({"blk": {1: 0x01d00300 | ref, 3: _isp2(cmp, wmask=0)},
                         "kpoke": [f"rd:17=0x{0x300 | s0:x}"]})
            labels.append(f"SCMP {cmp}, ref 0x{ref:02x} vs 0x{s0:02x}")
    for ref, cm in ((0x05, 0x0f), (0x05, 0xff), (0x50, 0xf0), (0x50, 0x0f)):
        sets.append({"blk": {1: 0x01d00300 | ref, 3: _isp2(2, cmask=cm, wmask=0)},
                     "kpoke": [f"rd:17=0x{0x300 | s0:x}"]})
        labels.append(f"SCMP equal, ref 0x{ref:02x}, SCMP_MASK 0x{cm:02x}")
    for b in (28, 29, 30, 31):
        sets.append({"blk": {1: 0x01d00300 | s0, 3: _isp2(2, wmask=0) | 1 << b},
                     "kpoke": [f"rd:17=0x{0x300 | s0:x}"]})
        labels.append(f"SCMP equal, ref = value, ISP2 bit {b}")
    out.append(_probe("isp-stencil-word-cmp", "ISP word 2's compare and compare mask on one "
                      "object against the background stencil 0x55", [_pix() for _ in sets],
                      labels, isp2=_isp2(7), case_set=_sets(sets)))
    ops = list(range(8))
    for ref in (0x0f, 0x00, 0x55, 0x10, 0x0e, 0xf0):
        out.append(_two(f"isp-stencil-word-sop3-ref-{ref:02x}",
                        f"which depth-pass ops (bits 18:16) leave 0x{ref:02x}, from 0x0f and "
                        "reference 0x55", [_isp2(7, sop3=o) for o in ops],
                        [f"SOP3 {o}" for o in ops], ref))
    for s0w, refs, wops in ((0xff, (0xff, 0x00), (3, 6)), (0x00, (0x00, 0xff), (4, 7))):
        for ref in refs:
            out.append(_two(f"isp-stencil-word-wrap-s{s0w:02x}-ref-{ref:02x}",
                            f"ops {wops} from 0x{s0w:02x}: clamp or wrap",
                            [_isp2(7, sop3=o) for o in wops], [f"SOP3 {o}" for o in wops], ref,
                            s0=s0w))
    for ref in (0x55, 0x0f):
        out.append(_two(f"isp-stencil-word-sop1-ref-{ref:02x}",
                        "replace (2) in each op field with the stencil test failing (never)",
                        [_isp2(0), _isp2(0, sop1=2), _isp2(0, sop2=2), _isp2(0, sop3=2)],
                        ["no op", "SOP1 replace", "SOP2 replace", "SOP3 replace"], ref))
        out.append(_two(f"isp-stencil-word-sop2-ref-{ref:02x}",
                        "replace (2) in each op field with the depth test failing (never)",
                        [_isp2(7), _isp2(7, sop1=2), _isp2(7, sop2=2), _isp2(7, sop3=2)],
                        ["no op", "SOP1 replace", "SOP2 replace", "SOP3 replace"], ref,
                        isp0=0x00000355))
    masks = (0x0f, 0xf0, 0x00, 0xff)
    for ref in (0xf5, 0x50, 0xf0, 0x55):
        out.append(_two(f"isp-stencil-word-swmask-ref-{ref:02x}",
                        f"replace 0x55 over 0xf0 under four write masks: which leave 0x{ref:02x}",
                        [_isp2(7, sop3=2, wmask=m) for m in masks],
                        [f"SW_MASK 0x{m:02x}" for m in masks], ref, s0=0xf0))
    return out


def reg04e8_probes() -> list[dict]:
    """E204: CR_ISP_REG_04E8 (rd:51) at the job's 0x100, 0, 1 and 0x101 under the stencil test
    against the background (equal 0 and equal 1), and under 42 overlapping copies counted by a
    visibility counter, depth always and depth less."""
    vals = (0x100, 0, 1, 0x101)
    out = []
    for run in ("", "-r2"):
        sets, labels = [], []
        for ref in (0, 1):
            for v in vals:
                sets.append({"blk": {1: 0x01d00300 | ref}, "kpoke": [f"rd:51=0x{v:x}"]})
                labels.append(f"equal {ref}, 04e8 0x{v:x}")
        out.append(_probe(f"isp-reg-04e8-stencil{run}", "0x04e8 under the stencil test against "
                          "the background stencil", [_pix() for _ in sets], labels,
                          isp2=_isp2(2, wmask=0), case_set=_sets(sets)))
        sets, labels = [], []
        for isp0, name in ((ISP0_JOB, "always"), (0x00400200, "less")):
            for v in vals:
                sets.append({"blk": {1: isp0, 2: 0x10f8}, "kpoke": [f"rd:51=0x{v:x}"]})
                labels.append(f"42 copies, depth {name}, 04e8 0x{v:x}")
        out.append(_probe(f"isp-reg-04e8-many{run}", "0x04e8 under 42 overlapping copies, the "
                          "visibility counter on", [_PA0 for _ in sets], labels,
                          case_set=_sets(sets), **dict(_COPIES, vertices=126)))
    return out


ISP_CTL_JOB = 0x000f0100


def ispctl_probes() -> list[dict]:
    """CR_ISP_CTL (rd:3) bits 24, 19:16 and 8 flipped from the job's 0x000f0100, and 0, on the
    triangle at 64x64, 96x64, 128x128 and 256x128 (Q029: untouched tiles with bit 8 clear)."""
    vals = [ISP_CTL_JOB, ISP_CTL_JOB ^ 0x100, ISP_CTL_JOB ^ 1 << 24] + \
        [ISP_CTL_JOB ^ 1 << b for b in (16, 17, 18, 19)] + [0]
    out = []
    for w, h in ((64, 64), (96, 64), (128, 128), (256, 128)):
        out.append(_probe(f"isp-isp-ctl-{w}x{h}", f"CR_ISP_CTL's bits on a {w}x{h} target",
                          [_pix() for _ in vals], [f"CR_ISP_CTL 0x{v:08x}" for v in vals],
                          size=[w, h], case_set=_sets([{"kpoke": [f"rd:3=0x{v:x}"]}
                                                       for v in vals])))
    return out


def reg04dc_probes() -> list[dict]:
    """Q072: CR_ISP_REG_04DC (rd:21) bit 1 on opaque and translucent copies, depth less with
    writes, the visibility counter on."""
    sets, labels = [], []
    for isp0, name in ((0x00400200, "opaque"), (0x02400200, "translucent")):
        for v in (0, 2):
            sets.append({"blk": {1: isp0, 2: 0x10f8}, "kpoke": [f"rd:21=0x{v:x}"]})
            labels.append(f"{name}, 04dc 0x{v:x}")
    return [_probe(f"isp-reg-04dc-depth-{run}", "0x04dc bit 1 on opaque and translucent copies "
                   "with depth less", [_PA0 for _ in sets], labels, case_set=_sets(sets),
                   **_COPIES) for run in ("r1", "r2")]


def translucent_probes() -> list[dict]:
    """Q073: a translucent (pass type 1) and an opaque triangle whose shader writes a constant
    without reading o0, passes o0 on, or changes o0 with an or."""
    ops = [_pix(), ["mov.skipinv.end o0, o0"], ["or.skipinv.end o0, o0, #0x000000FF"]]
    names = ["a constant", "o0", "o0 | 0xff"]
    sets, labels, cases = [], [], []
    for isp0, kind in ((ISP0_JOB | 1 << 25, "translucent"), (ISP0_JOB, "opaque")):
        for op, n in zip(ops, names):
            cases.append(op)
            sets.append({"blk": {1: isp0}})
            labels.append(f"{kind}, {n}")
    return [_probe(f"isp-translucent-blend-{run}", "whether anything after the shader blends "
                   "in a translucent pass", cases, labels, case_set=_sets(sets))
            for run in ("r1", "r2")]


def scene_probes() -> list[dict]:
    """E169: one kick's objects: two and five triangles in one object, and two objects."""
    return [_probe("render-kick-objects-tris2", "one object of two triangles", [_pix()],
                   ["two triangles"], vertices=6, dump_render=True),
            _probe("render-kick-objects-tris5", "one object of five triangles", [_pix()],
                   ["five triangles"], vertices=15, dump_render=True),
            _probe("render-kick-objects-obj2", "two objects in one kick", [_pix()],
                   ["two objects"], vertices=6, obj2={"first": 3, "pixel": "pix_blue.s"},
                   dump_render=True)]


def tables() -> dict[str, str]:
    """{"<unit>/<feature>": table text} of the 11.6 probe tables."""
    return {
        "isp/coverage-samples": table_text(
            "isp", "coverage samples", "ISP0 bit 28 against 0x04c8 and 0x0520 (Q031).",
            coverage_probes()),
        "isp/coverage-bytes": table_text(
            "isp", "coverage bytes", "the nibble order of 0x04c8's bytes 1-3 (Q031).",
            coverage_byte_probes()),
        "isp/msaa-layout": table_text(
            "isp", "msaa layout", "CR_ISP_MSAA modes over a known edge; bit 31 (Q030).",
            layout_probes()),
        "isp/msaa-positions": table_text(
            "isp", "msaa positions", "which register places the 4x samples (Q030).",
            msaa_position_probes()),
        "isp/msaa-te": table_text(
            "isp", "msaa te", "the TE anti-aliasing bits under modes 0-2 (Q030).",
            msaa_te_probes()),
        "isp/tag-write": table_text(
            "isp", "tag write", "ISP0 bit 21 and the depth it writes.", tagwrite_probes()),
        "isp/line-sample": table_text(
            "isp", "line sample", "0x0418 and the line's end pixels; line width (E181, E202).",
            line_probes()),
        "isp/line-bias": table_text(
            "isp", "line bias", "0x0418 against the polygon offset (E202).",
            line_bias_probes()),
        "isp/depth-compare": table_text(
            "isp", "depth compare", "ISP0's depth compare and write bits; its other bits.",
            depth_probes()),
        "isp/stencil-word": table_text(
            "isp", "stencil word", "ISP word 2: compare, masks and ops (Q071).",
            stencil_probes()),
        "isp/reg-04e8": table_text(
            "isp", "reg 04e8", "0x04e8 under the stencil test and many objects (E204).",
            reg04e8_probes()),
        "isp/isp-ctl": table_text(
            "isp", "isp ctl", "CR_ISP_CTL bits 24, 19:16 and 8 on four target sizes (Q029).",
            ispctl_probes()),
        "isp/reg-04dc-depth": table_text(
            "isp", "reg 04dc depth", "0x04dc bit 1 with depth less (Q072).", reg04dc_probes()),
        "isp/translucent-blend": table_text(
            "isp", "translucent blend", "the translucent pass and o0 (Q073).",
            translucent_probes()),
        "render/kick-objects": table_text(
            "render", "kick objects", "objects over one to three kicks, and in one kick (E169).",
            scene_probes(), needs=("render",),
            head={"name": "render-kick-objects", "script": "kick-objects.sh"}),
        "mte/clip-plane1": table_text(
            "mte", "clip plane1", "user clip plane 1 and 2 alone (Q039).", clip_probes(),
            needs=("render",)),
        "mte/clip-plane-state": table_text(
            "mte", "clip plane state", "the planes' state across jobs (Q039).",
            clip_state_probes(), needs=("render",)),
        "mte/clip-plane-dist": table_text(
            "mte", "clip plane dist", "the distance dwords once the state is set (Q039).",
            clip_dist_probes(), needs=("render",)),
        "mte/outsel-bits": table_text(
            "mte", "outsel bits", "OUTSEL bits 13:12 with zero, one and two sets (Q069).",
            outsel_probes(), needs=("render",)),
        "mte/depth-range2": table_text(
            "mte", "depth range2", "depths outside [0, 1], again; the clamp (Q069).",
            depth_range2_probes(), needs=("render",)),
        "mte/presence-high": table_text(
            "mte", "presence high", "the presence word's bits 16-31 (Q069).",
            presence_probes(), needs=("render",)),
        "mte/depth-range": table_text(
            "mte", "depth range", "depths outside [0, 1] (Q069). The data's clip probe ran "
            "with vtx_zab.s\n# naming #10 as its second phase and hung (E287); depth-range2 "
            "reruns it with #11.", depth_range_probes(),
            needs=("render",)),
    }


# ---- the command line -------------------------------------------------------------------------

def _meta(table: pathlib.Path, name: str) -> dict:
    for p in tomllib.loads(table.read_text()).get("probe", []):
        if p["name"] == name:
            return p
    raise IspError(f"{name}: not in {table}")


def _size(p: dict) -> tuple[int, int]:
    return tuple(p.get("size", [64, 64]))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("decode")
    d.add_argument("word")
    d.add_argument("value")
    t = sub.add_parser("table")
    t.add_argument("out")
    for name in ("rules", "layout", "lines", "copies", "counts"):
        e = sub.add_parser(name)
        e.add_argument("raw")
        e.add_argument("probe")
        e.add_argument("table")
        if name == "layout":
            e.add_argument("--joint", action="store_true",
                           help="one fit over every case, inside the binned tiles")
    u = sub.add_parser("unpack")
    u.add_argument("output")
    u.add_argument("out")
    a = ap.parse_args(argv)
    if a.cmd == "decode":
        for k, v in decode(a.word, int(a.value, 0)).items():
            print(f"{k} = 0x{v:x}")
        return 0
    if a.cmd == "table":
        for rel, text in tables().items():
            p = pathlib.Path(a.out) / f"{rel}.toml"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
        return 0
    if a.cmd == "unpack":
        for f in pb_unpack(pathlib.Path(a.output).read_text(), pathlib.Path(a.out)):
            print(f)
        return 0
    p = _meta(pathlib.Path(a.table), a.probe)
    w, h = _size(p)
    img, fail = case_images(pathlib.Path(a.raw).read_text(), a.probe)
    sets = p.get("case_set", [{}] * len(p["labels"]))
    if a.cmd == "layout" and a.joint:
        cases = [(img[i], affine_target(4, 4, 10, int(lab.split("=")[1])))
                 for i, lab in enumerate(p["labels"]) if i in img]
        for r in fit_layout_joint(cases, w, h)[:3]:
            print(f"{r['layout'][0]}x{r['layout'][1]}: miss {r['mismatch']}; " + "; ".join(
                f"slot {k}: miss {n} at " + " ".join(f"({x},{y})" for x, y in pos[:6]) +
                (f" (+{len(pos) - 6})" if len(pos) > 6 else "")
                for k, (n, pos) in enumerate(r["slots"])))
        return 0
    for i, label in enumerate(p["labels"]):
        if i in fail or i not in img:
            print(f"{label}: {fail.get(i, 'not run')}")
            continue
        im = img[i]
        if a.cmd == "rules":
            m = sets[i].get("cmd", {}).get("16", 0x88)
            s = int(next((k.split("=")[1] for k in sets[i].get("kpoke", [])
                          if k.startswith("rd:19=")), "0"), 0)
            fit = fit_rules(im, m, s, w, h)
            print(f"{label}: {sum(1 for v in im if v == GREEN)} pixels; " +
                  ", ".join(f"{r} {n}" for r, n in fit.items()))
        elif a.cmd == "layout":
            vals = [float_of(int(v, 16)) for v in p["cases"][i]]
            k = int(label.split("=")[1])
            tri = affine_target(4, 4, 10, k)
            assert all(abs(x - y) < 1e-4 for x, y in zip(vals, affine_params(tri, w, h)))
            best = fit_layout(im, tri, w, h)[:3]
            print(f"{label}: {sum(1 for v in im if v == GREEN)} pixels; " + "; ".join(
                f"{r['layout'][0]}x{r['layout'][1]} miss {r['mismatch']} at " +
                " ".join(f"({x},{y})" for x, y in r["samples"]) for r in best))
        elif a.cmd == "lines":
            sp = spans(im, w, GREEN)
            miss = ""
            if p.get("vdm", {}).get("2") == LINE:
                blk, pos, lw = line_setting({"blk": {**p.get("blk", {}),
                                                     **sets[i].get("blk", {})},
                                             "kpoke": sets[i].get("kpoke", [])})
                got = {(j % w, j // w) for j, v in enumerate(im) if v == GREEN}
                miss = f"; model miss {len(got ^ line_cover(line_ends(blk, w, h), pos, lw))}"
            print(f"{label}: {sum(n for *_x, n in sp.values())} pixels; " +
                  " ".join(f"y{y}:{x0}-{x1}" for y, (x0, x1, _n) in sorted(sp.items())) + miss)
        elif a.cmd == "copies":
            c = collections.Counter(copy_of(v) for v in im)
            print(f"{label}: " + ", ".join(f"{'bg' if k is None else f'copy {k}'} {n}"
                                           for k, n in sorted(c.items(),
                                                              key=lambda x: (x[0] is None,
                                                                             x[0] or 0))))
        else:
            c = collections.Counter(im)
            print(f"{label}: " + ", ".join(f"0x{v:08x} x{n}" for v, n in c.most_common(5)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
