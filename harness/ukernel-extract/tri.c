// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
/* tri.c: draw one constant-colour triangle with EGL + GLES2 into a 64x64
 * pbuffer, then glFinish and exit. Run under the fake libdrm (fakedrm.so) and
 * the fake window system (libpvrFAKEWSEGL.so) so the closed Cedarview GLES2
 * stack submits one TA + 3D render that the shim captures (README "3D capture").
 *
 * key=value arguments (triopts.h) change one piece of state at a time for
 * differential captures: size, pixel format, colours, depth, stencil, blending,
 * culling, colour mask, scissor, viewport, primitive type, vertex positions and
 * a varying colour. Without arguments it draws the original frame.
 *
 * BUILD (i686): gcc -m32 tri.c -o tri -ldl
 * The closed libEGL/libGLESv2 are loaded with dlopen from $SGX_UK_DIR/lib, so
 * the build needs no closed headers or libraries: the few EGL/GLES2 constants
 * and prototypes used are the Khronos API values, declared below. */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ucontext.h>
#include <unistd.h>

#include "triopts.h"
#include "ukdir.h"

/* Khronos EGL 1.4 / GLES 2.0 API constants. */
#define EGL_DEFAULT_DISPLAY     ((void *)0)
#define EGL_NO_CONTEXT          ((void *)0)
#define EGL_NONE                0x3038
#define EGL_RED_SIZE            0x3024
#define EGL_GREEN_SIZE          0x3023
#define EGL_BLUE_SIZE           0x3022
#define EGL_ALPHA_SIZE          0x3021
#define EGL_DEPTH_SIZE          0x3025
#define EGL_STENCIL_SIZE        0x3026
#define EGL_SURFACE_TYPE        0x3033
#define EGL_RENDERABLE_TYPE     0x3040
#define EGL_PBUFFER_BIT         0x0001
#define EGL_OPENGL_ES2_BIT      0x0004
#define EGL_WIDTH               0x3057
#define EGL_HEIGHT              0x3056
#define EGL_CONTEXT_CLIENT_VERSION 0x3098
#define EGL_OPENGL_ES_API       0x30A0

#define GL_TRIANGLES            0x0004
#define GL_TEXTURE_2D           0x0DE1
#define GL_TEXTURE_CUBE_MAP     0x8513
#define GL_TEXTURE_CUBE_MAP_POSITIVE_X 0x8515
#define GL_TEXTURE0             0x84C0
#define EGL_SAMPLES             0x3031
#define EGL_SAMPLE_BUFFERS      0x3032
#define GL_TEXTURE_MAG_FILTER   0x2800
#define GL_TEXTURE_MIN_FILTER   0x2801
#define GL_TEXTURE_WRAP_S       0x2802
#define GL_TEXTURE_WRAP_T       0x2803
#define GL_UNPACK_ALIGNMENT     0x0CF5
#define GL_FRAMEBUFFER          0x8D40
#define GL_COLOR_ATTACHMENT0    0x8CE0
#define GL_FLOAT                0x1406
#define GL_COLOR_BUFFER_BIT     0x4000
#define GL_FRAGMENT_SHADER      0x8B30
#define GL_VERTEX_SHADER        0x8B31
#define GL_COMPILE_STATUS       0x8B81
#define GL_LINK_STATUS          0x8B82
#define GL_RGBA                 0x1908
#define GL_UNSIGNED_BYTE        0x1401
#define GL_DEPTH_BUFFER_BIT     0x0100
#define GL_STENCIL_BUFFER_BIT   0x0400
#define GL_CULL_FACE            0x0B44
#define GL_DEPTH_TEST           0x0B71
#define GL_STENCIL_TEST         0x0B90
#define GL_DITHER               0x0BD0
#define GL_BLEND                0x0BE2
#define GL_SCISSOR_TEST         0x0C11
#define GL_POLYGON_OFFSET_FILL  0x8037
#define GL_TEXTURE_STREAM_IMG   0x8C0D   /* IMG_texture_stream(2) */
#define GL_TEXTURE_NUM_STREAM_DEVICES_IMG 0x8C0E
#define GL_TEXTURE_STREAM_DEVICE_WIDTH_IMG 0x8C0F
#define GL_TEXTURE_STREAM_DEVICE_HEIGHT_IMG 0x8EA0
#define GL_TEXTURE_STREAM_DEVICE_FORMAT_IMG 0x8EA1
#define GL_TEXTURE_STREAM_DEVICE_NUM_BUFFERS_IMG 0x8EA2
#define GL_EXTENSIONS           0x1F03
#define GL_RENDERBUFFER         0x8D41
#define GL_DEPTH_ATTACHMENT     0x8D00
#define GL_DEPTH_COMPONENT16    0x81A5
#define GL_KEEP                 0x1E00
#define GL_REPLACE              0x1E01

