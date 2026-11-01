// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
/* tri1.c: tri.c for GLES1, draw one triangle with EGL + the closed fixed-function
 * GLES 1.1 library (libGLES_CM) into a 64x64 pbuffer, then glFinish and exit. Run under
 * fakedrm.so and libpvrFAKEWSEGL.so as tri is, so the closed stack generates its own USSE
 * and PDS programs for the fixed-function state and submits them (README "3D capture").
 *
 * key=value arguments (tri1opts.h) change one piece of fixed-function state at a time:
 * the texture environment and combiners, two texture units, fog, lighting, alpha test,
 * colour arrays, flat shading, a modelview rotation, points and a clip plane.
 *
 * BUILD (i686): gcc -m32 tri1.c -o tri1 -ldl
 * The closed libraries are loaded with dlopen from $SGX_UK_DIR/lib; the few EGL/GLES1
 * constants and prototypes used are the Khronos API values, declared below. */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ucontext.h>
#include <unistd.h>

#include "tri1opts.h"
#include "ukdir.h"

/* Khronos EGL 1.4 / GLES 1.1 API constants. */
#define EGL_DEFAULT_DISPLAY     ((void *)0)
#define EGL_NO_CONTEXT          ((void *)0)
#define EGL_NONE                0x3038
#define EGL_RED_SIZE            0x3024
#define EGL_GREEN_SIZE          0x3023
#define EGL_BLUE_SIZE           0x3022
#define EGL_ALPHA_SIZE          0x3021
#define EGL_SURFACE_TYPE        0x3033
#define EGL_RENDERABLE_TYPE     0x3040
#define EGL_PBUFFER_BIT         0x0001
#define EGL_OPENGL_ES_BIT       0x0001
#define EGL_WIDTH               0x3057
#define EGL_HEIGHT              0x3056
#define EGL_CONTEXT_CLIENT_VERSION 0x3098
#define EGL_OPENGL_ES_API       0x30A0

#define GL_FLOAT                0x1406
#define GL_UNSIGNED_BYTE        0x1401
#define GL_RGBA                 0x1908
#define GL_COLOR_BUFFER_BIT     0x4000
#define GL_TEXTURE_2D           0x0DE1
#define GL_TEXTURE0             0x84C0
#define GL_TEXTURE_MAG_FILTER   0x2800
#define GL_TEXTURE_MIN_FILTER   0x2801
#define GL_NEAREST              0x2600
#define GL_TEXTURE_ENV          0x2300
#define GL_TEXTURE_ENV_MODE     0x2200
#define GL_COMBINE              0x8570
#define GL_COMBINE_RGB          0x8571
#define GL_SRC0_RGB             0x8580
#define GL_SRC1_RGB             0x8581
#define GL_SRC2_RGB             0x8582
#define GL_TEXTURE              0x1702
#define GL_PRIMARY_COLOR        0x8577
#define GL_CONSTANT             0x8576
#define GL_VERTEX_ARRAY         0x8074
#define GL_COLOR_ARRAY          0x8076
#define GL_TEXTURE_COORD_ARRAY  0x8078
#define GL_FOG                  0x0B60
#define GL_FOG_DENSITY          0x0B62
#define GL_FOG_START            0x0B63
#define GL_FOG_END              0x0B64
#define GL_FOG_MODE             0x0B65
#define GL_FOG_COLOR            0x0B66
#define GL_LIGHTING             0x0B50
#define GL_LIGHT0               0x4000
#define GL_POSITION             0x1203
#define GL_COLOR_MATERIAL       0x0B57
#define GL_ALPHA_TEST           0x0BC0
#define GL_MODELVIEW            0x1700
#define GL_CLIP_PLANE0          0x3000

static void on_fault(int sig, siginfo_t *si, void *uc)
{
    ucontext_t *c = (ucontext_t *)uc;
    fprintf(stderr, "\n*** SIG%d at pc=%#lx accessing addr=%p ***\n", sig,
            (unsigned long)c->uc_mcontext.gregs[REG_EIP], si->si_addr);
    _exit(139);
}

