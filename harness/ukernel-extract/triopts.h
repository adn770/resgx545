// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
/* triopts.h: the options of tri.c, for differential 3D captures.
 *
 * Every option changes one piece of GL state against the default frame (a
 * constant-colour triangle on a blue clear, 64x64 RGB565), so the capture it
 * produces can be diffed against the default one (diff3d.py). Options are
 * key=value words on the command line:
 *
 *   size=WxH            surface size (the viewport follows unless given)
 *   format=565|8888     WSEGL pixel format (RGB565, ARGB8888)
 *   color=r,g,b,a       the fragment shader's constant colour
 *   clear=r,g,b,a       glClearColor; "noclear" skips glClear
 *   depth=FUNC          depth test on with FUNC (never less equal lequal greater
 *                       notequal gequal always); cleardepth=F, depthmask=0, z=F
 *   depthrange=N,F      glDepthRangef
 *   stencil=FUNC,REF    stencil test on; stencilmask=CMP,WRITE (hex),
 *                       stencilop=SFAIL,ZFAIL,ZPASS (keep zero replace incr decr
 *                       invert incrwrap decrwrap; default keep,keep,replace)
 *   blend=SRC,DST       blending on (zero one srccolor oneminussrccolor srcalpha
 *                       oneminussrcalpha dstalpha oneminusdstalpha dstcolor
 *                       oneminusdstcolor); blendeq=add|sub|rsub
 *   cull=front|back|both, frontface=cw|ccw
 *   mask=RGBA           colour mask as four 0/1 digits
 *   scissor=x,y,w,h     scissor test on
 *   viewport=x,y,w,h
 *   dither=0            dithering off (GL default is on)
 *   prim=tri|two|strip|fan|points|lines|linestrip
 *   scale=S, shift=dx,dy  transform the vertex positions
 *   varying             a per-vertex colour attribute, interpolated
 *   draws=N             N draw calls in the frame (1-4096), draw k moved right by
 *                       0.05 * (k % 8); flush: glFlush between them
 *   frames=N            N frames (1-8), each ended by eglSwapBuffers; clearonce
 *                       clears only the first (later frames load what it left)
 *   tex=WxH             the triangle samples a WxH texture (1-2048 each side), uv from
 *                       the position; texel bytes are its x, y, x ^ y, 0xff (bpp 2: x, y;
 *                       bpp 1: x + 16 y), so a capture shows how the driver lays them out.
 *                       texfmt=8888|888|565|4444|5551|l8|a8|la88 (default 8888),
 *                       texfilter=nearest|linear|mipmap (glGenerateMipmap; default
 *                       nearest), texwrap=repeat|clamp|mirror (default repeat);
 *                       texmin=nearest|linear|nmn|lmn|nml|lml, texmag=nearest|linear one
 *                       filter each (the min's mipmap modes generate mipmaps),
 *                       texwraps=, texwrapt= one axis's wrap each
 *   fbo=WxH             draw the triangle into a WxH RGBA texture through a framebuffer
 *                       object, then a quad sampling it into the surface (two renders)
 *   tex2                (with tex) a second texture, the same, on unit 1, multiplied in at
 *                       twice the frequency; cube: (with a square tex) a cube map of six
 *                       such faces instead
 *   texsub              (with tex) after each frame, glTexSubImage2D of the lower left
 *                       quarter with every byte inverted
 *   copytex             after each frame, glCopyTexImage2D of the whole surface
 *   readback            glReadPixels of the whole surface (default: the centre pixel)
 *   samples=N           an EGL configuration with N samples (2 or 4)
 *   polyoffset=F,U      polygon offset fill on, glPolygonOffset(F, U)
 *   fbosamples=N        (with fbo) the texture attached with N samples (2 or 4) through
 *                       IMG_multisampled_render_to_texture
 *   fbodepth            (with fbo) a 16-bit depth renderbuffer on the framebuffer object
 *   a2c                 GL_SAMPLE_ALPHA_TO_COVERAGE on; samplecov=V[,inv] GL_SAMPLE_COVERAGE
 *                       on with glSampleCoverage(V, inv); linewidth=W glLineWidth(W);
 *                       hint=deriv|mipmap,fastest|nicest one glHint
 *   stream=FMT[,WxH]    the triangle samples a YUV buffer (bufclass.h's names; default 64x64)
 *                       of fakedrm.c's buffer-class device through IMG_texture_stream2
 *                       (bufclass.h: the format and the pattern; FAKEBC carries them)
 *   vsfile=PATH, fsfile=PATH  the vertex/fragment shader read from a file (up to 8 KiB;
 *                       the shader corpus, shaders3d.txt); "pos" is attribute 0
 *   uniform=NAME:x[,y,z,w]  set a float/vec uniform; uniformi=NAME:v an int one;
 *                       uniformm=NAME:N an NxN matrix of 1, 2, 3, ... (up to 8 in all)
 *   attrfmt=float|byte|ubyte|short|ushort, attrnorm, attrsize=2|3|4, stride=N, vbo
 *                       the position attribute's type, normalisation, components, bytes
 *                       per vertex (a multiple of 4) and a buffer object instead of a
 *                       client array (draws=1, no varying or fbo); unnormalised integers
 *                       are x * 8 (+ 8 if unsigned), normalised unsigned (x / 2 + 1/2)
 *
 * The values are the Khronos GLES 2.0 API constants. */
#ifndef TRIOPTS_H
#define TRIOPTS_H

