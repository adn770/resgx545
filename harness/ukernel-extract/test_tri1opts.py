# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Tests for tri1opts.h: the options of tri1.c, the GLES1 (fixed-function) sibling of tri.c.

tri1.c only builds as a 32-bit Linux program against the closed libGLES_CM, so its argument
parsing lives in tri1opts.h and is checked here through a host program that prints the
parsed state (tri1_dump). Each option changes one piece of fixed-function state against the
default (a constant-colour triangle), so its capture diffs against the default one.
"""
import pathlib
import shutil
import subprocess

import pytest

HERE = pathlib.Path(__file__).resolve().parent
CC = shutil.which("cc") or shutil.which("gcc")

PROBE = r"""
#include <stdio.h>
#include "tri1opts.h"
int main(int argc, char **argv) {
    struct tri1_opts o;
    char err[128];
    if (tri1_parse(&o, argc - 1, argv + 1, err, sizeof err)) {
        printf("error %s\n", err);
        return 1;
    }
    tri1_dump(stdout, &o);
    return 0;
}
"""


@pytest.fixture(scope="module")
def probe(tmp_path_factory):
    if not CC:
        pytest.skip("no C compiler")
    d = tmp_path_factory.mktemp("tri1opts")
    (d / "probe.c").write_text(PROBE)
    exe = d / "probe"
    subprocess.run([CC, "-std=c11", "-Wall", "-Werror", "-I", str(HERE),
                    str(d / "probe.c"), "-o", str(exe), "-lm"], check=True)
    return exe


def run(probe, *args, ok=True):
    r = subprocess.run([str(probe), *args], capture_output=True, text=True)
    assert (r.returncode == 0) == ok, r.stdout + r.stderr
    return dict(line.partition(" ")[::2] for line in r.stdout.splitlines())


def test_defaults(probe):
    o = run(probe)
    assert o["size"] == "64x64" and o["format"] == "565"
    assert o["color"] == "1 0.5 0.25 1" and o["clear"] == "0 0 1 1"
    assert o["prim"] == "0x4" and o["vcolor"] == "0" and o["shade"] == "0x1d01"
    for k in ("tex", "tex2", "fog", "light", "alphatest", "rotate", "pointsize", "clip"):
        assert o[k] == "off", k


def test_texture_environment(probe):
    o = run(probe, "tex=16x16")
    assert o["tex"] == "16x16 env=0x2100"                       # GL_MODULATE
    modes = {"replace": "0x1e01", "decal": "0x2101", "blend": "0xbe2", "add": "0x104"}
    for name, val in modes.items():
        assert run(probe, "tex=16x16", f"texenv={name}")["tex"] == f"16x16 env={val}"
    ops = {"replace": "0x1e01", "modulate": "0x2100", "add": "0x104", "addsigned": "0x8574",
           "interpolate": "0x8575", "subtract": "0x84e7", "dot3": "0x86ae"}
    for name, val in ops.items():
        o = run(probe, "tex=16x16", f"combine={name}")
        assert o["tex"] == f"16x16 env=0x8570 combine={val}", name   # GL_COMBINE
    o = run(probe, "tex=16x16", "tex2", "texenv2=add")
    assert o["tex2"] == "env=0x104"
    assert run(probe, "tex2", ok=False)["error"].startswith("tex2 needs tex")
    assert run(probe, "texenv=decal", ok=False)["error"].startswith("texenv needs tex")
    assert run(probe, "tex=16x16", "texenv=foo", ok=False)["error"].startswith("bad texenv")


def test_fog_light_alpha_shade(probe):
    assert run(probe, "fog=linear")["fog"] == "0x2601"
    assert run(probe, "fog=exp")["fog"] == "0x800"
    assert run(probe, "fog=exp2")["fog"] == "0x801"
    assert run(probe, "light")["light"] == "on"
    assert run(probe, "alphatest=greater,0.5")["alphatest"] == "0x204 0.5"
    assert run(probe, "vcolor")["vcolor"] == "1"
    assert run(probe, "shade=flat")["shade"] == "0x1d00"
    assert run(probe, "fog=thick", ok=False)["error"].startswith("bad fog")
    assert run(probe, "alphatest=greater", ok=False)["error"].startswith("bad alphatest")


def test_transform_points_clip(probe):
    assert run(probe, "rotate=30")["rotate"] == "30"
    o = run(probe, "prim=points", "pointsize=8")
    assert o["prim"] == "0x0" and o["pointsize"] == "8"
    assert run(probe, "prim=lines")["prim"] == "0x1"
    assert run(probe, "clip")["clip"] == "on"
    assert run(probe, "prim=quads", ok=False)["error"].startswith("bad prim")
    assert run(probe, "bogus", ok=False)["error"].startswith("unknown option")


def test_every_listed_gles1_run_parses(probe):
    names = set()
    for line in (HERE / "gles1_3d.txt").read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        name, *opts = line.split()
        assert name not in names
        names.add(name)
        assert "prog:tri1" in opts, name
        run(probe, *(o for o in opts if not o.startswith(("ini:", "prog:"))))
    assert "gles1_base" in names and len(names) >= 25
