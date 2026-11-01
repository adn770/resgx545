// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
/* xfer.c — run transfer-queue fills and copies through the closed Cedarview OpenVG
 * stack under the fake libdrm (fakedrm.so) and the fake window system
 * (libpvrFAKEWSEGL.so), so the shim captures each SGX_SUBMITTRANSFER with a snapshot
 * of device memory (README "Transfer captures"). The closed libraries are run as
 * black boxes, through the Khronos OpenVG 1.1 and EGL 1.4 APIs only.
 *
 * Arguments are steps, run in order; each fill and copy is followed by vgFinish:
 *
 *   img=NAME:FMT:WxH            vgCreateImage (FMT 8888 = sARGB_8888, x888 = sXRGB_8888,
 *                               565 = sRGB_565), quality non-antialiased
 *   fill=NAME:0xAARRGGBB:X,Y,W,H vgClearImage of that rectangle with that colour
 *   copy=DST:DX,DY:SRC:SX,SY,W,H vgCopyImage, no dither
 *
 * OpenVG rectangles have their origin at the bottom left. Every step is marked in the
 * bridge log (fakedrm_mark) and printed with its parameters.
 *
 * BUILD (i686): gcc -m32 xfer.c -o xfer -ldl
 * libEGL and libOpenVG are loaded with dlopen from $SGX_UK_DIR/lib; the constants and
 * prototypes used are the Khronos API values, declared below. */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "ukdir.h"

/* Khronos EGL 1.4 / OpenVG 1.1 API constants. */
#define EGL_NONE                0x3038
#define EGL_RED_SIZE            0x3024
#define EGL_GREEN_SIZE          0x3023
#define EGL_BLUE_SIZE           0x3022
#define EGL_ALPHA_SIZE          0x3021
#define EGL_SURFACE_TYPE        0x3033
#define EGL_RENDERABLE_TYPE     0x3040
#define EGL_PBUFFER_BIT         0x0001
#define EGL_OPENVG_BIT          0x0002
#define EGL_WIDTH               0x3057
#define EGL_HEIGHT              0x3056
#define EGL_OPENVG_API          0x30A1
#define VG_CLEAR_COLOR          0x1121
#define VG_sRGB_565             3
#define VG_sXRGB_8888           64
#define VG_sARGB_8888           65
#define VG_IMAGE_QUALITY_NONANTIALIASED 1

#define MAX_IMAGES 16

static void (*mark_fn)(const char *);

static void step(const char *what)
{
    printf("[xfer] %s\n", what);
    if (mark_fn) mark_fn(what);
}

static void *sym(void *lib, const char *name)
{
    void *p = dlsym(lib, name);
    if (!p) {
        fprintf(stderr, "xfer: missing symbol %s\n", name);
        exit(2);
    }
    return p;
}

static struct { char name[16]; unsigned h; } images[MAX_IMAGES];
static int nimages;

static unsigned image(const char *name)
{
    for (int i = 0; i < nimages; i++)
        if (!strcmp(images[i].name, name)) return images[i].h;
    fprintf(stderr, "xfer: no image %s\n", name);
    exit(2);
}

/* NAME:rest -> copies NAME into buf (at most n - 1 chars), returns rest. */
static const char *field(const char *s, char *buf, size_t n)
{
    const char *c = strchr(s, ':');
    size_t k = c ? (size_t)(c - s) : strlen(s);
    if (k >= n) k = n - 1;
    memcpy(buf, s, k);
    buf[k] = 0;
    return c ? c + 1 : s + strlen(s);
}