#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

#include "bufclass.h"

#define TRI_MAX_VERTS   8
#define TRI_VERT_FLOATS 8       /* position xyzw, colour rgba */

struct tri_opts {
    int w, h;
    int format;                 /* 565 or 8888 */
    float color[4], clear[4];
    int do_clear;
    unsigned depth_func;        /* 0 = depth test off */
    float clear_depth, z;
    int depth_write;
    unsigned stencil_func;      /* 0 = stencil test off */
    int stencil_ref;
    unsigned stencil_mask, stencil_write, stencil_ops[3];   /* sfail, zfail, zpass */
    float depth_range[2];
    unsigned blend_src, blend_dst, blend_eq;  /* blend_eq 0 = blending off */
    unsigned cull;              /* 0 = culling off */
    unsigned front_face;
    int mask[4];
    int scissor[4], do_scissor;
    int viewport[4], have_viewport;
    int dither;
    unsigned prim;
    int prim_kind;              /* index into TRI_PRIMS */
    float scale, shift[2];
    int varying;
    int draws, flush;           /* draw calls per frame, glFlush between them */
    int frames, clear_once;     /* frames, and clear only the first */
    int tex_w, tex_h, tex_kind; /* texture size (0: none), index into TRI_TEXFMTS */
    unsigned tex_min, tex_mag, tex_wrap, tex_wrap_t;   /* tex_wrap: S (and T unless set) */
    int tex_wrap_t_set;
    int tex_mip;
    int fbo_w, fbo_h;           /* render-to-texture size (0: none) */
    int tex2, cube, texsub, copytex, readback, samples;
    int polyoffset;             /* polygon offset fill on, with poly_factor, poly_units */
    float poly_factor, poly_units;
    int fbo_samples, fbo_depth;
    int a2c, samplecov, samplecov_inv;
    float samplecov_v, linewidth;
    unsigned hint_target, hint_mode;    /* 0: no glHint */
    char stream[24];            /* FAKEBC's "fmt,WxH", "" = no stream texture */
    char vsfile[256], fsfile[256];
    int nuniforms;
    struct tri_uniform { char kind, name[16]; int n; float f[16]; } uni[8];
    int attr_kind, attr_size, attr_norm, stride, vbo;
};

struct tri_name { const char *name; unsigned value; };

static const struct tri_name TRI_FUNCS[] = {
    { "never", 0x0200 }, { "less", 0x0201 }, { "equal", 0x0202 }, { "lequal", 0x0203 },
    { "greater", 0x0204 }, { "notequal", 0x0205 }, { "gequal", 0x0206 },
    { "always", 0x0207 }, { 0, 0 },
};
static const struct tri_name TRI_FACTORS[] = {
    { "zero", 0 }, { "one", 1 }, { "srccolor", 0x0300 }, { "oneminussrccolor", 0x0301 },
    { "srcalpha", 0x0302 }, { "oneminussrcalpha", 0x0303 }, { "dstalpha", 0x0304 },
    { "oneminusdstalpha", 0x0305 }, { "dstcolor", 0x0306 }, { "oneminusdstcolor", 0x0307 },
    { 0, 0 },
};
static const struct tri_name TRI_STENCIL_OPS[] = {
    { "keep", 0x1E00 }, { "zero", 0 }, { "replace", 0x1E01 }, { "incr", 0x1E02 },
    { "decr", 0x1E03 }, { "invert", 0x150A }, { "incrwrap", 0x8507 }, { "decrwrap", 0x8508 },
    { 0, 0 },
};
static const struct tri_name TRI_EQS[] = {
    { "add", 0x8006 }, { "sub", 0x800A }, { "rsub", 0x800B }, { 0, 0 },
};
static const struct tri_name TRI_FACES[] = {
    { "front", 0x0404 }, { "back", 0x0405 }, { "both", 0x0408 }, { 0, 0 },
};
static const struct tri_name TRI_WINDING[] = { { "cw", 0x0900 }, { "ccw", 0x0901 }, { 0, 0 } };

/* name, GL primitive, vertex count; the vertices come from TRI_SHAPE[kind]. */
static const struct { const char *name; unsigned prim; int n; } TRI_PRIMS[] = {
    { "tri", 0x0004, 3 }, { "two", 0x0004, 6 }, { "strip", 0x0005, 4 },
    { "fan", 0x0006, 4 }, { "points", 0x0000, 3 }, { "lines", 0x0001, 4 },
    { "linestrip", 0x0003, 3 },
};
#define TRI_NPRIMS ((int)(sizeof TRI_PRIMS / sizeof TRI_PRIMS[0]))

/* attrfmt: name, glVertexAttribPointer type, bytes per component. */
static const struct { const char *name; unsigned type; int bytes; } TRI_ATTRFMTS[] = {
    { "float", 0x1406, 4 }, { "byte", 0x1400, 1 }, { "ubyte", 0x1401, 1 },
    { "short", 0x1402, 2 }, { "ushort", 0x1403, 2 },
};
#define TRI_NATTRFMTS ((int)(sizeof TRI_ATTRFMTS / sizeof TRI_ATTRFMTS[0]))

/* texfmt: name, glTexImage2D format and type, bytes per texel. */
/* comp: 0 for an uncompressed format, else the compressed kind (TRI_COMP_*): uploaded with
 * glCompressedTexImage2D, type 0. The enums are the Khronos ones of the extensions the
 * closed driver advertises (EXT/IMG_texture_format_BGRA8888, OES_texture_float,
 * OES_texture_half_float, OES_depth_texture, IMG_texture_compression_pvrtc,
 * OES_compressed_ETC1_RGB8_texture). */
