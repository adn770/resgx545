/* SPDX-License-Identifier: MIT */
/* SPDX-FileCopyrightText: 2026 Josep Torra */
/* bufclass.h — the buffer-class device fakedrm.c offers (one device, one buffer), so the
 * closed GLES2 stack can stream a YUV texture (IMG_texture_stream2) with no kernel.
 *
 * FAKEBC=FORMAT,WxH configures it (default uyvy,64x64): FORMAT names a PVRSRV_PIXEL_FORMAT
 * code of the GPL DDK (include4/servicesext.h) and its layout (BC_NAMES). The buffer holds a
 * fixed pattern, Y = 4x, U = 8y, V = 255 - 8y (bytes, wrapping), so a capture shows how the
 * driver and the hardware read each format. Layouts: BUFFER_INFO (servicesext.h) as the
 * OUT of GET_BUFFERCLASS_INFO after eError (services4/include/pvr_bridge.h). */
#ifndef BUFCLASS_H
#define BUFCLASS_H

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define BC_FMT_NV12 64u
#define BC_FMT_YUYV 69u
#define BC_FMT_UYVY 71u

/* The names FAKEBC takes: the PVRSRV_PIXEL_FORMAT code and the layout (U first in a packed
 * pair, Y first, or the two NV12 planes). */
enum { BC_UYVY, BC_YUYV, BC_NV12 };
static const struct bc_name { const char *name; uint32_t code; int layout; } BC_NAMES[] = {
    { "uyvy", BC_FMT_UYVY, BC_UYVY }, { "yuyv", BC_FMT_YUYV, BC_YUYV },
    { "nv12", BC_FMT_NV12, BC_NV12 }, { "fuyvy", 73, BC_UYVY }, { "fyuyv", 74, BC_YUYV },
    { "c0yuyv", 195, BC_YUYV }, { "c0uyvy", 196, BC_UYVY }, { "c1yuyv", 199, BC_YUYV },
    { "c1uyvy", 200, BC_UYVY }, { 0, 0, 0 },
};

struct bc_config {
    uint32_t format, width, height, stride;
    int layout;
};

/* "FORMAT,WxH" (0: the default); 0 on success. Packed formats need an even width, NV12 an
 * even width and height. */
static inline int bc_parse(struct bc_config *c, const char *s)
{
    char f[8] = "uyvy";
    unsigned w = 64, h = 64;
    if (s && sscanf(s, "%7[a-z0-9],%ux%u", f, &w, &h) != 3)
        return -1;
    const struct bc_name *n = BC_NAMES;
    while (n->name && strcmp(n->name, f)) n++;
    if (!n->name)
        return -1;
    c->format = n->code;
    c->layout = n->layout;
    if (!w || !h || w > 2048 || h > 2048 || w % 2 || (c->layout == BC_NV12 && h % 2))
        return -1;
    c->width = w;
    c->height = h;
    c->stride = c->layout == BC_NV12 ? w : 2 * w;
    return 0;
}

static inline uint32_t bc_size(const struct bc_config *c)
{
    return c->layout == BC_NV12 ? c->width * c->height * 3 / 2 : c->stride * c->height;
}

/* GET_BUFFERCLASS_INFO's OUT: o[0] eError (left alone), o[1..7] ui32BufferCount,
 * ui32BufferDeviceID, pixelformat, ui32ByteStride, ui32Width, ui32Height, ui32Flags, then
 * szDeviceName[50] from o[8]. */
static inline void bc_info(uint32_t *o, const struct bc_config *c)
{
    o[1] = 1;
    o[2] = 0;
    o[3] = c->format;
    o[4] = c->stride;
    o[5] = c->width;
    o[6] = c->height;
    o[7] = 0;
    memcpy(o + 8, "fakebc", 7);
}

static inline void bc_pattern(const struct bc_config *c, unsigned char *b)
{
    for (uint32_t y = 0; y < c->height; y++)
        for (uint32_t x = 0; x < c->width; x += 2) {
            unsigned char y0 = 4 * x, y1 = 4 * (x + 1), u = 8 * y, v = 255 - 8 * y;
            unsigned char *p = b + y * c->stride + (c->layout == BC_NV12 ? x : 2 * x);
            if (c->layout == BC_UYVY) {
                p[0] = u; p[1] = y0; p[2] = v; p[3] = y1;
            } else if (c->layout == BC_YUYV) {
                p[0] = y0; p[1] = u; p[2] = y1; p[3] = v;
            } else {
                p[0] = y0; p[1] = y1;
                if (y % 2 == 0) {      /* the UV plane: one row per two luma rows */
                    unsigned char *q = b + c->width * c->height + (y / 2) * c->width + x;
                    q[0] = u; q[1] = v;
                }
            }
        }
}

#endif
