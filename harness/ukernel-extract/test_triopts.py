# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Tests for triopts.h: the options of tri.c for differential 3D captures.

tri.c only builds as a 32-bit Linux program against the closed GLES2 stack, so its
argument parsing and the geometry it draws live in triopts.h and are checked here through
a small host program that prints the parsed state (tri_dump) and the vertex data.
Each option changes one piece of GL state against the default triangle, so a capture with
the option can be diffed against the default capture (diff3d.py).
"""
import pathlib
import shutil
import subprocess

import pytest

HERE = pathlib.Path(__file__).resolve().parent
CC = shutil.which("cc") or shutil.which("gcc")

PROBE = r"""
#include <stdio.h>
#include "triopts.h"
int main(int argc, char **argv) {
    struct tri_opts o;
    char err[128];
    if (tri_parse(&o, argc - 1, argv + 1, err, sizeof err)) {
        printf("error %s\n", err);
        return 1;
    }
    tri_dump(stdout, &o);
    float v[TRI_MAX_VERTS * TRI_VERT_FLOATS];
    int n = tri_geometry(&o, v);
    printf("verts %d\n", n);
    for (int i = 0; i < n; i++) {
        const float *p = v + i * TRI_VERT_FLOATS;
        printf("v%d %g %g %g %g | %g %g %g %g\n", i, p[0], p[1], p[2], p[3],
               p[4], p[5], p[6], p[7]);
    }
    for (int k = 0; k < o.draws && k < 3; k++) {
        float dx, dy;
        tri_draw_shift(&o, k, &dx, &dy);
        printf("shift%d %g %g\n", k, dx, dy);
    }
    if (o.tex_w) {
        static unsigned char t[2048 * 2048 * 4];
        int nb = tri_texels(&o, t);
        printf("texels %d", nb);
        for (int i = 0; i < 8 && i < nb; i++) printf(" %02x", t[i]);
        printf(" | %02x\n", t[nb - 1]);
    }
    if (o.attr_kind || o.attr_size != 4 || o.stride || o.vbo) {
        static unsigned char ab[TRI_MAX_VERTS * 64];
        int st = tri_attr_data(&o, v, n, ab);
        printf("attrbytes %d", st);
        for (int i = 0; i < st && i < 16; i++) printf(" %02x", ab[i]);
        printf("\n");
    }
    for (int k = 0; k < 2; k++) {
        const char *s = k ? tri_vertex_shader(&o) : tri_fragment_shader(&o);
        printf(k ? "vs " : "fs ");
        for (; *s; s++) putchar(*s == '\n' ? ' ' : *s);
        putchar('\n');
    }
    return 0;
}
"""


@pytest.fixture(scope="module")
def probe(tmp_path_factory):
    if not CC:
        pytest.skip("no C compiler")
    d = tmp_path_factory.mktemp("triopts")
    (d / "probe.c").write_text(PROBE)
    exe = d / "probe"
    subprocess.run([CC, "-std=c11", "-Wall", "-Werror", "-I", str(HERE),
                    str(d / "probe.c"), "-o", str(exe)], check=True)
    return exe


def run(probe, *args, ok=True):
    # the listings name shader files relative to this directory, where capture3d.sh runs
    r = subprocess.run([str(probe), *args], capture_output=True, text=True, cwd=HERE)
    assert (r.returncode == 0) == ok, r.stdout + r.stderr
    out = {}
    for line in r.stdout.splitlines():
        key, _, val = line.partition(" ")
        out[key] = val
    return out


def test_defaults_are_the_original_triangle(probe):
    o = run(probe)
    assert o["size"] == "64x64"
    assert o["format"] == "565"
    assert o["color"] == "1 0.5 0.25 1"
    assert o["clear"] == "0 0 1 1"
    assert o["prim"] == "0x4"            # GL_TRIANGLES
    assert o["depth"] == "off" and o["blend"] == "off" and o["cull"] == "off"
    assert o["scissor"] == "off" and o["mask"] == "1111" and o["dither"] == "1"
    assert o["viewport"] == "0 0 64 64"
    assert o["verts"] == "3"
    assert o["v0"] == "-0.5 -0.5 0 1 | 0 0 0 0"
    assert o["v2"] == "0 0.5 0 1 | 0 0 0 0"
    assert "vec4(1.0000, 0.5000, 0.2500, 1.0000)" in o["fs"]
    assert o["vs"] == "attribute vec4 pos; void main() { gl_Position = pos; } "
    assert o["tex"] == "off" and o["fbo"] == "off" and "texels" not in o


def test_size_moves_the_default_viewport(probe):
    o = run(probe, "size=100x60")
    assert o["size"] == "100x60" and o["viewport"] == "0 0 100 60"
    assert run(probe, "size=128x32", "viewport=8,4,16,16")["viewport"] == "8 4 16 16"


def test_colours(probe):
    o = run(probe, "color=0,1,0,0.5", "clear=0.25,0.5,0.75,1")
    assert o["color"] == "0 1 0 0.5" and o["clear"] == "0.25 0.5 0.75 1"
    assert "vec4(0.0000, 1.0000, 0.0000, 0.5000)" in o["fs"]
    assert run(probe, "noclear")["clear"] == "none"


def test_depth_options(probe):
    o = run(probe, "depth=less", "cleardepth=0.5", "z=0.25")
    assert o["depth"] == "0x201 clear=0.5 write=1"
    assert o["v1"] == "0.5 -0.5 0.25 1 | 0 0 0 0"
    assert run(probe, "depth=always", "depthmask=0")["depth"] == "0x207 clear=1 write=0"
    for name, val in (("never", 0x200), ("equal", 0x202), ("lequal", 0x203),
                      ("greater", 0x204), ("notequal", 0x205), ("gequal", 0x206)):
        assert run(probe, f"depth={name}")["depth"].startswith(f"{val:#x} ")


def test_blend_options(probe):
    assert run(probe, "blend=srcalpha,oneminussrcalpha")["blend"] == "0x302 0x303 eq=0x8006"
    assert run(probe, "blend=one,one", "blendeq=sub")["blend"] == "0x1 0x1 eq=0x800a"
    assert run(probe, "blend=dstcolor,zero", "blendeq=rsub")["blend"] == "0x306 0 eq=0x800b"


def test_cull_and_front_face(probe):
    assert run(probe, "cull=back")["cull"] == "0x405 front=0x901"
    assert run(probe, "cull=front", "frontface=cw")["cull"] == "0x404 front=0x900"
    assert run(probe, "cull=both")["cull"] == "0x408 front=0x901"


def test_mask_scissor_dither_stencil(probe):
    assert run(probe, "mask=1010")["mask"] == "1010"
    assert run(probe, "scissor=4,8,16,32")["scissor"] == "4 8 16 32"
    assert run(probe, "dither=0")["dither"] == "0"
    assert run(probe, "stencil=equal,3")["stencil"] == \
        "0x202 ref=3 mask=0xff write=0xff ops=0x1e00,0x1e00,0x1e01"
    o = run(probe, "stencil=less,5", "stencilmask=0x0f,0xf0", "stencilop=zero,incr,invert")
    assert o["stencil"] == "0x201 ref=5 mask=0xf write=0xf0 ops=0,0x1e02,0x150a"
    assert run(probe, "stencilop=decr,incrwrap,decrwrap")["stencilops"] == \
        "0x1e03 0x8507 0x8508"


def test_depth_range(probe):
    assert run(probe)["depthrange"] == "0 1"
    assert run(probe, "depthrange=0.25,0.75")["depthrange"] == "0.25 0.75"


def test_primitives(probe):
    assert run(probe, "prim=strip")["prim"] == "0x5"
    assert run(probe, "prim=strip")["verts"] == "4"
    assert run(probe, "prim=fan")["prim"] == "0x6"
    assert run(probe, "prim=two")["prim"] == "0x4"
    assert run(probe, "prim=two")["verts"] == "6"
    assert run(probe, "prim=points")["prim"] == "0x0"
    assert "gl_PointSize" in run(probe, "prim=points")["vs"]
    assert "gl_PointSize" not in run(probe)["vs"]
    assert run(probe, "prim=lines")["prim"] == "0x1"
    assert run(probe, "prim=lines")["verts"] == "4"
    assert run(probe, "prim=linestrip")["prim"] == "0x3"


def test_vertex_transform(probe):
    o = run(probe, "scale=2", "shift=0.25,-0.25")
    assert o["v0"] == "-0.75 -1.25 0 1 | 0 0 0 0"


def test_varying_colour_adds_an_attribute(probe):
    o = run(probe, "varying")
    assert o["varying"] == "1"
    assert o["v0"] == "-0.5 -0.5 0 1 | 1 0 0 1"
    assert o["v1"].endswith("| 0 1 0 1") and o["v2"].endswith("| 0 0 1 1")
    assert "varying" in o["fs"] and "gl_FragColor = col" in o["fs"]
    assert "attribute vec4 colour" in o["vs"]


def test_format_8888(probe):
    assert run(probe, "format=8888")["format"] == "8888"


@pytest.mark.parametrize("listing", ["variations3d.txt", "track3d.txt", "textures3d.txt",
                                     "inputs3d.txt"])
def test_every_listed_variation_parses(probe, listing):
    names = set()
    for line in (HERE / listing).read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        name, *opts = line.split()
        assert name not in names
        names.add(name)
        run(probe, *(o for o in opts if not o.startswith("ini:")))
        for o in opts:
            if o.startswith("ini:"):
                assert "=" in o and " " not in o
    assert "base" in names


def test_errors(probe):
    assert run(probe, "bogus=1", ok=False)["error"].startswith("unknown option")
    assert run(probe, "size=0x10", ok=False)["error"].startswith("bad size")
    assert run(probe, "depth=sometimes", ok=False)["error"].startswith("bad depth")
    assert run(probe, "format=444", ok=False)["error"].startswith("bad format")


def test_several_draws_flushes_and_frames(probe):
    o = run(probe)
    assert o["draws"] == "1 flush=0" and o["frames"] == "1 clearonce=0"
    o = run(probe, "draws=3", "flush")
    assert o["draws"] == "3 flush=1"
    # each draw moves right by 0.05, wrapping every 8 draws, so all stay on screen
    assert o["shift0"] == "0 0" and o["shift1"] == "0.05 0" and o["shift2"] == "0.1 0"
    o = run(probe, "frames=2", "clearonce")
    assert o["frames"] == "2 clearonce=1"
    assert run(probe, "draws=4096")["draws"] == "4096 flush=0"
    assert run(probe, "draws=0", ok=False)["error"].startswith("bad draws")
    assert run(probe, "draws=4097", ok=False)["error"].startswith("bad draws")
    assert run(probe, "frames=9", ok=False)["error"].startswith("bad frames")


def test_ini_words_are_not_tri_options(probe):
    assert run(probe, "ini:PBSize=65536", ok=False)["error"].startswith("unknown option")


def test_texture_options(probe):
    """tex=WxH samples a texture whose texel bytes are its own x, y (x ^ y, then 0xff), so
    a capture shows how the driver lays texels out; uv comes from the position."""
    o = run(probe, "tex=16x8")
    assert o["tex"] == ("16x8 fmt=0x1908,0x1401 bpp=4 filter=0x2600,0x2600 mip=0 wrap=0x2901 "
                        "wrapt=0x2901")
    assert o["texels"] == "512 00 00 00 ff 01 00 01 ff | ff"      # (0,0), (1,0) .. (15,7)
    assert "uniform sampler2D tex;" in o["fs"] and "texture2D(tex, uv)" in o["fs"]
    assert "uv = pos.xy * 0.5 + 0.5;" in o["vs"]
    o = run(probe, "tex=8x8", "texfmt=565", "texfilter=mipmap", "texwrap=clamp")
    assert o["tex"] == ("8x8 fmt=0x1907,0x8363 bpp=2 filter=0x2703,0x2601 mip=1 wrap=0x812f "
                        "wrapt=0x812f")
    assert o["texels"] == "128 00 00 01 00 02 00 03 00 | 07"
    fmts = {"8888": "0x1908,0x1401 bpp=4", "888": "0x1907,0x1401 bpp=3",
            "565": "0x1907,0x8363 bpp=2", "4444": "0x1908,0x8033 bpp=2",
            "5551": "0x1908,0x8034 bpp=2", "l8": "0x1909,0x1401 bpp=1",
            "a8": "0x1906,0x1401 bpp=1", "la88": "0x190a,0x1401 bpp=2"}
    for name, want in fmts.items():
        assert f"fmt={want} " in run(probe, "tex=4x4", f"texfmt={name}")["tex"], name
    assert run(probe, "tex=4x4", "texfmt=l8")["texels"] == "16 00 01 02 03 10 11 12 13 | 33"
    assert "filter=0x2601,0x2601 mip=0" in run(probe, "tex=4x4", "texfilter=linear")["tex"]
    assert "wrap=0x8370" in run(probe, "tex=4x4", "texwrap=mirror")["tex"]


def test_fbo_option(probe):
    """fbo=WxH: the triangle goes into a texture first, then a quad samples it."""
    o = run(probe, "fbo=32x16")
    assert o["fbo"] == "32x16" and o["tex"] == "off"
    assert o["fs"].startswith("precision mediump float; void main() { gl_FragColor = vec4(")


def test_texture_errors(probe):
    assert run(probe, "tex=0x4", ok=False)["error"].startswith("bad tex")
    assert run(probe, "tex=4096x4", ok=False)["error"].startswith("bad tex")
    assert run(probe, "tex=4x4", "texfmt=dxt1", ok=False)["error"].startswith("bad texfmt")
    assert run(probe, "texfilter=cubic", ok=False)["error"].startswith("bad texfilter")
    assert run(probe, "texwrap=edge", ok=False)["error"].startswith("bad texwrap")
    assert run(probe, "fbo=2x5000", ok=False)["error"].startswith("bad fbo")
    assert run(probe, "tex=4x4", "varying", ok=False)["error"].startswith("tex and varying")


def test_readback_copy_and_update_options(probe):
    o = run(probe)
    assert o["readback"] == "1x1" and o["copytex"] == "0" and o["texsub"] == "0"
    assert o["samples"] == "0"
    assert run(probe, "readback")["readback"] == "full"
    assert run(probe, "copytex")["copytex"] == "1"
    assert run(probe, "tex=16x16", "texsub")["texsub"] == "1"
    assert run(probe, "texsub", ok=False)["error"].startswith("texsub needs tex")
    assert run(probe, "samples=4")["samples"] == "4"
    assert run(probe, "samples=3", ok=False)["error"].startswith("bad samples")


def test_second_texture_and_cube_options(probe):
    o = run(probe, "tex=16x16", "tex2")
    assert o["tex2"] == "1" and o["cube"] == "0"
    assert "uniform sampler2D tex1;" in o["fs"]
    assert "texture2D(tex, uv) * texture2D(tex1, uv * 2.0)" in o["fs"]
    o = run(probe, "tex=16x16", "cube")
    assert o["cube"] == "1" and "uniform samplerCube tex;" in o["fs"]
    assert "textureCube(tex, vec3(uv * 2.0 - 1.0, 1.0))" in o["fs"]
    assert run(probe, "tex2", ok=False)["error"].startswith("tex2 needs tex")
    assert run(probe, "tex=16x8", "cube", ok=False)["error"].startswith("cube needs a square tex")
    assert run(probe, "tex=16x16", "cube", "tex2", ok=False)["error"].startswith("cube and tex2")


def test_shader_files(probe, tmp_path):
    """vsfile=/fsfile= read the shaders from files (the shader corpus, shaders3d.txt)."""
    vs, fs = tmp_path / "a.vert", tmp_path / "a.frag"
    vs.write_text("attribute vec4 pos;\nvoid main() { gl_Position = pos * 0.5; }\n")
    fs.write_text("precision mediump float;\nvoid main() { gl_FragColor = vec4(0.25); }\n")
    o = run(probe, f"vsfile={vs}", f"fsfile={fs}")
    assert o["vs"] == "attribute vec4 pos; void main() { gl_Position = pos * 0.5; } "
    assert o["fs"] == "precision mediump float; void main() { gl_FragColor = vec4(0.25); } "
    assert o["vsfile"] == str(vs) and o["fsfile"] == str(fs)
    assert run(probe)["fsfile"] == "-"
    assert run(probe, f"fsfile={tmp_path}/none.frag", ok=False)["error"].startswith("bad fsfile")
    assert run(probe, f"fsfile={fs}", "tex=4x4", ok=False)["error"].startswith("fsfile and tex")


def test_every_corpus_shader_is_listed_and_exists():
    names = set()
    for line in (HERE / "shaders3d.txt").read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        name, *opts = line.split()
        assert name not in names
        names.add(name)
        for o in opts:
            if o.startswith(("vsfile=", "fsfile=")):
                assert (HERE / o.split("=", 1)[1]).is_file(), o
    assert len(names) >= 60
    assert sum(n.startswith("vs_") for n in names) >= 15


def test_uniform_options(probe):
    o = run(probe)
    assert o["uniforms"] == "0"
    o = run(probe, "uniform=u0:1,2,3,4", "uniform=uf:0.5", "uniformi=ui:7", "uniformm=m4:4")
    assert o["uniforms"] == "4"
    assert o["uniform0"] == "f u0 4 1 2 3 4"
    assert o["uniform1"] == "f uf 1 0.5"
    assert o["uniform2"] == "i ui 1 7"
    assert o["uniform3"] == "m m4 16 1 2 3 4"          # the first four of 1..16
    assert run(probe, "uniformm=m2:2")["uniform0"] == "m m2 4 1 2 3 4"
    assert run(probe, "uniform=u0", ok=False)["error"].startswith("bad uniform")
    assert run(probe, "uniform=u0:1,2,3,4,5", ok=False)["error"].startswith("bad uniform")
    assert run(probe, "uniformm=m5:5", ok=False)["error"].startswith("bad uniformm")
    many = [f"uniform=u{k}:1" for k in range(9)]
    assert run(probe, *many, ok=False)["error"].startswith("bad uniform")


def test_attribute_format_options(probe):
    """The position attribute as another type, size, stride or in a buffer object; the
    vertex bytes (v0 first) are what tri passes to glVertexAttribPointer."""
    o = run(probe)
    assert o["attr"] == "float size=4 norm=0 stride=0 vbo=0" and "attrbytes" not in o
    o = run(probe, "attrfmt=byte", "attrnorm", "attrsize=2")
    assert o["attr"] == "byte size=2 norm=1 stride=0 vbo=0"
    # v0 = (-0.5, -0.5): normalized bytes -64, -64 (0xc0); stride = 2 bytes
    assert o["attrbytes"] == "2 c0 c0"
    o = run(probe, "attrfmt=short", "attrnorm", "attrsize=3", "stride=8")
    assert o["attrbytes"].startswith("8 00 c0 00 c0 00 00")    # -16384 = 0xc000, then z = 0
    o = run(probe, "attrfmt=ubyte", "attrsize=4")              # not normalized: x * 8 + 8
    assert o["attrbytes"] == "4 04 04 08 10"
    o = run(probe, "vbo")
    assert o["attr"] == "float size=4 norm=0 stride=0 vbo=1"
    assert o["attrbytes"].startswith("16 00 00 00 bf 00 00 00 bf")  # -0.5f
    assert run(probe, "attrfmt=half", ok=False)["error"].startswith("bad attrfmt")
    assert run(probe, "attrsize=1", ok=False)["error"].startswith("bad attrsize")
    assert run(probe, "stride=3", ok=False)["error"].startswith("bad stride")
    assert run(probe, "attrfmt=byte", "draws=2", ok=False)["error"].startswith("attribute options")
    assert run(probe, "attrfmt=byte", "varying", ok=False)["error"].startswith("attribute options")


def test_polygon_offset_option(probe):
    """polyoffset=F,U: GL_POLYGON_OFFSET_FILL on with glPolygonOffset(F, U)."""
    assert run(probe)["polyoffset"] == "off"
    assert run(probe, "polyoffset=1.5,-2")["polyoffset"] == "1.5,-2"
    assert run(probe, "polyoffset=1", ok=False)["error"].startswith("bad polyoffset")


def test_fbo_samples_and_depth_options(probe):
    """fbosamples=N: the fbo's texture attached multisampled (IMG_multisampled_render_to_
    texture); fbodepth: a 16-bit depth renderbuffer on the fbo."""
    o = run(probe, "fbo=32x32")
    assert o["fbosamples"] == "0" and o["fbodepth"] == "0"
    o = run(probe, "fbo=32x32", "fbosamples=4", "fbodepth")
    assert o["fbosamples"] == "4" and o["fbodepth"] == "1"
    assert run(probe, "fbo=32x32", "fbosamples=3", ok=False)["error"].startswith("bad fbosamples")
    assert run(probe, "fbosamples=4", ok=False)["error"].startswith("fbosamples needs fbo")
    assert run(probe, "fbodepth", ok=False)["error"].startswith("fbodepth needs fbo")


def test_stream_option(probe):
    """stream=FMT[,WxH]: the triangle samples the fake buffer-class device's YUV buffer
    (fakedrm.c, bufclass.h) through IMG_texture_stream2; FAKEBC carries the format."""
    o = run(probe)
    assert o["stream"] == "off"
    o = run(probe, "stream=nv12")
    assert o["stream"] == "nv12,64x64"
    assert o["fs"].startswith("#extension GL_IMG_texture_stream2 : require")
    assert "uniform samplerStreamIMG tex;" in o["fs"] and "textureStreamIMG(tex, uv)" in o["fs"]
    assert "uv = pos.xy * 0.5 + 0.5" in o["vs"]
    assert run(probe, "stream=uyvy,32x16")["stream"] == "uyvy,32x16"
    assert run(probe, "stream=rgb", ok=False)["error"].startswith("bad stream")
    assert run(probe, "stream=uyvy", "tex=4x4", ok=False)["error"].startswith("stream and tex")


def test_texture_filter_and_wrap_per_axis(probe):
    """texmin=/texmag= set one filter each (texmin's mipmap modes generate mipmaps);
    texwraps=/texwrapt= set one axis's wrap each."""
    t = run(probe, "tex=16x16", "texmin=lml", "texmag=linear")["tex"]
    assert "filter=0x2703,0x2601 mip=1" in t
    assert "filter=0x2700,0x2600 mip=1" in run(probe, "tex=16x16", "texmin=nmn")["tex"]
    assert "filter=0x2601,0x2600 mip=0" in run(probe, "tex=16x16", "texmin=linear")["tex"]
    t = run(probe, "tex=16x16", "texwraps=clamp", "texwrapt=mirror")["tex"]
    assert "wrap=0x812f wrapt=0x8370" in t
    assert "wrap=0x2901 wrapt=0x2901" in run(probe, "tex=16x16")["tex"]
    assert run(probe, "tex=16x16", "texmin=cubic", ok=False)["error"].startswith("bad texmin")


def test_more_texture_formats(probe):
    """BGRA, float, half-float, depth and compressed (PVRTC, ETC1) texture formats: the
    Khronos enums the driver's extensions name; compressed ones upload a block-sized image."""
    fmts = {"bgra8888": "0x80e1,0x1401 bpp=4", "f32": "0x1908,0x1406 bpp=16",
            "f16": "0x1908,0x8d61 bpp=8", "lf32": "0x1909,0x1406 bpp=4",
            "lf16": "0x1909,0x8d61 bpp=2", "depth16": "0x1902,0x1403 bpp=2",
            "depth32": "0x1902,0x1405 bpp=4"}
    for name, want in fmts.items():
        assert f"fmt={want} " in run(probe, "tex=4x4", f"texfmt={name}")["tex"], name
    o = run(probe, "tex=16x16", "texfmt=f32")
    assert o["texels"].startswith("4096 00 00 00 ff 00 00 00 ff")    # the 4-byte pattern
    # compressed: format, no type, the image's byte count (PVRTC 4bpp at least 8x8, 2bpp at
    # least 16x8, ETC1 in 8-byte 4x4 blocks)
    for name, fmt, n in (("pvrtc4", 0x8C02, 128), ("pvrtc2", 0x8C03, 64),
                         ("pvrtc4rgb", 0x8C00, 128), ("pvrtc2rgb", 0x8C01, 64),
                         ("etc1", 0x8D64, 128)):
        o = run(probe, "tex=16x16", f"texfmt={name}")
        assert f"fmt={fmt:#x},0 " in o["tex"] and o["texels"].startswith(f"{n} "), name
    assert run(probe, "tex=4x4", "texfmt=pvrtc2")["texels"].startswith("32 ")   # 16x8 minimum
    assert run(probe, "tex=16x16", "texfmt=etc1", "texfilter=mipmap",
               ok=False)["error"].startswith("compressed textures take no mipmaps")


def test_coverage_line_and_hint_options(probe):
    """a2c: GL_SAMPLE_ALPHA_TO_COVERAGE on; samplecov=V[,inv]: GL_SAMPLE_COVERAGE on with
    glSampleCoverage(V, inv); linewidth=W; hint=TARGET,MODE (deriv or mipmap, fastest or
    nicest)."""
    o = run(probe)
    assert o["a2c"] == "0" and o["samplecov"] == "off" and o["linewidth"] == "1" and \
        o["hint"] == "off"
    o = run(probe, "a2c", "samplecov=0.5,inv", "linewidth=4", "hint=deriv,nicest")
    assert o["a2c"] == "1" and o["samplecov"] == "0.5,1" and o["linewidth"] == "4"
    assert o["hint"] == "0x8b8b,0x1102"
    assert run(probe, "hint=mipmap,fastest")["hint"] == "0x8192,0x1101"
    assert run(probe, "samplecov=2", ok=False)["error"].startswith("bad samplecov")
    assert run(probe, "hint=deriv", ok=False)["error"].startswith("bad hint")