enum { TRI_COMP_NONE, TRI_COMP_PVRTC4, TRI_COMP_PVRTC2, TRI_COMP_ETC1 };
static const struct { const char *name; unsigned format, type; int bpp, comp; } TRI_TEXFMTS[] = {
    { "8888", 0x1908, 0x1401, 4, 0 }, { "888", 0x1907, 0x1401, 3, 0 },
    { "565", 0x1907, 0x8363, 2, 0 }, { "4444", 0x1908, 0x8033, 2, 0 },
    { "5551", 0x1908, 0x8034, 2, 0 }, { "l8", 0x1909, 0x1401, 1, 0 },
    { "a8", 0x1906, 0x1401, 1, 0 }, { "la88", 0x190A, 0x1401, 2, 0 },
    { "bgra8888", 0x80E1, 0x1401, 4, 0 }, { "f32", 0x1908, 0x1406, 16, 0 },
    { "f16", 0x1908, 0x8D61, 8, 0 }, { "lf32", 0x1909, 0x1406, 4, 0 },
    { "lf16", 0x1909, 0x8D61, 2, 0 }, { "depth16", 0x1902, 0x1403, 2, 0 },
    { "depth32", 0x1902, 0x1405, 4, 0 },
    { "pvrtc4", 0x8C02, 0, 0, TRI_COMP_PVRTC4 }, { "pvrtc2", 0x8C03, 0, 0, TRI_COMP_PVRTC2 },
    { "pvrtc4rgb", 0x8C00, 0, 0, TRI_COMP_PVRTC4 }, { "pvrtc2rgb", 0x8C01, 0, 0, TRI_COMP_PVRTC2 },
    { "etc1", 0x8D64, 0, 0, TRI_COMP_ETC1 },
};

/* A compressed image's byte count: PVRTC 4bpp at least 8x8, 2bpp at least 16x8 (the
 * IMG_texture_compression_pvrtc rule), ETC1 in 8-byte blocks of 4x4. */
static int tri_comp_size(int comp, int w, int h)
{
    if (comp == TRI_COMP_PVRTC4)
        return (w < 8 ? 8 : w) * (h < 8 ? 8 : h) / 2;
    if (comp == TRI_COMP_PVRTC2)
        return (w < 16 ? 16 : w) * (h < 8 ? 8 : h) / 4;
    return ((w + 3) / 4) * ((h + 3) / 4) * 8;
}
#define TRI_NTEXFMTS ((int)(sizeof TRI_TEXFMTS / sizeof TRI_TEXFMTS[0]))
#define TRI_TEX_MAX 2048
static const struct tri_name TRI_WRAPS[] = {
    { "repeat", 0x2901 }, { "clamp", 0x812F }, { "mirror", 0x8370 }, { 0, 0 },
};

/* x, y of each vertex (counter-clockwise triangles). */
static const float TRI_SHAPE[][TRI_MAX_VERTS][2] = {
    { { -0.5f, -0.5f }, { 0.5f, -0.5f }, { 0.0f, 0.5f } },
    { { -0.5f, -0.5f }, { 0.0f, -0.5f }, { -0.25f, 0.0f },
      { 0.0f, 0.0f }, { 0.5f, 0.0f }, { 0.25f, 0.5f } },
    { { -0.5f, -0.5f }, { 0.5f, -0.5f }, { -0.5f, 0.5f }, { 0.5f, 0.5f } },
    { { -0.5f, -0.5f }, { 0.5f, -0.5f }, { 0.5f, 0.5f }, { -0.5f, 0.5f } },
    { { -0.5f, -0.5f }, { 0.5f, -0.5f }, { 0.0f, 0.5f } },
    { { -0.5f, -0.5f }, { 0.5f, -0.5f }, { -0.5f, 0.5f }, { 0.5f, 0.5f } },
    { { -0.5f, -0.5f }, { 0.5f, -0.5f }, { 0.0f, 0.5f } },
};
static const float TRI_COLOURS[3][4] = { { 1, 0, 0, 1 }, { 0, 1, 0, 1 }, { 0, 0, 1, 1 } };

static int tri_lookup(const struct tri_name *t, const char *s, unsigned *out)
{
    for (; t->name; t++)
        if (!strcmp(t->name, s)) { *out = t->value; return 0; }
    return -1;
}

static int tri_floats(const char *s, float *out, int n)
{
    char *end;
    for (int i = 0; i < n; i++) {
        out[i] = strtof(s, &end);
        if (end == s) return -1;
        s = end;
        if (i + 1 < n) {
            if (*s != ',') return -1;
            s++;
        }
    }
    return *s ? -1 : 0;
}

static int tri_ints(const char *s, int *out, int n)
{
    float f[4];
    if (n > 4 || tri_floats(s, f, n)) return -1;
    for (int i = 0; i < n; i++) out[i] = (int)f[i];
    return 0;
}

