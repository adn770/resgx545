// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
/* tri1opts.h: the options of tri1.c, the GLES1 (fixed-function) sibling of tri.c.
 *
 * Every option changes one piece of fixed-function state against the default frame (a
 * constant-colour triangle on a blue clear, 64x64 RGB565), so its capture diffs against
 * the default one (diff3d.py). Options are key=value words:
 *
 *   size=WxH, format=565|8888, color=r,g,b,a (glColor4f), clear=r,g,b,a
 *   prim=tri|points|lines, pointsize=N (glPointSize)
 *   vcolor              a colour array (red, green, blue vertices); shade=flat
 *   tex=WxH             a texture on unit 0 (texel bytes x, y, x ^ y, 0xff), coordinates
 *                       from the positions; texenv=modulate|replace|decal|blend|add,
 *                       combine=replace|modulate|add|addsigned|interpolate|subtract|dot3
 *                       (GL_COMBINE with that RGB operation)
 *   tex2                the same texture on unit 1 too; texenv2=MODE for it
 *   fog=linear|exp|exp2 light (GL_LIGHT0, a normal array) alphatest=FUNC,REF
 *   rotate=DEG          glRotatef about z on the modelview; clip: a clip plane x <= 0.25
 *
 * The values are the Khronos GLES 1.1 API constants. */
#ifndef TRI1OPTS_H
#define TRI1OPTS_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct tri1_opts {
    int w, h, format;
    float color[4], clear[4];
    unsigned prim;
    float pointsize;
    int vcolor;
    unsigned shade;
    int tex_w, tex_h, tex2;
    unsigned texenv, combine, texenv2;
    int have_texenv;
    unsigned fog;
    int light;
    unsigned alpha_func;
    float alpha_ref;
    float rotate;
    int clip;
};

struct tri1_name { const char *name; unsigned value; };

static const struct tri1_name TRI1_ENVS[] = {
    { "modulate", 0x2100 }, { "replace", 0x1E01 }, { "decal", 0x2101 }, { "blend", 0x0BE2 },
    { "add", 0x0104 }, { 0, 0 },
};
static const struct tri1_name TRI1_COMBINES[] = {
    { "replace", 0x1E01 }, { "modulate", 0x2100 }, { "add", 0x0104 },
    { "addsigned", 0x8574 }, { "interpolate", 0x8575 }, { "subtract", 0x84E7 },
    { "dot3", 0x86AE }, { 0, 0 },
};
static const struct tri1_name TRI1_FOGS[] = {
    { "linear", 0x2601 }, { "exp", 0x0800 }, { "exp2", 0x0801 }, { 0, 0 },
};
static const struct tri1_name TRI1_FUNCS[] = {
    { "never", 0x0200 }, { "less", 0x0201 }, { "equal", 0x0202 }, { "lequal", 0x0203 },
    { "greater", 0x0204 }, { "notequal", 0x0205 }, { "gequal", 0x0206 },
    { "always", 0x0207 }, { 0, 0 },
};
static const struct tri1_name TRI1_PRIMS[] = {
    { "tri", 0x0004 }, { "points", 0x0000 }, { "lines", 0x0001 }, { 0, 0 },
};

static int tri1_lookup(const struct tri1_name *t, const char *s, unsigned *out)
{
    for (; t->name; t++)
        if (!strcmp(t->name, s)) { *out = t->value; return 0; }
    return -1;
}

static int tri1_floats(const char *s, float *out, int n)
{
    char *end;
    for (int i = 0; i < n; i++) {
        out[i] = strtof(s, &end);
        if (end == s || (i + 1 < n ? *end != ',' : *end))
            return -1;
        s = end + 1;
    }
    return 0;
}

static void tri1_defaults(struct tri1_opts *o)
{
    static const struct tri1_opts d = {
        .w = 64, .h = 64, .format = 565, .color = { 1.0f, 0.5f, 0.25f, 1.0f },
        .clear = { 0.0f, 0.0f, 1.0f, 1.0f }, .prim = 0x0004, .shade = 0x1D01,
        .texenv = 0x2100, .texenv2 = 0x2100,
    };
    *o = d;
}

