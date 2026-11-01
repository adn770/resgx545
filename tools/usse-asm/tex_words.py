#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The texture words T0-T3 by glossary name, the 11.5 texture tables, and the models the copy
runs are read against.

FIELDS names each word's fields as the glossary does (T0 of a strided texture, TEXTYPE 6,
has T0.STRIDE where a twiddled one has its filter and mipmap fields: decode(strided=True));
T0.MAX_LEVEL (20:17) stands for the older rows T0.BITS20_19 and T0.NO_MIPMAPS, its parts.
decode() keeps the bits outside every field as `<WORD>.rest`. copy_words() gives the copy's
four words as libsgxfive builds them, source() its source texels, csc() and yuv_image() the
colour-space conversion E037 fitted, and Band the luma-key model of E039 with the low end of
E275's band, with cuts(), the cut-point fitter (for one image, the luma, the weighted sum
shifted by 10, at which the alpha changes, and whether one threshold separates the two alphas)
and band_misfits(), the band model against each copy of the luma-cuts script.

The tables (probes/texture/):

  mip-fields   T0 bits 20:17 (all 16 values, LOD 1 to 4) and bits 26:21 (all 64, LOD 2 and 4)
               on the tagged mip chain of mipmaps.toml's mip-t0-field probe (Q009);
  fetch-size   T3 bits 26:23 at 8 and 15 in a two-fetch primary program (E242's open values).

    tex_words.py decode WORD VALUE [--strided]   the fields of T0-T3
    tex_words.py table DIR                       write the tables into DIR (probes/texture/)
    tex_words.py cuts OUTPUT W0 W1 W2            per section of a copy script's output: the
                                                 luma-key cut points against the words
    tex_words.py band OUTPUT W0 W1 W2 [--round R ...]  per section, the pixels the band model
                                                 does not give (the section's label "low L
                                                 threshold T" sets W2's bytes 1 and 0); the
                                                 low cut read as (S + R) >> 10
"""
from __future__ import annotations

import argparse
import dataclasses
import pathlib
import re
import struct
import sys
import tomllib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MIPMAPS = ROOT / "probes" / "texture" / "mipmaps.toml"

FIELDS = {
    "T0": [("ALPHA_FROM_LUMA_KEY", 31, 31), ("BIT30", 30, 30), ("BIT27", 27, 27),
           ("BITS26_21", 26, 21), ("MAX_LEVEL", 20, 17), ("MAGFILTER", 13, 12),
           ("MINFILTER", 11, 10), ("MIPFILTER", 9, 9), ("ADDRMODE_U", 8, 6),
           ("ADDRMODE_V", 5, 3)],
    "T1": [("TEXTYPE", 31, 29), ("TEXFORMAT", 28, 24), ("WIDTH", 23, 12), ("HEIGHT", 11, 0)],
    "T2": [("TEXADDR", 31, 2)],
    "T3": [("CMP_MODE", 31, 29), ("BITS28_27", 28, 27), ("DATA_SIZE", 26, 23),
           ("BITS19_18", 19, 18), ("CONVERT", 17, 16), ("NORMALIZE", 15, 15), ("BIT14", 14, 14),
           ("BIT10", 10, 10), ("BITS7_0", 7, 0)],
}
# T0 of a strided texture: the stride in place of the filter and mipmap fields
STRIDED_T0 = [("ALPHA_FROM_LUMA_KEY", 31, 31), ("BIT30", 30, 30), ("BIT27", 27, 27),
              ("MAGFILTER", 13, 12), ("ADDRMODE_U", 8, 6), ("ADDRMODE_V", 5, 3)]
STRIDE_MASK = 0x07fe0e00            # T0.STRIDE: [11:9] and [26:17]
# Colour-space set 0 as E037 reads the limited-range BT.601 words, in 128ths: the Y weight, R
# from V, G from U and from V, B from U.
BT601 = (149, 204, -50, -104, 258)
LODS = (1.0, 2.0, 3.0, 4.0)


class TexError(Exception):
    pass


def _mask(hi: int, lo: int) -> int:
    return (1 << (hi + 1)) - (1 << lo)


def decode(word: str, value: int, strided: bool = False) -> dict:
    """{glossary name: field value} of one texture word, and `<word>.rest`."""
    if word not in FIELDS:
        raise TexError(f"no word {word}: one of {', '.join(FIELDS)}")
    fields = STRIDED_T0 if (word == "T0" and strided) else FIELDS[word]
    out, rest = {}, value
    for name, hi, lo in fields:
        out[f"{word}.{name}"] = (value & _mask(hi, lo)) >> lo
        rest &= ~_mask(hi, lo)
    if word == "T0" and strided:
        out["T0.STRIDE"] = (value >> 9 & 7) | (value >> 17 & 0x3ff) << 3
        rest &= ~STRIDE_MASK
    out[f"{word}.rest"] = rest
    return out


def copy_words(width: int, height: int, addr: int, stride: int) -> list[int]:
    """T0-T3 of the copy's source (sgxfive_tex_words): strided B8G8R8A8, point sampling."""
    s = stride // 4 - 1
    return [(s & 7) << 9 | (s >> 3) << 17, 0xcc000000 | (width - 1) << 12 | (height - 1),
            addr & ~3, 0xa0800000]


def source(x: int, y: int, width: int, every: bool = False) -> int:
    """The copy's source texel (x, y) of a source width texels wide (sgxfive-test pattern())."""
    n = (y * width + x) & 0xff
    if every:
        return n << 24 | ((n * 167 + 13) & 0xff) << 16 | ((n * 29 + 101) & 0xff) << 8 | \
            ((n * 93 + 57) & 0xff)
    return 0xa5000000 | (y & 0xff) << 16 | (x & 0xff) << 8 | ((x ^ y) & 0xff)


def source_bytes(width: int, height: int, every: bool = False) -> bytes:
    return b"".join(struct.pack("<I", source(x, y, width, every))
                    for y in range(height) for x in range(width))


def _sat(v: int) -> int:
    return max(0, min(255, v))


def csc(y: int, u: int, v: int, c: tuple = BT601, offset: bool = True) -> tuple:
    """(R, G, B) of one texel as E037 fitted set 0 (arithmetic shift, saturated)."""
    cy, rv, gu, gv, bu = c
    yy = (y - 16) if offset else y
    return (_sat((cy * yy + rv * (v - 128)) >> 7), _sat((cy * yy + gu * (u - 128) +
                                                         gv * (v - 128)) >> 7),
            _sat((cy * yy + bu * (u - 128)) >> 7))


def pack(rgb: tuple) -> int:
    return rgb[0] << 16 | rgb[1] << 8 | rgb[2]


def yuv_image(src: bytes, width: int, height: int, stride: int, order: str,
              c: tuple = BT601) -> list[int]:
    """The ARGB image of a 4:2:2 source read at `stride` bytes a row, pairs of texels in four
    bytes (order YUYV or UYVY), converted as csc(), alpha 0xff."""
    out = []
    for y in range(height):
        for x in range(width):
            b = src[y * stride + (x // 2) * 4:][:4]
            if order == "YUYV":
                lum, u, v = (b[0] if x % 2 == 0 else b[2]), b[1], b[3]
            elif order == "UYVY":
                lum, u, v = (b[1] if x % 2 == 0 else b[3]), b[0], b[2]
            else:
                raise TexError(f"order {order}: YUYV or UYVY")
            out.append(0xff000000 | pack(csc(lum, u, v, c)))
    return out


@dataclasses.dataclass(frozen=True)
class Band:
    """The three luma-key words of E039's model: weights in 1024ths, an offset in halves,
    a threshold, the two alphas, and the low byte of the third word, the band's low end
    (E275)."""
    wr: int
    wg: int
    wb: int
    offset: int
    threshold: int
    below: int
    above: int
    low: int

    @classmethod
    def of(cls, words: tuple) -> "Band":
        w0, w1, w2 = words
        return cls(w0 & 0x3ff, w0 >> 16 & 0x3ff, w1 & 0x3ff, w1 >> 16 & 0xff, w2 >> 8 & 0xff,
                   w2 >> 16 & 0xff, w2 >> 24 & 0xff, w2 & 0xff)

    def sum(self, r: int, g: int, b: int) -> int:
        """S, the weighted sum: the luma in 1024ths."""
        return self.wr * r + self.wg * g + self.wb * b + 512 * self.offset

    def luma(self, r: int, g: int, b: int) -> int:
        return self.sum(r, g, b) >> 10

    def alpha(self, r: int, g: int, b: int, round_low: int = 0) -> int:
        """alpha_below where low <= (S + round_low) >> 10 and S >> 10 <= threshold, else
        alpha_above (E275's band; round_low the rounding fitted at the low cut)."""
        s = self.sum(r, g, b)
        inside = self.low <= (s + round_low) >> 10 and s >> 10 <= self.threshold
        return self.below if inside else self.above


def cuts(pix: list[int], key: Band) -> dict:
    """The alphas of an ARGB image against the luma of each pixel's RGB: the runs of one alpha
    over increasing luma (alpha, first luma, last luma; alpha None where one luma holds two
    alphas), whether one cut separates two alphas (monotone), and that cut."""
    by: dict[int, set] = {}
    for p in pix:
        lum = key.luma(p >> 16 & 0xff, p >> 8 & 0xff, p & 0xff)
        by.setdefault(lum, set()).add(p >> 24)
    runs: list[list] = []
    for lum in sorted(by):
        a = next(iter(by[lum])) if len(by[lum]) == 1 else None      # None: both at one luma
        if runs and runs[-1][0] == a:
            runs[-1][2] = lum
        else:
            runs.append([a, lum, lum])
    alphas = sorted({a for s in by.values() for a in s})
    out = {"runs": [tuple(r) for r in runs], "alphas": alphas,
           "monotone": len(runs) <= 2 and all(r[0] is not None for r in runs)}
    if len(runs) == 2 and out["monotone"]:
        out.update(below=runs[0][0], above=runs[1][0], last_below=runs[0][2],
                   first_above=runs[1][1])
    elif len(runs) == 1:
        out.update(below=runs[0][0], above=runs[0][0], last_below=None, first_above=None)
    return out


def band_misfits(text: str, words: tuple, round_low: int = 0) -> dict[str, int]:
    """{label: pixels whose alpha the band model does not give} for each section of a copy
    script's output that has pixels; a label "low L threshold T" sets the third word's bits
    7:0 and 15:8 (the luma-cuts script's sections), others keep `words`."""
    w0, w1, w2 = words
    out = {}
    for label, pix in sections(text).items():
        if not pix:
            continue
        m = re.match(r"low (\d+) threshold (\d+)", label)
        key = Band.of((w0, w1, w2 & ~0xffff | int(m[2]) << 8 | int(m[1])) if m else words)
        out[label] = sum(p >> 24 != key.alpha(p >> 16 & 0xff, p >> 8 & 0xff, p & 0xff,
                                              round_low) for p in pix)
    return out


def sections(text: str) -> dict[str, list[int]]:
    """{label: pixels} of a script's output: `#### label` starts a section, `row Y: ...`
    lines hold its pixels (none if the job failed)."""
    out: dict[str, list[int]] = {}
    cur = None
    for line in text.splitlines():
        if line.startswith("#### "):
            cur = line[5:].strip()
            out[cur] = []
        elif cur is not None:
            m = re.match(r"row \d+:((?: 0x[0-9a-f]{8})*)$", line)
            if m:
                out[cur] += [int(v, 16) for v in m[1].split()]
    return out


def _f32(v: float) -> int:
    return struct.unpack("<I", struct.pack("<f", v))[0]


MIP_TEMPLATE = "mip_chain.s"


def _mip_base(table: pathlib.Path) -> dict:
    d = tomllib.loads(table.read_text())
    (base,) = [p for p in d["probe"] if p["name"].endswith("mip-t0-field")]
    op = base["cases"][0][0]
    if "mov r20, #0x07FA0000" not in op or "mov r26, #0x40000000" not in op:
        raise TexError("mip-t0-field's case 0 no longer sets T0 in r20 and the LOD in r26")
    return base


def mip_template(table: pathlib.Path = MIPMAPS) -> str:
    """dump.s with mip-t0-field's case 0 as its OP, T0 (r20) and the LOD (r26) as inputs."""
    base = _mip_base(table)
    dump = (table.parent / "templates" / base["source"]).read_text()
    op = base["cases"][0][0].replace("mov r20, #0x07FA0000", "mov r20, #{T0}") \
        .replace("mov r26, #0x40000000", "mov r26, #{LOD}")
    body = [line for line in dump.splitlines() if not line.startswith(";")]
    head = ["; SPDX-License-Identifier: MIT", "; SPDX-FileCopyrightText: 2026 Josep Torra",
            "; The mip-field probes (tex_words.py): dump.s with the case of mipmaps.toml's",
            "; mip-t0-field probe as its OP, a tagged 16x16 chain of five levels written to the",
            "; scratch buffer and read by smp2dreplace with T0 {T0} in r20 and the LOD {LOD} (an",
            "; IEEE single) in r26; the result in r10 is the pixel."]
    return "\n".join(head + body).replace("{OP}", op) + "\n"


def mip_probes(table: pathlib.Path = MIPMAPS) -> list[dict]:
    """T0 (r20) and the LOD (r26) of mip-t0-field varied, through mip_template()."""
    base = _mip_base(table)
    keep = {"source": MIP_TEMPLATE, "params": base["params"], "inputs": ["T0", "LOD"]}
    p1 = {"name": "texture-mip-fields-bits20-17",
          "question": "which level each value of T0 bits 20:17 reads at LOD 1 to 4, bits 26:21 "
                      "at 0x3f (the level tags of mip-t0-field)", **keep,
          "labels": [f"20:17 = 0x{v:x}, LOD {lod}" for v in range(16) for lod in LODS],
          "cases": [[0x3f << 21 | v << 17, _f32(lod)] for v in range(16) for lod in LODS]}
    p2 = {"name": "texture-mip-fields-bits26-21",
          "question": "which level each value of T0 bits 26:21 reads at LOD 2 and 4, bits 20:17 "
                      "at 0xd", **keep,
          "labels": [f"26:21 = 0x{v:02x}, LOD {lod}" for v in range(64) for lod in (2.0, 4.0)],
          "cases": [[v << 21 | 0xd << 17, _f32(lod)] for v in range(64) for lod in (2.0, 4.0)]}
    return [p1, p2]


def fetch_probes() -> list[dict]:
    """Two fetches (pds_tex2.s) with the first's T3 bits 26:23 at 1, 8 and 15, as fetched and
    as f32 channels at 8; the second texel looked for in pa1, pa8 and pa15."""
    a, b = 0x06012201, 0x46012201
    ts = [(1, 0), (8, 0), (15, 0), (8, 3)]
    labels = [f"first {'as fetched' if c == 0 else 'as f32 channels'}, 26:23 = {f}"
              for f, c in ts]
    cases = [[a, b, f << 23 | c << 16 | 0x800] for f, c in ts]
    return [{"name": f"texture-fetch-size-pa{n}",
             "question": f"pa{n} after two fetches, the first's T3 26:23 at 1, 8 and 15",
             "source": "pds_tex2.s", "host": "tri", "slot": "pixpds",
             "slots": {"pixel": f"pix_pa{n}.s", "vtxuse": "vtx_coords.s"}, "vtx_coords": 2,
             "size": [64, 64], "pixels": True, "inputs": ["A", "B", "T"], "labels": labels,
             "cases": cases} for n in (1, 8, 15)]


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
    raise TexError(f"no TOML for {v!r}")


def table_text(title: str, about: str, ps: list[dict]) -> str:
    head = ["# SPDX-License-Identifier: MIT", "# SPDX-FileCopyrightText: 2026 Josep Torra",
            f"# texture {title}: 0 sweeps, {len(ps)} probes (written by "
            "tools/usse-asm/tex_words.py).", f"# {about}", 'needs = ["render"]']
    body = []
    for p in ps:
        body.append("\n[[probe]]")
        body += [f"{k} = {_toml(v)}" for k, v in p.items()]
    return "\n".join(head + body) + "\n"


def tables() -> dict[str, str]:
    return {"mip-fields": table_text("mip fields", "T0 bits 20:17 and 26:21 on the mip chain "
                                     "(Q009).", mip_probes()),
            "fetch-size": table_text("fetch size", "T3 bits 26:23 at 8 and 15 (E242).",
                                     fetch_probes())}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("decode")
    d.add_argument("word")
    d.add_argument("value")
    d.add_argument("--strided", action="store_true")
    t = sub.add_parser("table")
    t.add_argument("out")
    c = sub.add_parser("cuts")
    c.add_argument("output")
    c.add_argument("words", nargs=3)
    b = sub.add_parser("band")
    b.add_argument("output")
    b.add_argument("words", nargs=3)
    b.add_argument("--round", type=int, nargs="+", default=[0])
    a = ap.parse_args(argv)
    if a.cmd == "decode":
        for k, v in decode(a.word, int(a.value, 0), a.strided).items():
            print(f"{k} = 0x{v:x}")
    elif a.cmd == "table":
        for name, text in tables().items():
            (pathlib.Path(a.out) / f"{name}.toml").write_text(text)
    if a.cmd == "table":
        (pathlib.Path(a.out) / "templates" / MIP_TEMPLATE).write_text(mip_template())
    if a.cmd == "cuts":
        key = Band.of(tuple(int(w, 0) for w in a.words))
        for label, pix in sections(pathlib.Path(a.output).read_text()).items():
            if not pix:
                print(f"{label}: no pixels")
                continue
            cut = cuts(pix, key)
            runs = " ".join(("mixed" if al is None else f"0x{al:02x}") + f"@{lo}-{hi}"
                            for al, lo, hi in cut["runs"])
            print(f"{label}: {'monotone' if cut['monotone'] else 'not monotone'}: {runs}")
    if a.cmd == "band":
        text = pathlib.Path(a.output).read_text()
        words = tuple(int(w, 0) for w in a.words)
        for r in a.round:
            bad = {k: n for k, n in band_misfits(text, words, r).items() if n}
            n = len(band_misfits(text, words, r))
            print(f"round {r}: {n - len(bad)} of {n} copies fit" +
                  "".join(f"; {k}: {v} pixels" for k, v in bad.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