static void tri_defaults(struct tri_opts *o)
{
    static const struct tri_opts d = {
        .w = 64, .h = 64, .format = 565, .color = { 1.0f, 0.5f, 0.25f, 1.0f },
        .clear = { 0.0f, 0.0f, 1.0f, 1.0f }, .do_clear = 1, .clear_depth = 1.0f,
        .depth_write = 1, .front_face = 0x0901, .mask = { 1, 1, 1, 1 }, .dither = 1,
        .prim = 0x0004, .scale = 1.0f, .stencil_mask = 0xff, .stencil_write = 0xff,
        .stencil_ops = { 0x1E00, 0x1E00, 0x1E01 }, .depth_range = { 0.0f, 1.0f },
        .draws = 1, .frames = 1, .linewidth = 1.0f, .tex_min = 0x2600, .tex_mag = 0x2600, .tex_wrap = 0x2901,
        .attr_size = 4,
    };
    *o = d;
}

/* Parse key=value words; 0 on success, else -1 with a message in err. */
static int tri_parse(struct tri_opts *o, int argc, char **argv, char *err, size_t errn)
{
    tri_defaults(o);
    for (int i = 0; i < argc; i++) {
        char key[32];
        const char *a = argv[i], *eq = strchr(a, '=');
        const char *v = eq ? eq + 1 : "";
        size_t kn = eq ? (size_t)(eq - a) : strlen(a);
        if (kn >= sizeof key) kn = sizeof key - 1;
        memcpy(key, a, kn);
        key[kn] = 0;
        int bad = 0;
        if (!strcmp(key, "size")) {
            bad = sscanf(v, "%dx%d", &o->w, &o->h) != 2 || o->w <= 0 || o->h <= 0;
        } else if (!strcmp(key, "format")) {
            o->format = atoi(v);
            bad = o->format != 565 && o->format != 8888;
        } else if (!strcmp(key, "color")) {
            bad = tri_floats(v, o->color, 4);
        } else if (!strcmp(key, "clear")) {
            bad = tri_floats(v, o->clear, 4);
        } else if (!strcmp(key, "noclear")) {
            o->do_clear = 0;
        } else if (!strcmp(key, "depth")) {
            bad = tri_lookup(TRI_FUNCS, v, &o->depth_func);
        } else if (!strcmp(key, "cleardepth")) {
            bad = tri_floats(v, &o->clear_depth, 1);
        } else if (!strcmp(key, "depthmask")) {
            o->depth_write = atoi(v) != 0;
        } else if (!strcmp(key, "z")) {
            bad = tri_floats(v, &o->z, 1);
        } else if (!strcmp(key, "stencil")) {
            char f[16] = "";
            bad = sscanf(v, "%15[a-z],%d", f, &o->stencil_ref) != 2 ||
                  tri_lookup(TRI_FUNCS, f, &o->stencil_func);
        } else if (!strcmp(key, "stencilmask")) {
            bad = sscanf(v, "%x,%x", &o->stencil_mask, &o->stencil_write) != 2;
        } else if (!strcmp(key, "stencilop")) {
            char f[3][16] = { "", "", "" };
            bad = sscanf(v, "%15[a-z],%15[a-z],%15[a-z]", f[0], f[1], f[2]) != 3;
            for (int k = 0; !bad && k < 3; k++)
                bad = tri_lookup(TRI_STENCIL_OPS, f[k], &o->stencil_ops[k]);
        } else if (!strcmp(key, "depthrange")) {
            bad = tri_floats(v, o->depth_range, 2);
        } else if (!strcmp(key, "blend")) {
            char s[24] = "", d[24] = "";
            bad = sscanf(v, "%23[a-z],%23[a-z]", s, d) != 2 ||
                  tri_lookup(TRI_FACTORS, s, &o->blend_src) ||
                  tri_lookup(TRI_FACTORS, d, &o->blend_dst);
            if (!o->blend_eq) o->blend_eq = 0x8006;
        } else if (!strcmp(key, "blendeq")) {
            bad = tri_lookup(TRI_EQS, v, &o->blend_eq);
        } else if (!strcmp(key, "cull")) {
            bad = tri_lookup(TRI_FACES, v, &o->cull);
        } else if (!strcmp(key, "frontface")) {
            bad = tri_lookup(TRI_WINDING, v, &o->front_face);
        } else if (!strcmp(key, "mask")) {
            bad = strlen(v) != 4 || strspn(v, "01") != 4;
            for (int k = 0; !bad && k < 4; k++) o->mask[k] = v[k] == '1';
        } else if (!strcmp(key, "scissor")) {
            bad = tri_ints(v, o->scissor, 4);
            o->do_scissor = 1;
        } else if (!strcmp(key, "viewport")) {
            bad = tri_ints(v, o->viewport, 4);
            o->have_viewport = 1;
        } else if (!strcmp(key, "dither")) {
            o->dither = atoi(v) != 0;
        } else if (!strcmp(key, "prim")) {
            bad = 1;
            for (int k = 0; k < TRI_NPRIMS; k++)
                if (!strcmp(TRI_PRIMS[k].name, v)) {
                    o->prim_kind = k;
                    o->prim = TRI_PRIMS[k].prim;
                    bad = 0;
                }
        } else if (!strcmp(key, "scale")) {
            bad = tri_floats(v, &o->scale, 1);
        } else if (!strcmp(key, "shift")) {
            bad = tri_floats(v, o->shift, 2);
        } else if (!strcmp(key, "varying")) {
            o->varying = 1;
        } else if (!strcmp(key, "draws")) {
            o->draws = atoi(v);
            bad = o->draws < 1 || o->draws > 4096;
        } else if (!strcmp(key, "flush")) {
            o->flush = 1;
        } else if (!strcmp(key, "frames")) {
            o->frames = atoi(v);
            bad = o->frames < 1 || o->frames > 8;
        } else if (!strcmp(key, "clearonce")) {
            o->clear_once = 1;
        } else if (!strcmp(key, "tex") || !strcmp(key, "fbo")) {
            int w = 0, h = 0, n = -1;
            bad = sscanf(v, "%dx%d%n", &w, &h, &n) != 2 || n < 0 || v[n] || w < 1 || h < 1
                || w > TRI_TEX_MAX || h > TRI_TEX_MAX;
            if (key[0] == 't') { o->tex_w = w; o->tex_h = h; }
            else { o->fbo_w = w; o->fbo_h = h; }
        } else if (!strcmp(key, "texfmt")) {
            bad = 1;
            for (int k = 0; k < TRI_NTEXFMTS; k++)
                if (!strcmp(v, TRI_TEXFMTS[k].name)) { o->tex_kind = k; bad = 0; }
        } else if (!strcmp(key, "texfilter")) {
            o->tex_mip = !strcmp(v, "mipmap");
            if (!strcmp(v, "nearest")) o->tex_min = o->tex_mag = 0x2600;
            else if (!strcmp(v, "linear")) o->tex_min = o->tex_mag = 0x2601;
            else if (o->tex_mip) { o->tex_min = 0x2703; o->tex_mag = 0x2601; }
            else bad = 1;
        } else if (!strcmp(key, "texwrap") || !strcmp(key, "texwraps")) {
            bad = tri_lookup(TRI_WRAPS, v, &o->tex_wrap);
        } else if (!strcmp(key, "texwrapt")) {
            bad = tri_lookup(TRI_WRAPS, v, &o->tex_wrap_t);
            o->tex_wrap_t_set = 1;
        } else if (!strcmp(key, "texmin")) {
            static const struct tri_name MINS[] = {
                { "nearest", 0x2600 }, { "linear", 0x2601 }, { "nmn", 0x2700 },
                { "lmn", 0x2701 }, { "nml", 0x2702 }, { "lml", 0x2703 }, { 0, 0 },
            };
            bad = tri_lookup(MINS, v, &o->tex_min);
            o->tex_mip = !bad && o->tex_min >= 0x2700;
        } else if (!strcmp(key, "texmag")) {
            static const struct tri_name MAGS[] = {
                { "nearest", 0x2600 }, { "linear", 0x2601 }, { 0, 0 },
            };
            bad = tri_lookup(MAGS, v, &o->tex_mag);
        } else if (!strcmp(key, "tex2")) {
            o->tex2 = 1;
        } else if (!strcmp(key, "cube")) {
            o->cube = 1;
        } else if (!strcmp(key, "texsub")) {
            o->texsub = 1;
        } else if (!strcmp(key, "copytex")) {
            o->copytex = 1;
        } else if (!strcmp(key, "readback")) {
            o->readback = 1;
        } else if (!strcmp(key, "vsfile") || !strcmp(key, "fsfile")) {
            char *dst = key[0] == 'v' ? o->vsfile : o->fsfile;
            FILE *f = fopen(v, "r");
            bad = !f || strlen(v) >= sizeof o->vsfile;
            if (f)
                fclose(f);
            if (!bad)
                snprintf(dst, sizeof o->vsfile, "%s", v);
        } else if (!strcmp(key, "uniform") || !strcmp(key, "uniformi") ||
                   !strcmp(key, "uniformm")) {
            const char *colon = strchr(v, ':');
            struct tri_uniform *u = &o->uni[o->nuniforms];
            bad = !colon || colon == v || colon - v >= (int)sizeof u->name || o->nuniforms >= 8;
            if (!bad) {
                memset(u, 0, sizeof *u);
                memcpy(u->name, v, (size_t)(colon - v));
                u->kind = key[7] ? key[7] : 'f';
                if (u->kind == 'm') {
                    int k = atoi(colon + 1);
                    bad = k < 2 || k > 4;
                    u->n = k * k;
                    for (int j = 0; j < u->n; j++) u->f[j] = (float)(j + 1);
                } else {
                    char *end;
                    const char *q = colon + 1;
                    do {
                        u->f[u->n++] = strtof(q, &end);
                        bad |= end == q;
                        q = end + (*end == ',');
                    } while (*end == ',' && u->n < 5);
                    bad |= *end || u->n > 4 || (u->kind == 'i' && u->n != 1);
                }
                o->nuniforms += !bad;
            }
        } else if (!strcmp(key, "attrfmt")) {
            bad = 1;
            for (int k = 0; k < TRI_NATTRFMTS; k++)
                if (!strcmp(v, TRI_ATTRFMTS[k].name)) { o->attr_kind = k; bad = 0; }
        } else if (!strcmp(key, "attrnorm")) {
            o->attr_norm = 1;
        } else if (!strcmp(key, "attrsize")) {
            o->attr_size = atoi(v);
            bad = o->attr_size < 2 || o->attr_size > 4;
        } else if (!strcmp(key, "stride")) {
            o->stride = atoi(v);
            bad = o->stride < 4 || o->stride > 64 || o->stride % 4;
        } else if (!strcmp(key, "vbo")) {
            o->vbo = 1;
        } else if (!strcmp(key, "samples")) {
            o->samples = atoi(v);
            bad = o->samples != 2 && o->samples != 4;
        } else if (!strcmp(key, "polyoffset")) {
            o->polyoffset = 1;
            bad = sscanf(v, "%f,%f", &o->poly_factor, &o->poly_units) != 2;
        } else if (!strcmp(key, "fbosamples")) {
            o->fbo_samples = atoi(v);
            bad = o->fbo_samples != 2 && o->fbo_samples != 4;
        } else if (!strcmp(key, "fbodepth")) {
            o->fbo_depth = 1;
        } else if (!strcmp(key, "a2c")) {
            o->a2c = 1;
        } else if (!strcmp(key, "samplecov")) {
            char inv[8] = "";
            int n = sscanf(v, "%f,%7s", &o->samplecov_v, inv);
            o->samplecov = 1;
            o->samplecov_inv = n == 2 && !strcmp(inv, "inv");
            bad = n < 1 || (n == 2 && !o->samplecov_inv) || o->samplecov_v < 0 ||
                  o->samplecov_v > 1;
        } else if (!strcmp(key, "linewidth")) {
            o->linewidth = (float)atof(v);
            bad = o->linewidth <= 0 || o->linewidth > 64;
        } else if (!strcmp(key, "hint")) {
            char t[8] = "", m[8] = "";
            bad = sscanf(v, "%7[a-z],%7[a-z]", t, m) != 2;
            o->hint_target = !strcmp(t, "deriv") ? 0x8B8B : !strcmp(t, "mipmap") ? 0x8192 : 0;
            o->hint_mode = !strcmp(m, "fastest") ? 0x1101 : !strcmp(m, "nicest") ? 0x1102 : 0;
            bad |= !o->hint_target || !o->hint_mode;
        } else if (!strcmp(key, "stream")) {
            char f[8] = "";
            unsigned sw = 64, sh = 64;
            int n = sscanf(v, "%7[a-z0-9],%ux%u", f, &sw, &sh);
            struct bc_config bc;
            char cfg[24];
            snprintf(cfg, sizeof cfg, "%s,%ux%u", f, sw, sh);
            bad = (n != 1 && n != 3) || bc_parse(&bc, cfg) || sh % 2;
            if (!bad)
                snprintf(o->stream, sizeof o->stream, "%s", cfg);
        } else {
            snprintf(err, errn, "unknown option %s", a);
            return -1;
        }
        if (bad) {
            snprintf(err, errn, "bad %s: %s", key, v);
            return -1;
        }
    }
    const char *why = 0;
    if (o->tex_w && o->varying)
        why = "tex and varying both feed the fragment colour";
    else if (o->tex2 && !o->tex_w)
        why = "tex2 needs tex";
    else if (o->texsub && !o->tex_w)
        why = "texsub needs tex";
    else if (o->cube && (!o->tex_w || o->tex_w != o->tex_h))
        why = "cube needs a square tex";
    else if (o->cube && o->tex2)
        why = "cube and tex2 together are not drawn";
    else if ((o->vsfile[0] || o->fsfile[0]) && (o->tex_w || o->varying || o->fbo_w))
        why = "fsfile and tex, varying or fbo both choose the shaders";
    else if ((o->attr_kind || o->attr_size != 4 || o->stride || o->vbo) &&
             (o->draws != 1 || o->varying || o->fbo_w))
        why = "attribute options need draws=1 and no varying or fbo";
    else if (o->stride && o->stride < o->attr_size * TRI_ATTRFMTS[o->attr_kind].bytes)
        why = "bad stride: smaller than a vertex";
    else if (o->tex_w && TRI_TEXFMTS[o->tex_kind].comp && o->tex_mip)
        why = "compressed textures take no mipmaps";
    else if (o->fbo_samples && !o->fbo_w)
        why = "fbosamples needs fbo";
    else if (o->fbo_depth && !o->fbo_w)
        why = "fbodepth needs fbo";
    else if (o->stream[0] && (o->tex_w || o->varying || o->fbo_w || o->vsfile[0] ||
                              o->fsfile[0]))
        why = "stream and tex, varying, fbo or shader files both choose the shaders";
    if (why) {
        snprintf(err, errn, "%s", why);
        return -1;
    }
    if (!o->tex_wrap_t_set)
        o->tex_wrap_t = o->tex_wrap;
    if (!o->have_viewport) {
        o->viewport[0] = o->viewport[1] = 0;
        o->viewport[2] = o->w;
        o->viewport[3] = o->h;
    }
    return 0;
}