int main(int argc, char **argv)
{
    setvbuf(stdout, 0, _IONBF, 0);
    setenv("FAKEWSEGL_FORMAT", "8888", 1);      /* fakewsegl.c: an ARGB8888 configuration */
    mark_fn = (void (*)(const char *))dlsym(RTLD_DEFAULT, "fakedrm_mark");
    char path[UK_PATH_MAX];
    void *egl = dlopen(uk_path(path, sizeof path, "lib/libEGL.so.1"), RTLD_NOW | RTLD_GLOBAL);
    void *vg = egl ? dlopen(uk_path(path, sizeof path, "lib/libOpenVG.so.1"),
                            RTLD_NOW | RTLD_GLOBAL) : 0;
    if (!egl || !vg) {
        fprintf(stderr, "dlopen: %s\n", dlerror());
        return 1;
    }
    void *(*eglGetDisplay)(void *) = sym(egl, "eglGetDisplay");
    unsigned (*eglInitialize)(void *, int *, int *) = sym(egl, "eglInitialize");
    unsigned (*eglBindAPI)(unsigned) = sym(egl, "eglBindAPI");
    unsigned (*eglChooseConfig)(void *, const int *, void **, int, int *) =
        sym(egl, "eglChooseConfig");
    void *(*eglCreatePbufferSurface)(void *, void *, const int *) =
        sym(egl, "eglCreatePbufferSurface");
    void *(*eglCreateContext)(void *, void *, void *, const int *) =
        sym(egl, "eglCreateContext");
    unsigned (*eglMakeCurrent)(void *, void *, void *, void *) = sym(egl, "eglMakeCurrent");
    int (*eglGetError)(void) = sym(egl, "eglGetError");
    void (*vgSetfv)(int, int, const float *) = sym(vg, "vgSetfv");
    void (*vgFinish)(void) = sym(vg, "vgFinish");
    unsigned (*vgCreateImage)(int, int, int, unsigned) = sym(vg, "vgCreateImage");
    void (*vgClearImage)(unsigned, int, int, int, int) = sym(vg, "vgClearImage");
    void (*vgCopyImage)(unsigned, int, int, unsigned, int, int, int, int, int) =
        sym(vg, "vgCopyImage");
    int (*vgGetError)(void) = sym(vg, "vgGetError");

    void *dpy = eglGetDisplay((void *)0);
    int major = 0, minor = 0;
    if (!eglInitialize(dpy, &major, &minor)) {
        printf("[xfer] eglInitialize failed: %#x\n", eglGetError());
        return 1;
    }
    eglBindAPI(EGL_OPENVG_API);
    const int cfg_attr[] = { EGL_SURFACE_TYPE, EGL_PBUFFER_BIT, EGL_RENDERABLE_TYPE,
        EGL_OPENVG_BIT, EGL_RED_SIZE, 8, EGL_GREEN_SIZE, 8, EGL_BLUE_SIZE, 8,
        EGL_ALPHA_SIZE, 8, EGL_NONE };
    void *cfg = 0;
    int ncfg = 0;
    if (!eglChooseConfig(dpy, cfg_attr, &cfg, 1, &ncfg) || ncfg < 1) {
        printf("[xfer] eglChooseConfig failed: %#x\n", eglGetError());
        return 1;
    }
    const int pb_attr[] = { EGL_WIDTH, 16, EGL_HEIGHT, 16, EGL_NONE };
    void *surf = eglCreatePbufferSurface(dpy, cfg, pb_attr);
    void *ctx = surf ? eglCreateContext(dpy, cfg, (void *)0, 0) : 0;
    if (!ctx || !eglMakeCurrent(dpy, surf, surf, ctx)) {
        printf("[xfer] EGL setup failed: %#x\n", eglGetError());
        return 1;
    }

    char what[160], a[16], b[16];
    for (int k = 1; k < argc; k++) {
        const char *s = argv[k];
        int x, y, w, h, dx, dy;
        unsigned c;
        if (!strncmp(s, "img=", 4)) {
            const char *r = field(field(s + 4, a, sizeof a), b, sizeof b);
            if (nimages == MAX_IMAGES || sscanf(r, "%dx%d", &w, &h) != 2) goto bad;
            int fmt = !strcmp(b, "8888") ? VG_sARGB_8888 : !strcmp(b, "x888") ? VG_sXRGB_8888
                    : !strcmp(b, "565") ? VG_sRGB_565 : -1;
            if (fmt < 0) goto bad;
            snprintf(what, sizeof what, "img %s fmt=%s size=%dx%d", a, b, w, h);
            step(what);
            snprintf(images[nimages].name, sizeof images[nimages].name, "%s", a);
            images[nimages++].h = vgCreateImage(fmt, w, h, VG_IMAGE_QUALITY_NONANTIALIASED);
            vgFinish();
        } else if (!strncmp(s, "fill=", 5)) {
            const char *r = field(field(s + 5, a, sizeof a), b, sizeof b);
            if (sscanf(b, "%x", &c) != 1 || sscanf(r, "%d,%d,%d,%d", &x, &y, &w, &h) != 4)
                goto bad;
            float f[4] = { (c >> 16 & 0xff) / 255.0f, (c >> 8 & 0xff) / 255.0f,
                           (c & 0xff) / 255.0f, (c >> 24) / 255.0f };
            snprintf(what, sizeof what, "fill %s colour=0x%08x rect=%d,%d,%d,%d", a, c, x, y,
                     w, h);
            step(what);
            vgSetfv(VG_CLEAR_COLOR, 4, f);
            vgClearImage(image(a), x, y, w, h);
            vgFinish();
        } else if (!strncmp(s, "copy=", 5)) {
            char d2[16];
            const char *r = field(s + 5, a, sizeof a);
            r = field(r, d2, sizeof d2);
            r = field(r, b, sizeof b);
            if (sscanf(d2, "%d,%d", &dx, &dy) != 2 ||
                sscanf(r, "%d,%d,%d,%d", &x, &y, &w, &h) != 4)
                goto bad;
            snprintf(what, sizeof what, "copy %s pos=%d,%d from %s rect=%d,%d,%d,%d", a, dx,
                     dy, b, x, y, w, h);
            step(what);
            vgCopyImage(image(a), dx, dy, image(b), x, y, w, h, 0);
            vgFinish();
        } else {
            goto bad;
        }
        int e = vgGetError();
        if (e) {
            printf("[xfer] %s: VG error %#x\n", s, e);
            return 1;
        }
        continue;
bad:
        fprintf(stderr, "xfer: bad step %s\n", s);
        return 2;
    }
    step("done");
    return 0;
}