/* Parse key=value words; 0 on success, else -1 with a message in err. */
static int tri1_parse(struct tri1_opts *o, int argc, char **argv, char *err, size_t errn)
{
    tri1_defaults(o);
    for (int i = 0; i < argc; i++) {
        char key[32];
        const char *a = argv[i], *eq = strchr(a, '=');
        const char *v = eq ? eq + 1 : "";
        size_t kl = eq ? (size_t)(eq - a) : strlen(a);
        int bad = 0;
        snprintf(key, sizeof key, "%.*s", (int)kl, a);
        if (!strcmp(key, "size") || !strcmp(key, "tex")) {
            int w = 0, h = 0, n = -1;
            bad = sscanf(v, "%dx%d%n", &w, &h, &n) != 2 || n < 0 || v[n] || w < 1 || h < 1 ||
                  w > 2048 || h > 2048;
            if (key[0] == 's') { o->w = w; o->h = h; } else { o->tex_w = w; o->tex_h = h; }
        } else if (!strcmp(key, "format")) {
            o->format = atoi(v);
            bad = o->format != 565 && o->format != 8888;
        } else if (!strcmp(key, "color")) {
            bad = tri1_floats(v, o->color, 4);
        } else if (!strcmp(key, "clear")) {
            bad = tri1_floats(v, o->clear, 4);
        } else if (!strcmp(key, "prim")) {
            bad = tri1_lookup(TRI1_PRIMS, v, &o->prim);
        } else if (!strcmp(key, "pointsize")) {
            o->pointsize = strtof(v, 0);
            bad = o->pointsize <= 0;
        } else if (!strcmp(key, "vcolor")) {
            o->vcolor = 1;
        } else if (!strcmp(key, "shade")) {
            bad = strcmp(v, "flat");
            o->shade = 0x1D00;
        } else if (!strcmp(key, "texenv")) {
            bad = tri1_lookup(TRI1_ENVS, v, &o->texenv);
            o->have_texenv = 1;
        } else if (!strcmp(key, "combine")) {
            bad = tri1_lookup(TRI1_COMBINES, v, &o->combine);
            o->texenv = 0x8570;
            o->have_texenv = 1;
        } else if (!strcmp(key, "tex2")) {
            o->tex2 = 1;
        } else if (!strcmp(key, "texenv2")) {
            bad = tri1_lookup(TRI1_ENVS, v, &o->texenv2);
        } else if (!strcmp(key, "fog")) {
            bad = tri1_lookup(TRI1_FOGS, v, &o->fog);
        } else if (!strcmp(key, "light")) {
            o->light = 1;
        } else if (!strcmp(key, "alphatest")) {
            char f[16] = "";
            const char *c = strchr(v, ',');
            bad = !c || c - v >= (int)sizeof f;
            if (!bad) {
                memcpy(f, v, (size_t)(c - v));
                bad = tri1_lookup(TRI1_FUNCS, f, &o->alpha_func) || tri1_floats(c + 1,
                                                                               &o->alpha_ref, 1);
            }
        } else if (!strcmp(key, "rotate")) {
            bad = tri1_floats(v, &o->rotate, 1);
        } else if (!strcmp(key, "clip")) {
            o->clip = 1;
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
    if (o->tex2 && !o->tex_w)
        why = "tex2 needs tex";
    else if (o->have_texenv && !o->tex_w)
        why = "texenv needs tex";
    if (why) {
        snprintf(err, errn, "%s", why);
        return -1;
    }
    return 0;
}

static void tri1_dump(FILE *f, const struct tri1_opts *o)
{
    fprintf(f, "size %dx%d\nformat %d\n", o->w, o->h, o->format);
    fprintf(f, "color %g %g %g %g\n", o->color[0], o->color[1], o->color[2], o->color[3]);
    fprintf(f, "clear %g %g %g %g\n", o->clear[0], o->clear[1], o->clear[2], o->clear[3]);
    fprintf(f, "prim 0x%x\nvcolor %d\nshade %#x\n", o->prim, o->vcolor, o->shade);
    if (o->tex_w && o->texenv == 0x8570)
        fprintf(f, "tex %dx%d env=%#x combine=%#x\n", o->tex_w, o->tex_h, o->texenv, o->combine);
    else if (o->tex_w)
        fprintf(f, "tex %dx%d env=%#x\n", o->tex_w, o->tex_h, o->texenv);
    else
        fprintf(f, "tex off\n");
    if (o->tex2)
        fprintf(f, "tex2 env=%#x\n", o->texenv2);
    else
        fprintf(f, "tex2 off\n");
    if (o->fog)
        fprintf(f, "fog %#x\n", o->fog);
    else
        fprintf(f, "fog off\n");
    fprintf(f, "light %s\n", o->light ? "on" : "off");
    if (o->alpha_func)
        fprintf(f, "alphatest %#x %g\n", o->alpha_func, o->alpha_ref);
    else
        fprintf(f, "alphatest off\n");
    if (o->rotate)
        fprintf(f, "rotate %g\n", o->rotate);
    else
        fprintf(f, "rotate off\n");
    if (o->pointsize)
        fprintf(f, "pointsize %g\n", o->pointsize);
    else
        fprintf(f, "pointsize off\n");
    fprintf(f, "clip %s\n", o->clip ? "on" : "off");
}

#endif