/* Fill v (TRI_MAX_VERTS x TRI_VERT_FLOATS) and return the vertex count. */
static int tri_geometry(const struct tri_opts *o, float *v)
{
    int n = TRI_PRIMS[o->prim_kind].n;
    for (int i = 0; i < n; i++) {
        float *p = v + i * TRI_VERT_FLOATS;
        p[0] = TRI_SHAPE[o->prim_kind][i][0] * o->scale + o->shift[0];
        p[1] = TRI_SHAPE[o->prim_kind][i][1] * o->scale + o->shift[1];
        p[2] = o->z;
        p[3] = 1.0f;
        for (int c = 0; c < 4; c++) p[4 + c] = o->varying ? TRI_COLOURS[i % 3][c] : 0.0f;
    }
    return n;
}

/* The position attribute's bytes for attrfmt/attrsize/stride (v as tri_geometry fills
 * it): n vertices at the stride, which it returns. */
static int tri_attr_data(const struct tri_opts *o, const float *v, int n, unsigned char *out)
{
    int bytes = TRI_ATTRFMTS[o->attr_kind].bytes, kind = o->attr_kind;
    int st = o->stride ? o->stride : o->attr_size * bytes;
    memset(out, 0, (size_t)(st * n));
    for (int i = 0; i < n; i++)
        for (int c = 0; c < o->attr_size; c++) {
            float x = v[i * TRI_VERT_FLOATS + c];
            unsigned char *p = out + i * st + c * bytes;
            int is_unsigned = kind == 2 || kind == 4, max = bytes == 1 ? 127 : 32767;
            long q;
            if (kind == 0) {
                memcpy(p, &x, 4);
                continue;
            }
            if (o->attr_norm)
                q = lroundf(is_unsigned ? (x * 0.5f + 0.5f) * (2 * max + 1) : x * max);
            else
                q = lroundf(x * 8.0f + (is_unsigned ? 8.0f : 0.0f));
            for (int b = 0; b < bytes; b++) p[b] = (unsigned char)(q >> (8 * b));
        }
    return st;
}

