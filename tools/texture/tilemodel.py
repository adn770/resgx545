# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""tilemodel.py: the 11.32 sampler model (tools/texture/p1132/recompute/texmodel.py, the same
bytes as resgx545-data texture/p1141/support/texmodel.py, sha256 ffa41eb9...) with the twiddled
address of E561: tiles of min(W, 16) x min(H, 16) texels, each the plain interleave (y in bit 0),
the tiles in raster order x first. texmodel.py addresses a twiddled texture by plain Morton order
over the whole side, which E561 found wrong when both sides are above 16 (r13-tex: E564's
an-t3b11 differs at pixel 16); neither copy of it is changed (11.32's declared predictions and
the published p1141 batch are frozen on it).

The model is a private copy of texmodel.py loaded from its file, its `morton` replaced by
tile_index; the module texmodel imported elsewhere is not touched. Use it as texmodel:
`tilemodel.tm.render(spec)`, `tilemodel.tm.Tex(...)`, `tilemodel.tm.ev(...)`. Standard library
only."""
import importlib.util
import pathlib
import sys

TEXMODEL = pathlib.Path(__file__).resolve().parent / "p1132/recompute/texmodel.py"


def _load():
    spec = importlib.util.spec_from_file_location("texmodel_tiles", TEXMODEL)
    m = importlib.util.module_from_spec(spec)
    sys.modules["texmodel_tiles"] = m       # dataclass-free, but kept findable by its name
    spec.loader.exec_module(m)
    return m


tm = _load()
plain = tm.morton           # the plain interleave over the whole side (texmodel's order)


def tile_index(x, y, w, h):
    """E561's twiddled index: tiles of min(w, 16) x min(h, 16), each the plain interleave, the
    tiles in raster order x first; equal to the plain order up to 16 a side."""
    tw, th = min(w, 16), min(h, 16)
    return plain(x % tw, y % th, tw, th) + tw * th * (x // tw + (w // tw) * (y // th))


tm.morton = tile_index