/* fakedrm.so exports fakedrm_mark(): phase markers in its bridge log. */
static void (*mark_fn)(const char *);

static void phase(const char *what)
{
    printf("[tri1] %s\n", what);
    if (mark_fn) mark_fn(what);
}

static void *sym(void *lib, const char *name)
{
    void *p = dlsym(lib, name);
    if (!p) {
        fprintf(stderr, "missing symbol %s\n", name);
        exit(2);
    }
    return p;
}

int main(int argc, char **argv)
{
    struct tri1_opts o;
    char err[128];
    if (tri1_parse(&o, argc - 1, argv + 1, err, sizeof err)) {
        fprintf(stderr, "tri1: %s\n", err);
        return 2;
    }
    tri1_dump(stdout, &o);
    if (o.format == 8888) setenv("FAKEWSEGL_FORMAT", "8888", 1);   /* fakewsegl.c */
    const int W = o.w, H = o.h;
    struct sigaction sa = { 0 };
    sa.sa_sigaction = on_fault;
    sa.sa_flags = SA_SIGINFO;
    sigaction(SIGSEGV, &sa, 0);
    sigaction(SIGBUS, &sa, 0);
    sigaction(SIGILL, &sa, 0);
    setvbuf(stdout, 0, _IONBF, 0);

    mark_fn = (void (*)(const char *))dlsym(RTLD_DEFAULT, "fakedrm_mark");
    char path[UK_PATH_MAX];
    void *egl = dlopen(uk_path(path, sizeof path, "lib/libEGL.so.1"), RTLD_NOW | RTLD_GLOBAL);
    void *gl = egl ? dlopen(uk_path(path, sizeof path, "lib/libGLES_CM.so.1"),
                            RTLD_NOW | RTLD_GLOBAL) : 0;
    if (!egl || !gl) {
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
    unsigned (*eglSwapBuffers)(void *, void *) = sym(egl, "eglSwapBuffers");
    unsigned (*eglTerminate)(void *) = sym(egl, "eglTerminate");
    int (*eglGetError)(void) = sym(egl, "eglGetError");

    void (*glViewport)(int, int, int, int) = sym(gl, "glViewport");
    void (*glClearColor)(float, float, float, float) = sym(gl, "glClearColor");
    void (*glClear)(unsigned) = sym(gl, "glClear");
    void (*glColor4f)(float, float, float, float) = sym(gl, "glColor4f");
    void (*glShadeModel)(unsigned) = sym(gl, "glShadeModel");
    void (*glEnable)(unsigned) = sym(gl, "glEnable");
    void (*glEnableClientState)(unsigned) = sym(gl, "glEnableClientState");
    void (*glVertexPointer)(int, unsigned, int, const void *) = sym(gl, "glVertexPointer");
    void (*glColorPointer)(int, unsigned, int, const void *) = sym(gl, "glColorPointer");
    void (*glTexCoordPointer)(int, unsigned, int, const void *) = sym(gl, "glTexCoordPointer");
    void (*glClientActiveTexture)(unsigned) = sym(gl, "glClientActiveTexture");
    void (*glActiveTexture)(unsigned) = sym(gl, "glActiveTexture");
    void (*glGenTextures)(int, unsigned *) = sym(gl, "glGenTextures");
    void (*glBindTexture)(unsigned, unsigned) = sym(gl, "glBindTexture");
    void (*glTexImage2D)(unsigned, int, int, int, int, int, unsigned, unsigned, const void *) =
        sym(gl, "glTexImage2D");
    void (*glTexParameteri)(unsigned, unsigned, int) = sym(gl, "glTexParameteri");
    void (*glTexEnvi)(unsigned, unsigned, int) = sym(gl, "glTexEnvi");
    void (*glFogf)(unsigned, float) = sym(gl, "glFogf");
    void (*glFogfv)(unsigned, const float *) = sym(gl, "glFogfv");
    void (*glLightfv)(unsigned, unsigned, const float *) = sym(gl, "glLightfv");
    void (*glNormal3f)(float, float, float) = sym(gl, "glNormal3f");
    void (*glAlphaFunc)(unsigned, float) = sym(gl, "glAlphaFunc");
    void (*glMatrixMode)(unsigned) = sym(gl, "glMatrixMode");
    void (*glRotatef)(float, float, float, float) = sym(gl, "glRotatef");
    void (*glPointSize)(float) = sym(gl, "glPointSize");
    void (*glClipPlanef)(unsigned, const float *) = sym(gl, "glClipPlanef");
    void (*glDrawArrays)(unsigned, int, int) = sym(gl, "glDrawArrays");
    void (*glFinish)(void) = sym(gl, "glFinish");
    void (*glReadPixels)(int, int, int, int, unsigned, unsigned, void *) =
        sym(gl, "glReadPixels");
    unsigned (*glGetError)(void) = sym(gl, "glGetError");

    phase("eglInitialize");
    void *dpy = eglGetDisplay(EGL_DEFAULT_DISPLAY);
    int major = 0, minor = 0;
    if (!eglInitialize(dpy, &major, &minor)) {
        printf("[tri1] eglInitialize failed: %#x\n", eglGetError());
        return 1;
    }
    eglBindAPI(EGL_OPENGL_ES_API);
    const int c8 = o.format == 8888;
    const int cfg_attr[] = { EGL_SURFACE_TYPE, EGL_PBUFFER_BIT,
        EGL_RENDERABLE_TYPE, EGL_OPENGL_ES_BIT, EGL_RED_SIZE, c8 ? 8 : 5,
        EGL_GREEN_SIZE, c8 ? 8 : 6, EGL_BLUE_SIZE, c8 ? 8 : 5, EGL_ALPHA_SIZE, c8 ? 8 : 0,
        EGL_NONE };
    void *cfg = 0;
    int ncfg = 0;
    if (!eglChooseConfig(dpy, cfg_attr, &cfg, 1, &ncfg) || ncfg < 1) {
        printf("[tri1] eglChooseConfig failed: %#x n=%d\n", eglGetError(), ncfg);
        return 1;
    }
    const int pb_attr[] = { EGL_WIDTH, W, EGL_HEIGHT, H, EGL_NONE };
    phase("eglCreatePbufferSurface");
    void *surf = eglCreatePbufferSurface(dpy, cfg, pb_attr);
    static const int ctx_attr[] = { EGL_CONTEXT_CLIENT_VERSION, 1, EGL_NONE };
    phase("eglCreateContext");
    void *ctx = surf ? eglCreateContext(dpy, cfg, EGL_NO_CONTEXT, ctx_attr) : 0;
    if (!ctx || !eglMakeCurrent(dpy, surf, surf, ctx)) {
        printf("[tri1] surface/context failed: %#x\n", eglGetError());
        return 1;
    }

    phase("state");
    static const float pos[] = { -0.5f, -0.5f, 0.5f, -0.5f, 0.0f, 0.5f };
    static const float uv[] = { 0.25f, 0.25f, 0.75f, 0.25f, 0.5f, 0.75f };
    static const float rgba[] = { 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1 };
    glViewport(0, 0, W, H);
    glClearColor(o.clear[0], o.clear[1], o.clear[2], o.clear[3]);
    glColor4f(o.color[0], o.color[1], o.color[2], o.color[3]);
    glEnableClientState(GL_VERTEX_ARRAY);
    glVertexPointer(2, GL_FLOAT, 0, pos);
    if (o.vcolor) {
        glEnableClientState(GL_COLOR_ARRAY);
        glColorPointer(4, GL_FLOAT, 0, rgba);
    }
    if (o.shade != 0x1D01)
        glShadeModel(o.shade);
    if (o.tex_w) {
        /* the same texture on each unit used; texel bytes x, y, x ^ y, 0xff */
        unsigned char *t = malloc((size_t)o.tex_w * o.tex_h * 4);
        for (int y = 0, n = 0; y < o.tex_h; y++)
            for (int x = 0; x < o.tex_w; x++, n += 4) {
                t[n] = (unsigned char)x;
                t[n + 1] = (unsigned char)y;
                t[n + 2] = (unsigned char)(x ^ y);
                t[n + 3] = 0xff;
            }
        for (int unit = 0; unit < (o.tex2 ? 2 : 1); unit++) {
            unsigned tex;
            glActiveTexture(GL_TEXTURE0 + unit);
            glClientActiveTexture(GL_TEXTURE0 + unit);
            glEnableClientState(GL_TEXTURE_COORD_ARRAY);
            glTexCoordPointer(2, GL_FLOAT, 0, uv);
            glGenTextures(1, &tex);
            glBindTexture(GL_TEXTURE_2D, tex);
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, o.tex_w, o.tex_h, 0, GL_RGBA,
                         GL_UNSIGNED_BYTE, t);
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
            glEnable(GL_TEXTURE_2D);
            unsigned env = unit ? o.texenv2 : o.texenv;
            glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, (int)env);
            if (!unit && env == GL_COMBINE) {
                glTexEnvi(GL_TEXTURE_ENV, GL_COMBINE_RGB, (int)o.combine);
                glTexEnvi(GL_TEXTURE_ENV, GL_SRC0_RGB, GL_TEXTURE);
                glTexEnvi(GL_TEXTURE_ENV, GL_SRC1_RGB, GL_PRIMARY_COLOR);
                glTexEnvi(GL_TEXTURE_ENV, GL_SRC2_RGB, GL_CONSTANT);
            }
        }
        free(t);
        glActiveTexture(GL_TEXTURE0);
    }
    if (o.fog) {
        static const float grey[] = { 0.5f, 0.5f, 0.5f, 1.0f };
        glEnable(GL_FOG);
        glFogf(GL_FOG_MODE, (float)o.fog);
        glFogf(GL_FOG_START, 0.0f);
        glFogf(GL_FOG_END, 1.0f);
        glFogf(GL_FOG_DENSITY, 0.5f);
        glFogfv(GL_FOG_COLOR, grey);
    }
    if (o.light) {
        static const float dir[] = { 0.0f, 0.0f, 1.0f, 0.0f };
        glEnable(GL_LIGHTING);
        glEnable(GL_LIGHT0);
        glEnable(GL_COLOR_MATERIAL);
        glLightfv(GL_LIGHT0, GL_POSITION, dir);
        glNormal3f(0.0f, 0.0f, 1.0f);
    }
    if (o.alpha_func) {
        glEnable(GL_ALPHA_TEST);
        glAlphaFunc(o.alpha_func, o.alpha_ref);
    }
    if (o.rotate) {
        glMatrixMode(GL_MODELVIEW);
        glRotatef(o.rotate, 0.0f, 0.0f, 1.0f);
    }
    if (o.pointsize)
        glPointSize(o.pointsize);
    if (o.clip) {
        static const float plane[] = { -1.0f, 0.0f, 0.0f, 0.25f };   /* x <= 0.25 */
        glClipPlanef(GL_CLIP_PLANE0, plane);
        glEnable(GL_CLIP_PLANE0);
    }
    printf("[tri1] state glGetError=%#x\n", glGetError());

    phase("glClear");
    glClear(GL_COLOR_BUFFER_BIT);
    phase("glDrawArrays");
    glDrawArrays(o.prim, 0, o.prim == 0x0001 ? 2 : 3);
    phase("glFinish");
    glFinish();
    unsigned char px[4] = { 0 };
    glReadPixels(W / 2, H / 2, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, px);
    printf("[tri1] centre pixel %02x%02x%02x%02x glGetError=%#x\n", px[0], px[1], px[2], px[3],
           glGetError());
    phase("eglSwapBuffers");
    eglSwapBuffers(dpy, surf);
    phase("eglTerminate");
    eglMakeCurrent(dpy, 0, 0, EGL_NO_CONTEXT);
    eglTerminate(dpy);
    printf("[tri1] done\n");
    return 0;
}