/* Where draw k of a frame goes: right by 0.05 per draw, wrapping every 8. */
static void tri_draw_shift(const struct tri_opts *o, int k, float *dx, float *dy)
{
    (void)o;
    *dx = 0.05f * (float)(k % 8);
    *dy = 0.0f;
}

/* Write the texture's texels to buf (tex_w x tex_h, rows bottom up as glTexImage2D
 * reads them) and return the byte count. */
static int tri_texels(const struct tri_opts *o, unsigned char *buf)
{
    int bpp = TRI_TEXFMTS[o->tex_kind].bpp, n = 0, comp = TRI_TEXFMTS[o->tex_kind].comp;
    if (comp) {             /* a compressed image: its blocks' bytes count up */
        int size = tri_comp_size(comp, o->tex_w, o->tex_h);
        for (; n < size; n++) buf[n] = (unsigned char)n;
        return n;
    }
    for (int y = 0; y < o->tex_h; y++)
        for (int x = 0; x < o->tex_w; x++) {
            const unsigned char b[4] = { (unsigned char)x, (unsigned char)y,
                                         (unsigned char)(x ^ y), 0xff };
            if (bpp == 1)
                buf[n++] = (unsigned char)(x + 16 * y);
            else
                for (int k = 0; k < bpp; k++) buf[n++] = b[k % 4];
        }
    return n;
}

