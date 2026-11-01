#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Write the 3D capture tables from the variation lists: for each list of TABLES,
captures/<unit>/<feature>.toml (kind = "capture", for the private data repository) and its
template captures/<unit>/templates/<feature>.sh, which runs capture3d_host.sh on the capture
host with the list (README "3D capture"). The table's files are the harness sources the host
builds, capture3d.sh, capture3d_host.sh and the list (and gen_shaders3d.py for every list
that names its shader files); `open` names the runs of a list no earlier capture recorded.

    cap3d_tables.py [--check] [ROOT [OUT]]   write (or check) the tables of ROOT's lists
                                             under OUT/captures (OUT defaults to ROOT)
"""
from __future__ import annotations

import pathlib
import sys
import textwrap

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HARNESS = "harness/ukernel-extract"
HEADER = "# SPDX-License-Identifier: MIT\n# SPDX-FileCopyrightText: 2026 Josep Torra\n"
GENERATED = "# Written by harness/ukernel-extract/cap3d_tables.py from {list}; do not edit.\n"
SOURCES = ("fakedrm.c", "loader.c", "fakewsegl.c", "tri.c", "tri1.c", "triopts.h",
           "tri1opts.h", "ukdir.h", "bridgecmd.h", "devmem.h", "bufclass.h", "capture3d.sh",
           "capture3d_host.sh")


# (unit, feature, list, what the table captures, list runs never captured before)
TABLES = [
    ("render", "state-variations", "variations3d.txt",
     "one piece of GL state per run against base", False),
    ("render", "register-gaps", "gaps3d.txt",
     "the render-details registers the state variations leave alone: polygon offset, "
     "multisampled render to texture, a depth buffer reloaded", False),
    ("render", "draws-frames-pb", "track3d.txt",
     "several draws, flushes and frames, depth and stencil kept in memory, parameter "
     "buffer sizes", True),
    ("isp", "registers", "isp3d.txt",
     "translucency over depth, discard, overlapping draws, alpha to coverage and sample "
     "coverage under 4x multisampling, wide lines and hints", False),
    ("isp", "line-width", "lines3d.txt", "line and point widths 1 to 15", False),
    ("ta", "target-sizes", "sizes3d.txt", "render-target sizes 1x1 to 4096x4096", False),
    ("texture", "textures", "textures3d.txt",
     "textures, mipmaps and render to texture", False),
    ("texture", "samplers", "samplers3d.txt", "one filter or one axis's wrap per run", False),
    ("texture", "formats", "formats3d.txt", "texture formats, 16x16 each", False),
    ("texture", "streams", "streams3d.txt",
     "YUV texture streams through the buffer-class device", False),
    ("usse", "shaders", "shaders3d.txt", "one GLSL ES shader per feature", False),
    ("usse", "inputs", "inputs3d.txt", "uniform values and vertex attribute layouts", False),
    ("usse", "gles1-programs", "gles1_3d.txt", "GLES1 fixed-function state, with tri1", False),
]


def runs(text: str) -> list[str]:
    """The run names of a variation list, in order."""
    return [ln.split()[0] for ln in text.splitlines() if ln.strip() and not ln.lstrip()
            .startswith("#")]


def files(lst: str, list_text: str = "") -> list[str]:
    """The repository files a table copies to the capture host; a list that names shader
    files (shaders/) brings their generator."""
    out = [f"{HARNESS}/{s}" for s in SOURCES] + [f"{HARNESS}/{lst}"]
    if "shaders/" in (list_text or (HERE / lst).read_text()):
        out.append(f"{HARNESS}/gen_shaders3d.py")
    return out


def _list(xs: list[str], indent: int = 8) -> str:
    """A TOML array of strings, wrapped under 100 columns."""
    lines, cur = [], "["
    for i, x in enumerate(xs):
        item = f'"{x}"' + ("," if i < len(xs) - 1 else "]")
        if len(cur) + len(item) + 1 > 100 - indent and cur != "[":
            lines.append(cur.rstrip())
            cur = " " * indent
        cur += item + " "
    lines.append(cur.rstrip())
    return "\n".join(lines)


def table(unit: str, feature: str, lst: str, about: str, new: bool,
          list_text: str) -> tuple[str, str]:
    """(table text, template script text) of one capture table."""
    gen = GENERATED.format(list=lst)
    t = [HEADER.rstrip("\n"), gen.rstrip("\n"),
         *textwrap.wrap(f"The closed GLES stacks under the harness, {lst}: {about}.", 98,
                        initial_indent="# ", subsequent_indent="# "),
         'kind = "capture"', f'name = "{unit}-{feature}"', 'host = "build"',
         f'script = "{feature}.sh"', "files = " + _list(files(lst, list_text), 9)]
    if new:
        t.append("# the runs no earlier capture recorded")
        t.append("open = " + _list([r for r in runs(list_text) if r != "base"], 8))
    script = (HEADER + gen + f"# Run {lst} under the harness; capture3d_host.sh says how.\n"
              f"set -eu\nexec sh ./capture3d_host.sh {lst}\n")
    return "\n".join(t) + "\n", script


def render(root: pathlib.Path = ROOT) -> dict[str, str]:
    """{path under root: text} of every table and template."""
    out = {}
    for unit, feature, lst, about, new in TABLES:
        tt, sh = table(unit, feature, lst, about, new,
                       (root / HARNESS / lst).read_text())
        out[f"captures/{unit}/{feature}.toml"] = tt
        out[f"captures/{unit}/templates/{feature}.sh"] = sh
    return out


def main(argv: list[str]) -> int:
    check = "--check" in argv
    args = [a for a in argv if a != "--check"]
    root = pathlib.Path(args[0]) if args else ROOT
    out = pathlib.Path(args[1]) if len(args) > 1 else root
    stale = []
    for rel, text in render(root).items():
        p = out / rel
        if check:
            if not p.exists() or p.read_text() != text:
                stale.append(rel)
        else:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
    for rel in stale:
        print(f"cap3d_tables.py: {rel} differs from its list", file=sys.stderr)
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