static void on_fault(int sig, siginfo_t *si, void *uc)
{
    ucontext_t *c = (ucontext_t *)uc;
    char line[512];
    fprintf(stderr, "\n*** SIG%d at pc=%#lx accessing addr=%p ***\n", sig,
            (unsigned long)c->uc_mcontext.gregs[REG_EIP], si->si_addr);
    FILE *m = fopen("/proc/self/maps", "r");
    while (m && fgets(line, sizeof line, m))
        if (strstr(line, " r-xp ") || strstr(line, " r--p 00000000"))
            fputs(line, stderr);
    _exit(139);
}

/* fakedrm.so exports fakedrm_mark(): phase markers in its bridge log. */
static void (*mark_fn)(const char *);

static void phase(const char *what)
{
    printf("[tri] %s\n", what);
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
    struct tri_opts o;
    char err[128];
    if (tri_parse(&o, argc - 1, argv + 1, err, sizeof err)) {
        fprintf(stderr, "tri: %s\n", err);
        return 2;
    }
    tri_dump(stdout, &o);
    if (o.format == 8888) setenv("FAKEWSEGL_FORMAT", "8888", 1);   /* fakewsegl.c */
    if (o.stream[0]) setenv("FAKEBC", o.stream, 1);                 /* fakedrm.c, bufclass.h */
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
    void *gl = egl ? dlopen(uk_path(path, sizeof path, "lib/libGLESv2.so.2"),
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

    unsigned (*glCreateShader)(unsigned) = sym(gl, "glCreateShader");
    void (*glShaderSource)(unsigned, int, const char **, const int *) = sym(gl, "glShaderSource");
    void (*glCompileShader)(unsigned) = sym(gl, "glCompileShader");
    void (*glGetShaderiv)(unsigned, unsigned, int *) = sym(gl, "glGetShaderiv");
    unsigned (*glCreateProgram)(void) = sym(gl, "glCreateProgram");
    void (*glAttachShader)(unsigned, unsigned) = sym(gl, "glAttachShader");
    void (*glBindAttribLocation)(unsigned, unsigned, const char *) =
        sym(gl, "glBindAttribLocation");
    void (*glLinkProgram)(unsigned) = sym(gl, "glLinkProgram");
    void (*glGetProgramiv)(unsigned, unsigned, int *) = sym(gl, "glGetProgramiv");
    void (*glUseProgram)(unsigned) = sym(gl, "glUseProgram");
    void (*glViewport)(int, int, int, int) = sym(gl, "glViewport");
    void (*glClearColor)(float, float, float, float) = sym(gl, "glClearColor");
    void (*glClear)(unsigned) = sym(gl, "glClear");
    void (*glVertexAttribPointer)(unsigned, int, unsigned, unsigned char, int, const void *) =
        sym(gl, "glVertexAttribPointer");
    void (*glEnableVertexAttribArray)(unsigned) = sym(gl, "glEnableVertexAttribArray");
    void (*glDrawArrays)(unsigned, int, int) = sym(gl, "glDrawArrays");
    void (*glFinish)(void) = sym(gl, "glFinish");
    void (*glFlush)(void) = sym(gl, "glFlush");
    void (*glReadPixels)(int, int, int, int, unsigned, unsigned, void *) =
        sym(gl, "glReadPixels");
    unsigned (*glGetError)(void) = sym(gl, "glGetError");
    void (*glEnable)(unsigned) = sym(gl, "glEnable");
    void (*glDisable)(unsigned) = sym(gl, "glDisable");
    void (*glDepthFunc)(unsigned) = sym(gl, "glDepthFunc");
    void (*glDepthMask)(unsigned char) = sym(gl, "glDepthMask");
    void (*glClearDepthf)(float) = sym(gl, "glClearDepthf");
    void (*glStencilFunc)(unsigned, int, unsigned) = sym(gl, "glStencilFunc");
    void (*glStencilOp)(unsigned, unsigned, unsigned) = sym(gl, "glStencilOp");
    void (*glStencilMask)(unsigned) = sym(gl, "glStencilMask");
    void (*glDepthRangef)(float, float) = sym(gl, "glDepthRangef");
    void (*glBlendFunc)(unsigned, unsigned) = sym(gl, "glBlendFunc");
    void (*glBlendEquation)(unsigned) = sym(gl, "glBlendEquation");
    void (*glCullFace)(unsigned) = sym(gl, "glCullFace");
    void (*glFrontFace)(unsigned) = sym(gl, "glFrontFace");
    void (*glColorMask)(unsigned char, unsigned char, unsigned char, unsigned char) =
        sym(gl, "glColorMask");
    void (*glScissor)(int, int, int, int) = sym(gl, "glScissor");
    void (*glGenTextures)(int, unsigned *) = sym(gl, "glGenTextures");
    void (*glBindTexture)(unsigned, unsigned) = sym(gl, "glBindTexture");
    void (*glTexImage2D)(unsigned, int, int, int, int, int, unsigned, unsigned, const void *) =
        sym(gl, "glTexImage2D");
    void (*glTexParameteri)(unsigned, unsigned, int) = sym(gl, "glTexParameteri");
    void (*glGenerateMipmap)(unsigned) = sym(gl, "glGenerateMipmap");
    void (*glPixelStorei)(unsigned, int) = sym(gl, "glPixelStorei");
    void (*glGenFramebuffers)(int, unsigned *) = sym(gl, "glGenFramebuffers");
    void (*glBindFramebuffer)(unsigned, unsigned) = sym(gl, "glBindFramebuffer");
    void (*glFramebufferTexture2D)(unsigned, unsigned, unsigned, unsigned, int) =
        sym(gl, "glFramebufferTexture2D");
    unsigned (*glCheckFramebufferStatus)(unsigned) = sym(gl, "glCheckFramebufferStatus");
    void (*glPolygonOffset)(float, float) = sym(gl, "glPolygonOffset");
    void (*glSampleCoverage)(float, unsigned char) = sym(gl, "glSampleCoverage");
    void (*glLineWidth)(float) = sym(gl, "glLineWidth");
    void (*glHint)(unsigned, unsigned) = sym(gl, "glHint");
    const char *(*glGetString)(unsigned) = sym(gl, "glGetString");
    void (*glGenRenderbuffers)(int, unsigned *) = sym(gl, "glGenRenderbuffers");
    void (*glBindRenderbuffer)(unsigned, unsigned) = sym(gl, "glBindRenderbuffer");
    void (*glRenderbufferStorage)(unsigned, unsigned, int, int) =
        sym(gl, "glRenderbufferStorage");
    void (*glFramebufferRenderbuffer)(unsigned, unsigned, unsigned, unsigned) =
        sym(gl, "glFramebufferRenderbuffer");
    void *(*eglGetProcAddress)(const char *) = sym(egl, "eglGetProcAddress");
    void (*glGetIntegerv)(unsigned, int *) = sym(gl, "glGetIntegerv");
    void (*glCompressedTexImage2D)(unsigned, int, unsigned, int, int, int, int, const void *) =
        sym(gl, "glCompressedTexImage2D");
    void (*glActiveTexture)(unsigned) = sym(gl, "glActiveTexture");
    int (*glGetUniformLocation)(unsigned, const char *) = sym(gl, "glGetUniformLocation");
    void (*glUniform1i)(int, int) = sym(gl, "glUniform1i");
    void (*glTexSubImage2D)(unsigned, int, int, int, int, int, unsigned, unsigned,
                            const void *) = sym(gl, "glTexSubImage2D");
    void (*glCopyTexImage2D)(unsigned, int, unsigned, int, int, int, int, int) =
        sym(gl, "glCopyTexImage2D");
    void (*glUniformNfv[4])(int, int, const float *) = {
        sym(gl, "glUniform1fv"), sym(gl, "glUniform2fv"), sym(gl, "glUniform3fv"),
        sym(gl, "glUniform4fv") };
    void (*glUniformMatrixNfv[3])(int, int, unsigned char, const float *) = {
        sym(gl, "glUniformMatrix2fv"), sym(gl, "glUniformMatrix3fv"),
        sym(gl, "glUniformMatrix4fv") };
    void (*glGenBuffers)(int, unsigned *) = sym(gl, "glGenBuffers");
    void (*glBindBuffer)(unsigned, unsigned) = sym(gl, "glBindBuffer");
    void (*glBufferData)(unsigned, long, const void *, unsigned) = sym(gl, "glBufferData");

    phase("eglGetDisplay");
    void *dpy = eglGetDisplay(EGL_DEFAULT_DISPLAY);
    int major = 0, minor = 0;
    phase("eglInitialize");
    if (!eglInitialize(dpy, &major, &minor)) {
        printf("[tri] eglInitialize failed: %#x\n", eglGetError());
        return 1;
    }
    printf("[tri] EGL %d.%d\n", major, minor);
    eglBindAPI(EGL_OPENGL_ES_API);

    const int c8 = o.format == 8888;
    int cfg_attr[] = { EGL_SURFACE_TYPE, EGL_PBUFFER_BIT,
        EGL_RENDERABLE_TYPE, EGL_OPENGL_ES2_BIT, EGL_RED_SIZE, c8 ? 8 : 5,
        EGL_GREEN_SIZE, c8 ? 8 : 6, EGL_BLUE_SIZE, c8 ? 8 : 5, EGL_ALPHA_SIZE, c8 ? 8 : 0,
        EGL_DEPTH_SIZE, o.depth_func ? 16 : 0, EGL_STENCIL_SIZE, o.stencil_func ? 8 : 0,
        EGL_NONE, 0, 0, 0, 0 };
    if (o.samples) {            /* samples=: the four spare words, before EGL_NONE */
        int n = (int)(sizeof cfg_attr / sizeof cfg_attr[0]) - 5;
        cfg_attr[n] = EGL_SAMPLE_BUFFERS;
        cfg_attr[n + 1] = 1;
        cfg_attr[n + 2] = EGL_SAMPLES;
        cfg_attr[n + 3] = o.samples;
        cfg_attr[n + 4] = EGL_NONE;
    }
    void *cfg = 0;
    int ncfg = 0;
    if (!eglChooseConfig(dpy, cfg_attr, &cfg, 1, &ncfg) || ncfg < 1) {
        printf("[tri] eglChooseConfig failed: %#x n=%d\n", eglGetError(), ncfg);
        return 1;
    }
    const int pb_attr[] = { EGL_WIDTH, W, EGL_HEIGHT, H, EGL_NONE };
    phase("eglCreatePbufferSurface");
    void *surf = eglCreatePbufferSurface(dpy, cfg, pb_attr);
    if (!surf) {
        printf("[tri] eglCreatePbufferSurface failed: %#x\n", eglGetError());
        return 1;
    }
    static const int ctx_attr[] = { EGL_CONTEXT_CLIENT_VERSION, 2, EGL_NONE };
    phase("eglCreateContext");
    void *ctx = eglCreateContext(dpy, cfg, EGL_NO_CONTEXT, ctx_attr);
    if (!ctx) {
        printf("[tri] eglCreateContext failed: %#x\n", eglGetError());
        return 1;
    }
    phase("eglMakeCurrent");
    if (!eglMakeCurrent(dpy, surf, surf, ctx)) {
        printf("[tri] eglMakeCurrent failed: %#x\n", eglGetError());
        return 1;
    }
    printf("[tri] GL_EXTENSIONS %s\n", glGetString(GL_EXTENSIONS));

    phase("compile and link");
    unsigned vs = glCreateShader(GL_VERTEX_SHADER), fs = glCreateShader(GL_FRAGMENT_SHADER);
    int ok = 0;
    const char *VS = tri_vertex_shader(&o), *FS = tri_fragment_shader(&o);
    glShaderSource(vs, 1, &VS, 0);
    glCompileShader(vs);
    glGetShaderiv(vs, GL_COMPILE_STATUS, &ok);
    printf("[tri] vertex shader compiled=%d\n", ok);
    glShaderSource(fs, 1, &FS, 0);
    glCompileShader(fs);
    glGetShaderiv(fs, GL_COMPILE_STATUS, &ok);
    printf("[tri] fragment shader compiled=%d\n", ok);
    unsigned prog = glCreateProgram();
    glAttachShader(prog, vs);
    glAttachShader(prog, fs);
    glBindAttribLocation(prog, 0, "pos");
    if (o.varying) glBindAttribLocation(prog, 1, "colour");
    glLinkProgram(prog);
    glGetProgramiv(prog, GL_LINK_STATUS, &ok);
    printf("[tri] program linked=%d\n", ok);
    glUseProgram(prog);

    /* uniform=, uniformi=, uniformm=: values for the program's uniforms */
    for (int k = 0; k < o.nuniforms; k++) {
        const struct tri_uniform *u = &o.uni[k];
        int loc = glGetUniformLocation(prog, u->name);
        if (u->kind == 'i')
            glUniform1i(loc, (int)u->f[0]);
        else if (u->kind == 'm')
            glUniformMatrixNfv[u->n == 4 ? 0 : u->n == 9 ? 1 : 2](loc, 1, 0, u->f);
        else
            glUniformNfv[u->n - 1](loc, 1, u->f);
        printf("[tri] uniform %s at %d glGetError=%#x\n", u->name, loc, glGetError());
    }

    /* tex=: the texture the triangle samples (unit 0, the sampler's default) */
    if (o.tex_w) {
        phase("glTexImage2D");
        unsigned char *t = malloc((size_t)o.tex_w * o.tex_h * 16);     /* up to RGBA f32 */
        const int nbytes = tri_texels(&o, t);
        const unsigned target = o.cube ? GL_TEXTURE_CUBE_MAP : GL_TEXTURE_2D;
        const unsigned fmt = TRI_TEXFMTS[o.tex_kind].format, type = TRI_TEXFMTS[o.tex_kind].type;
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1);
        for (int unit = 0; unit < (o.tex2 ? 2 : 1); unit++) {     /* tex2: the same on 1 */
            unsigned tex;
            glActiveTexture(GL_TEXTURE0 + unit);
            glGenTextures(1, &tex);
            glBindTexture(target, tex);
            for (int face = 0; face < (o.cube ? 6 : 1); face++) {
                const unsigned tgt = o.cube ? GL_TEXTURE_CUBE_MAP_POSITIVE_X + face : GL_TEXTURE_2D;
                if (TRI_TEXFMTS[o.tex_kind].comp)
                    glCompressedTexImage2D(tgt, 0, fmt, o.tex_w, o.tex_h, 0, nbytes, t);
                else
                    glTexImage2D(tgt, 0, (int)fmt, o.tex_w, o.tex_h, 0, fmt, type, t);
            }
            glTexParameteri(target, GL_TEXTURE_MIN_FILTER, (int)o.tex_min);
            glTexParameteri(target, GL_TEXTURE_MAG_FILTER, (int)o.tex_mag);
            glTexParameteri(target, GL_TEXTURE_WRAP_S, (int)o.tex_wrap);
            glTexParameteri(target, GL_TEXTURE_WRAP_T, (int)o.tex_wrap_t);
            if (o.tex_mip)
                glGenerateMipmap(target);
        }
        if (o.tex2) {
            glUniform1i(glGetUniformLocation(prog, "tex1"), 1);
            glActiveTexture(GL_TEXTURE0);
        }
        free(t);
        printf("[tri] texture %dx%d glGetError=%#x\n", o.tex_w, o.tex_h, glGetError());
    }

    /* stream=: the buffer-class device's YUV buffer as the triangle's texture */
    if (o.stream[0]) {
        phase("glTexBindStreamIMG");
        void (*bind)(int, int) = eglGetProcAddress("glTexBindStreamIMG");
        void (*attr)(int, unsigned, int *) = eglGetProcAddress("glGetTexStreamDeviceAttributeivIMG");
        const char *(*name)(int) = eglGetProcAddress("glGetTexStreamDeviceNameIMG");
        int ndev = -1, a[4] = { -1, -1, -1, -1 };
        glGetIntegerv(GL_TEXTURE_NUM_STREAM_DEVICES_IMG, &ndev);
        if (attr) {
            attr(0, GL_TEXTURE_STREAM_DEVICE_WIDTH_IMG, &a[0]);
            attr(0, GL_TEXTURE_STREAM_DEVICE_HEIGHT_IMG, &a[1]);
            attr(0, GL_TEXTURE_STREAM_DEVICE_FORMAT_IMG, &a[2]);
            attr(0, GL_TEXTURE_STREAM_DEVICE_NUM_BUFFERS_IMG, &a[3]);
        }
        printf("[tri] stream devices=%d name=%s %dx%d format=%#x buffers=%d bind=%s\n", ndev,
               name && name(0) ? name(0) : "-", a[0], a[1], a[2], a[3], bind ? "found" : "missing");
        unsigned st;
        glGenTextures(1, &st);
        glBindTexture(GL_TEXTURE_STREAM_IMG, st);
        glTexParameteri(GL_TEXTURE_STREAM_IMG, GL_TEXTURE_MIN_FILTER, 0x2600);
        glTexParameteri(GL_TEXTURE_STREAM_IMG, GL_TEXTURE_MAG_FILTER, 0x2600);
        if (bind) bind(0, 0);
        printf("[tri] stream bound glGetError=%#x\n", glGetError());
    }

    /* fbo=: the triangle goes to an RGBA texture; a second program draws a quad
     * sampling it into the surface */
    unsigned fbo = 0, fbo_tex = 0, prog2 = 0;
    if (o.fbo_w) {
        phase("glFramebufferTexture2D");
        glGenTextures(1, &fbo_tex);
        glBindTexture(GL_TEXTURE_2D, fbo_tex);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, o.fbo_w, o.fbo_h, 0, GL_RGBA, GL_UNSIGNED_BYTE, 0);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, 0x2600);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, 0x2600);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, 0x812F);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, 0x812F);
        glGenFramebuffers(1, &fbo);
        glBindFramebuffer(GL_FRAMEBUFFER, fbo);
        if (o.fbo_samples) {    /* IMG_multisampled_render_to_texture */
            void (*ms)(unsigned, unsigned, unsigned, unsigned, int, int) =
                eglGetProcAddress("glFramebufferTexture2DMultisampleIMG");
            printf("[tri] glFramebufferTexture2DMultisampleIMG %s\n", ms ? "found" : "missing");
            if (ms)
                ms(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, fbo_tex, 0,
                   o.fbo_samples);
        } else {
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, fbo_tex, 0);
        }
        if (o.fbo_depth) {      /* fbodepth: a depth renderbuffer the fbo keeps */
            unsigned rb;
            glGenRenderbuffers(1, &rb);
            glBindRenderbuffer(GL_RENDERBUFFER, rb);
            glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT16, o.fbo_w, o.fbo_h);
            glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, rb);
        }
        printf("[tri] fbo %dx%d status=%#x\n", o.fbo_w, o.fbo_h,
               glCheckFramebufferStatus(GL_FRAMEBUFFER));
        const char *VS2 = TRI_TEX_VS, *FS2 = TRI_TEX_FS;
        unsigned vs2 = glCreateShader(GL_VERTEX_SHADER), fs2 = glCreateShader(GL_FRAGMENT_SHADER);
        glShaderSource(vs2, 1, &VS2, 0);
        glCompileShader(vs2);
        glShaderSource(fs2, 1, &FS2, 0);
        glCompileShader(fs2);
        prog2 = glCreateProgram();
        glAttachShader(prog2, vs2);
        glAttachShader(prog2, fs2);
        glBindAttribLocation(prog2, 0, "pos");
        glLinkProgram(prog2);
        glGetProgramiv(prog2, GL_LINK_STATUS, &ok);
        printf("[tri] quad program linked=%d\n", ok);
    }

    phase("glClear");
    if (o.fbo_w)
        glViewport(0, 0, o.fbo_w, o.fbo_h);
    else
        glViewport(o.viewport[0], o.viewport[1], o.viewport[2], o.viewport[3]);
    if (!o.dither) glDisable(GL_DITHER);
    if (o.a2c) glEnable(0x809E);                    /* GL_SAMPLE_ALPHA_TO_COVERAGE */
    if (o.samplecov) {                              /* GL_SAMPLE_COVERAGE */
        glEnable(0x80A0);
        glSampleCoverage(o.samplecov_v, (unsigned char)o.samplecov_inv);
    }
    if (o.linewidth != 1.0f) glLineWidth(o.linewidth);
    if (o.hint_target) glHint(o.hint_target, o.hint_mode);
    if (o.polyoffset) {
        glEnable(GL_POLYGON_OFFSET_FILL);
        glPolygonOffset(o.poly_factor, o.poly_units);
    }
    if (o.depth_range[0] != 0.0f || o.depth_range[1] != 1.0f)
        glDepthRangef(o.depth_range[0], o.depth_range[1]);
    unsigned clear_bits = GL_COLOR_BUFFER_BIT;
    if (o.depth_func) {
        glEnable(GL_DEPTH_TEST);
        glDepthFunc(o.depth_func);
        glDepthMask(o.depth_write);
        glClearDepthf(o.clear_depth);
        clear_bits |= GL_DEPTH_BUFFER_BIT;
    }
    if (o.stencil_func) {
        glEnable(GL_STENCIL_TEST);
        glStencilFunc(o.stencil_func, o.stencil_ref, o.stencil_mask);
        glStencilMask(o.stencil_write);
        glStencilOp(o.stencil_ops[0], o.stencil_ops[1], o.stencil_ops[2]);
        clear_bits |= GL_STENCIL_BUFFER_BIT;
    }
    if (o.do_clear)
        glClearColor(o.clear[0], o.clear[1], o.clear[2], o.clear[3]);
    if (o.blend_eq) {
        glEnable(GL_BLEND);
        glBlendFunc(o.blend_src, o.blend_dst);
        glBlendEquation(o.blend_eq);
    }
    if (o.cull) {
        glEnable(GL_CULL_FACE);
        glCullFace(o.cull);
    }
    if (o.front_face != 0x0901) glFrontFace(o.front_face);
    if (!(o.mask[0] && o.mask[1] && o.mask[2] && o.mask[3]))
        glColorMask(o.mask[0], o.mask[1], o.mask[2], o.mask[3]);
    if (o.do_scissor) {
        glEnable(GL_SCISSOR_TEST);
        glScissor(o.scissor[0], o.scissor[1], o.scissor[2], o.scissor[3]);
    }
    /* Positions and colours in two packed arrays, as the original frame. */
    static float v[TRI_MAX_VERTS * TRI_VERT_FLOATS], pos[TRI_MAX_VERTS * 4],
        col[TRI_MAX_VERTS * 4];
    int nv = tri_geometry(&o, v);
    for (int i = 0; i < nv; i++)
        for (int c = 0; c < 4; c++) {
            pos[4 * i + c] = v[i * TRI_VERT_FLOATS + c];
            col[4 * i + c] = v[i * TRI_VERT_FLOATS + 4 + c];
        }
    if (o.attr_kind || o.attr_size != 4 || o.stride || o.vbo) {
        /* attrfmt=, attrsize=, stride=, vbo: the position in another layout */
        static unsigned char ab[TRI_MAX_VERTS * 64];
        int st = tri_attr_data(&o, v, nv, ab);
        const void *at = ab;
        if (o.vbo) {
            unsigned vb;
            glGenBuffers(1, &vb);
            glBindBuffer(0x8892, vb);                   /* GL_ARRAY_BUFFER */
            glBufferData(0x8892, st * nv, ab, 0x88E4);  /* GL_STATIC_DRAW */
            at = 0;
        }
        glVertexAttribPointer(0, o.attr_size, TRI_ATTRFMTS[o.attr_kind].type,
                              (unsigned char)o.attr_norm, o.stride, at);
    } else {
        glVertexAttribPointer(0, 4, GL_FLOAT, 0, 0, pos);
    }
    glEnableVertexAttribArray(0);
    if (o.varying) {
        glVertexAttribPointer(1, 4, GL_FLOAT, 0, 0, col);
        glEnableVertexAttribArray(1);
    }
    for (int f = 0; f < o.frames; f++) {
        if (o.do_clear && (!o.clear_once || f == 0)) {
            phase("glClear");
            glClear(clear_bits);
        }
        phase("glDrawArrays");
        for (int k = 0; k < o.draws; k++) {
            /* the client array is read at the draw call: move it for each draw */
            float dx, dy;
            tri_draw_shift(&o, k, &dx, &dy);
            for (int i = 0; i < nv; i++) {
                pos[4 * i] = v[i * TRI_VERT_FLOATS] + dx;
                pos[4 * i + 1] = v[i * TRI_VERT_FLOATS + 1] + dy;
            }
            glDrawArrays(o.prim, 0, nv);
            if (o.flush && k + 1 < o.draws)
                glFlush();
        }
        if (o.fbo_w) {
            static const float quad[] = { -1, -1, 0, 1, 1, -1, 0, 1, 1, 1, 0, 1,
                                          -1, -1, 0, 1, 1, 1, 0, 1, -1, 1, 0, 1 };
            phase("fbo quad");
            glBindFramebuffer(GL_FRAMEBUFFER, 0);
            glViewport(0, 0, W, H);
            glUseProgram(prog2);
            glBindTexture(GL_TEXTURE_2D, fbo_tex);
            glVertexAttribPointer(0, 4, GL_FLOAT, 0, 0, quad);
            glDrawArrays(GL_TRIANGLES, 0, 6);
        }
        phase("glFinish");
        glFinish();
        unsigned char px[4] = { 0 };
        if (o.readback) {       /* readback: the whole surface, the centre pixel printed */
            unsigned char *all = malloc((size_t)W * H * 4);
            phase("glReadPixels");
            glReadPixels(0, 0, W, H, GL_RGBA, GL_UNSIGNED_BYTE, all);
            memcpy(px, all + ((size_t)(H / 2) * W + W / 2) * 4, 4);
            free(all);
        } else {
            glReadPixels(W / 2, H / 2, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, px);
        }
        printf("[tri] frame %d centre pixel %02x%02x%02x%02x glGetError=%#x\n", f,
               px[0], px[1], px[2], px[3], glGetError());
        if (o.texsub) {         /* texsub: the lower left quarter, every byte inverted */
            int qw = (o.tex_w + 1) / 2, qh = (o.tex_h + 1) / 2;
            unsigned char *q = malloc((size_t)qw * qh * 4);
            for (int i = 0; i < qw * qh * 4; i++) q[i] = (unsigned char)~i;
            phase("glTexSubImage2D");
            glTexSubImage2D(o.cube ? GL_TEXTURE_CUBE_MAP_POSITIVE_X : GL_TEXTURE_2D, 0, 0, 0, qw,
                            qh, TRI_TEXFMTS[o.tex_kind].format, TRI_TEXFMTS[o.tex_kind].type, q);
            free(q);
            glFinish();
        }
        if (o.copytex) {        /* copytex: the whole surface into a new texture */
            unsigned ct;
            glGenTextures(1, &ct);
            glBindTexture(GL_TEXTURE_2D, ct);
            phase("glCopyTexImage2D");
            glCopyTexImage2D(GL_TEXTURE_2D, 0, c8 ? GL_RGBA : 0x1907, 0, 0, W, H, 0);
            glFinish();
            printf("[tri] copytex glGetError=%#x\n", glGetError());
        }
        phase("eglSwapBuffers");
        eglSwapBuffers(dpy, surf);
        if (o.fbo_w) {          /* back to the first pass for the next frame */
            glBindFramebuffer(GL_FRAMEBUFFER, fbo);
            glViewport(0, 0, o.fbo_w, o.fbo_h);
            glUseProgram(prog);
            glVertexAttribPointer(0, 4, GL_FLOAT, 0, 0, pos);
        }
    }
    phase("eglTerminate");
    eglMakeCurrent(dpy, 0, 0, EGL_NO_CONTEXT);
    eglTerminate(dpy);
    printf("[tri] done\n");
    return 0;
}