/* The shaders that sample a texture: the tex= triangle, and fbo='s second pass. */
#define TRI_TEX_VS "attribute vec4 pos;\nvarying vec2 uv;\n" \
    "void main() { gl_Position = pos; uv = pos.xy * 0.5 + 0.5; }\n"
#define TRI_TEX_FS "precision mediump float;\nuniform sampler2D tex;\nvarying vec2 uv;\n" \
    "void main() { gl_FragColor = texture2D(tex, uv); }\n"
#define TRI_TEX2_FS "precision mediump float;\nuniform sampler2D tex;\n" \
    "uniform sampler2D tex1;\nvarying vec2 uv;\n" \
    "void main() { gl_FragColor = texture2D(tex, uv) * texture2D(tex1, uv * 2.0); }\n"
#define TRI_STREAM_FS "#extension GL_IMG_texture_stream2 : require\n" \
    "precision mediump float;\nuniform samplerStreamIMG tex;\nvarying vec2 uv;\n" \
    "void main() { gl_FragColor = textureStreamIMG(tex, uv); }\n"
#define TRI_CUBE_FS "precision mediump float;\nuniform samplerCube tex;\nvarying vec2 uv;\n" \
    "void main() { gl_FragColor = textureCube(tex, vec3(uv * 2.0 - 1.0, 1.0)); }\n"

/* A shader file's text (vsfile=, fsfile=), at most 8 KiB. */
static const char *tri_shader_file(const char *path, char *buf, size_t n)
{
    FILE *f = fopen(path, "r");
    size_t len = f ? fread(buf, 1, n - 1, f) : 0;
    if (f)
        fclose(f);
    buf[len] = 0;
    return buf;
}

/* The default is the original frame's shader; points also set a point size. */
static const char *tri_vertex_shader(const struct tri_opts *o)
{
    static char vs[8192];
    if (o->vsfile[0])
        return tri_shader_file(o->vsfile, vs, sizeof vs);
    if (o->tex_w || o->stream[0])
        return TRI_TEX_VS;
    if (o->varying)
        return "attribute vec4 pos;\nattribute vec4 colour;\nvarying vec4 col;\n"
               "void main() { gl_Position = pos; col = colour; }\n";
    if (o->prim == 0x0000)
        return "attribute vec4 pos;\nvoid main() { gl_Position = pos; gl_PointSize = 4.0; }\n";
    return "attribute vec4 pos;\nvoid main() { gl_Position = pos; }\n";
}

static const char *tri_fragment_shader(const struct tri_opts *o)
{
    static char fs[256], ff[8192];
    if (o->fsfile[0])
        return tri_shader_file(o->fsfile, ff, sizeof ff);
    if (o->stream[0])
        return TRI_STREAM_FS;
    if (o->tex_w)
        return o->cube ? TRI_CUBE_FS : o->tex2 ? TRI_TEX2_FS : TRI_TEX_FS;
    if (o->varying)
        return "precision mediump float;\nvarying vec4 col;\n"
               "void main() { gl_FragColor = col; }\n";
    snprintf(fs, sizeof fs, "precision mediump float;\nvoid main() { gl_FragColor = "
             "vec4(%.4f, %.4f, %.4f, %.4f); }\n",
             o->color[0], o->color[1], o->color[2], o->color[3]);
    return fs;
}

static void tri_dump(FILE *f, const struct tri_opts *o)
{
    fprintf(f, "size %dx%d\nformat %d\n", o->w, o->h, o->format);
    fprintf(f, "color %g %g %g %g\n", o->color[0], o->color[1], o->color[2], o->color[3]);
    if (o->do_clear)
        fprintf(f, "clear %g %g %g %g\n", o->clear[0], o->clear[1], o->clear[2], o->clear[3]);
    else
        fprintf(f, "clear none\n");
    if (o->depth_func)
        fprintf(f, "depth %#x clear=%g write=%d\n", o->depth_func, o->clear_depth,
                o->depth_write);
    else
        fprintf(f, "depth off\n");
    if (o->stencil_func)
        fprintf(f, "stencil %#x ref=%d mask=%#x write=%#x ops=%#x,%#x,%#x\n", o->stencil_func,
                o->stencil_ref, o->stencil_mask, o->stencil_write, o->stencil_ops[0],
                o->stencil_ops[1], o->stencil_ops[2]);
    else
        fprintf(f, "stencil off\n");
    fprintf(f, "stencilops %#x %#x %#x\n", o->stencil_ops[0], o->stencil_ops[1],
            o->stencil_ops[2]);
    fprintf(f, "depthrange %g %g\n", o->depth_range[0], o->depth_range[1]);
    if (o->blend_eq)
        fprintf(f, "blend %#x %#x eq=%#x\n", o->blend_src, o->blend_dst, o->blend_eq);
    else
        fprintf(f, "blend off\n");
    if (o->cull)
        fprintf(f, "cull %#x front=%#x\n", o->cull, o->front_face);
    else
        fprintf(f, "cull off\n");
    fprintf(f, "mask %d%d%d%d\n", o->mask[0], o->mask[1], o->mask[2], o->mask[3]);
    if (o->do_scissor)
        fprintf(f, "scissor %d %d %d %d\n", o->scissor[0], o->scissor[1], o->scissor[2],
                o->scissor[3]);
    else
        fprintf(f, "scissor off\n");
    fprintf(f, "viewport %d %d %d %d\n", o->viewport[0], o->viewport[1], o->viewport[2],
            o->viewport[3]);
    fprintf(f, "dither %d\nprim 0x%x\nvarying %d\n", o->dither, o->prim, o->varying);
    fprintf(f, "draws %d flush=%d\nframes %d clearonce=%d\n", o->draws, o->flush,
            o->frames, o->clear_once);
    if (o->tex_w)
        fprintf(f, "tex %dx%d fmt=%#x,%#x bpp=%d filter=%#x,%#x mip=%d wrap=%#x wrapt=%#x\n",
                o->tex_w, o->tex_h, TRI_TEXFMTS[o->tex_kind].format,
                TRI_TEXFMTS[o->tex_kind].type, TRI_TEXFMTS[o->tex_kind].bpp, o->tex_min,
                o->tex_mag, o->tex_mip, o->tex_wrap, o->tex_wrap_t);
    else
        fprintf(f, "tex off\n");
    if (o->fbo_w)
        fprintf(f, "fbo %dx%d\n", o->fbo_w, o->fbo_h);
    else
        fprintf(f, "fbo off\n");
    fprintf(f, "tex2 %d\ncube %d\ntexsub %d\ncopytex %d\nreadback %s\nsamples %d\n", o->tex2,
            o->cube, o->texsub, o->copytex, o->readback ? "full" : "1x1", o->samples);
    if (o->polyoffset)
        fprintf(f, "polyoffset %g,%g\n", o->poly_factor, o->poly_units);
    else
        fprintf(f, "polyoffset off\n");
    fprintf(f, "fbosamples %d\nfbodepth %d\n", o->fbo_samples, o->fbo_depth);
    fprintf(f, "stream %s\n", o->stream[0] ? o->stream : "off");
    fprintf(f, "a2c %d\n", o->a2c);
    if (o->samplecov)
        fprintf(f, "samplecov %g,%d\n", o->samplecov_v, o->samplecov_inv);
    else
        fprintf(f, "samplecov off\n");
    fprintf(f, "linewidth %g\n", o->linewidth);
    if (o->hint_target)
        fprintf(f, "hint %#x,%#x\n", o->hint_target, o->hint_mode);
    else
        fprintf(f, "hint off\n");
    fprintf(f, "vsfile %s\nfsfile %s\n", o->vsfile[0] ? o->vsfile : "-",
            o->fsfile[0] ? o->fsfile : "-");
    fprintf(f, "uniforms %d\n", o->nuniforms);
    for (int k = 0; k < o->nuniforms; k++) {
        const struct tri_uniform *u = &o->uni[k];
        fprintf(f, "uniform%d %c %s %d", k, u->kind, u->name, u->n);
        for (int j = 0; j < u->n && j < 4; j++) fprintf(f, " %g", u->f[j]);
        fputc('\n', f);
    }
    fprintf(f, "attr %s size=%d norm=%d stride=%d vbo=%d\n", TRI_ATTRFMTS[o->attr_kind].name,
            o->attr_size, o->attr_norm, o->stride, o->vbo);
}

#endif
