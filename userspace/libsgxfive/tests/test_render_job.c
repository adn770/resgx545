// SPDX-License-Identifier: MIT
/*
 * Render contexts and render jobs against the mock: what DEV_QUERY reports, the kernel's rules on contexts, commands and
 * reserved heaps, the triangle rendered by the mock's interpreter and checked
 * pixel by pixel, a faulting render losing its context, a scene overflowing
 * the parameter buffer failing with -ENOSPC, transfers keeping
 * PDS_EXEC_BASE at the PDS_PIXEL heap base, and transfers and renders
 * interleaved in one VM.
 */
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

#include "sgxfive_mock.h"
#include "sgxfive_render.h"
#include "sgxfive_tri_probe.h"
#include "sgxfive_xfer.h"
#include "tap.h"

#define NSEC 1000000000LL

struct env {
	struct sgxfive_mock *mock;
	struct sgxfive_dev *dev;
	struct sgxfive_vm *vm;
	uint32_t ctx;
	struct sgxfive_render *r;
};

static void env_init(struct env *e)
{
	const struct sgxfive_mock_config cfg = { .layout = SGXFIVE_MOCK_LAYOUT_REV1 };

	memset(e, 0, sizeof(*e));
	e->mock = sgxfive_mock_create(&cfg);
	CHECK_EQ(sgxfive_dev_open(sgxfive_mock_backend(e->mock), NULL, &e->dev), 0);
	CHECK_EQ(sgxfive_vm_create(e->dev, &e->vm), 0);
	CHECK_EQ(sgxfive_render_ctx_create(e->vm, SGXFIVE_TRI_MAX_W, SGXFIVE_TRI_MAX_H, &e->ctx),
		 0);
	CHECK_EQ(sgxfive_render_create(e->vm, e->ctx, &e->r), 0);
}

static void env_fini(struct env *e)
{
	sgxfive_render_destroy(e->r);
	sgxfive_ctx_destroy(e->dev, e->ctx);
	sgxfive_vm_destroy(e->vm);
	sgxfive_dev_close(e->dev);
	sgxfive_mock_destroy(e->mock);
}

static void query(void)
{
	struct env e;
	const struct sgxfive_info *info;
	const struct drm_sgxfive_heap *h;

	env_init(&e);
	info = sgxfive_dev_info(e.dev);
	CHECK(info->job.job_types & DRM_SGXFIVE_JOB_TYPE_RENDER_BIT);
	CHECK(info->job.job_types & DRM_SGXFIVE_JOB_TYPE_TRANSFER_BIT);
	CHECK_EQ(info->job.render_cmd_size, DRM_SGXFIVE_RENDER_CMD_SIZE_V1);
	CHECK_EQ(info->job.render_pb_pages, 0x422);
	CHECK_EQ(info->job.render_max_width, 4096);
	CHECK_EQ(info->job.render_max_height, 4096);
	CHECK_EQ(info->num_heaps, DRM_SGXFIVE_HEAP_COUNT);
	h = &info->heaps[DRM_SGXFIVE_HEAP_PARAMETERS];
	CHECK_EQ(h->base, 0x10000000);
	CHECK(h->flags & DRM_SGXFIVE_HEAP_RESERVED);
	h = &info->heaps[DRM_SGXFIVE_HEAP_TA_DATA];
	CHECK_EQ(h->base, 0x20000000);
	CHECK(h->flags & DRM_SGXFIVE_HEAP_RESERVED);
	env_fini(&e);
}

/* The triangle at several sizes: every pixel, the guard area, and twice in a row. */
static void triangle(void)
{
	static const uint32_t sizes[][2] = {
		{ 64, 64 }, { 128, 64 }, { 256, 128 }, { 32, 16 }, { 128, 192 }, { 256, 256 },
		{ 100, 60 }, { 1024, 768 }, { 32, 16 },
	};
	struct sgxfive_tri_counts n;
	struct sgxfive_mock_stats st;
	struct sgxfive_tri_params p;
	struct env e;

	env_init(&e);
	for (unsigned int i = 0; i < sizeof(sizes) / sizeof(sizes[0]); i++) {
		sgxfive_tri_default(&p, sizes[i][0], sizes[i][1]);
		CHECK_EQ(sgxfive_render_tri(e.r, &p, 0, 0), 0);
		CHECK_EQ(sgxfive_render_wait(e.r, NSEC), 0);
		CHECK_EQ(sgxfive_tri_check(&p, sgxfive_render_fb(e.r), &n), 0);
		CHECK(n.tri > 0 && n.bg > 0);
		CHECK_EQ(n.other, 0);
		CHECK_EQ(sgxfive_render_guard_dirty(e.r, &p), 0);
	}
	/* Another colour on the same context. */
	sgxfive_tri_default(&p, 64, 64);
	p.colour = 0xffff0000;
	p.bg_colour = 0xff000080;
	CHECK_EQ(sgxfive_render_tri(e.r, &p, 0, 0), 0);
	CHECK_EQ(sgxfive_render_wait(e.r, NSEC), 0);
	CHECK_EQ(sgxfive_tri_check(&p, sgxfive_render_fb(e.r), &n), 0);
	sgxfive_mock_get_stats(e.mock, &st);
	CHECK_EQ(st.renders_run, 10);
	CHECK_EQ(st.faults, 0);
	env_fini(&e);
}

/*
 * Odd widths: the image at the even row pitch, its pad pixel and the guard area
 * untouched, and an even width after an odd one.
 */
static void odd_width(void)
{
	static const uint32_t sizes[][2] = { { 19, 18 }, { 33, 17 }, { 1, 1 }, { 63, 64 }, { 64, 64 } };
	struct sgxfive_tri_counts n;
	struct sgxfive_tri_params p;
	struct env e;

	env_init(&e);
	for (unsigned int i = 0; i < sizeof(sizes) / sizeof(sizes[0]); i++) {
		const uint32_t w = sizes[i][0], h = sizes[i][1], s = sgxfive_tri_stride_px(w);
		const uint32_t *fb;

		sgxfive_tri_default(&p, w, h);
		CHECK_EQ(sgxfive_render_tri(e.r, &p, 0, 0), 0);
		CHECK_EQ(sgxfive_render_wait(e.r, NSEC), 0);
		fb = sgxfive_render_fb(e.r);
		CHECK_EQ(sgxfive_tri_check(&p, fb, &n), 0);
		CHECK_EQ(n.other, 0);
		CHECK_EQ(n.tri + n.bg, w * h);
		CHECK_EQ(sgxfive_render_guard_dirty(e.r, &p), 0);
		for (uint32_t y = 0; s != w && y < h; y++)
			CHECK_EQ(fb[(uint64_t)y * s + w], SGXFIVE_TRI_SENTINEL);
	}
	env_fini(&e);
}

/* The kernel's rules on render contexts, commands and the reserved heaps. */
static void rules(void)
{
	struct drm_sgxfive_render_cmd cmd __attribute__((aligned(8)));
	struct sgxfive_tri_params p;
	struct sgxfive_bo *bo = NULL;
	uint32_t xctx, ctxs[32], n = 0, t;
	struct env e;
	int ret;

	env_init(&e);
	sgxfive_tri_default(&p, 64, 64);
	CHECK_EQ(sgxfive_render_tri(e.r, &p, 0, 0), 0);
	CHECK_EQ(sgxfive_render_wait(e.r, NSEC), 0);
	cmd = *sgxfive_render_last_cmd(e.r);

	/* Job and context types must match. */
	CHECK_EQ(sgxfive_ctx_create(e.vm, &xctx), 0);
	CHECK_EQ(sgxfive_submit_render(e.dev, xctx, &cmd, 0, 0), -EINVAL);
	CHECK_EQ(sgxfive_submit_transfer(e.dev, e.ctx, DRM_SGXFIVE_SUBMIT_JOB_TRANSFER_DUMMY,
					 NULL, 0, 0), -EINVAL);
	/* Fetch addresses in user heaps, aligned; the target within the limit. */
	cmd.vdm_ctrl_stream_base = 0x32000000;
	CHECK_EQ(sgxfive_submit_render(e.dev, e.ctx, &cmd, 0, 0), -EINVAL);
	cmd = *sgxfive_render_last_cmd(e.r);
	cmd.vdm_ctrl_stream_base += 2;
	CHECK_EQ(sgxfive_submit_render(e.dev, e.ctx, &cmd, 0, 0), -EINVAL);
	cmd = *sgxfive_render_last_cmd(e.r);
	cmd.event_pixel_pds_exec = 0x10001000;	/* the PARAMETERS heap */
	CHECK_EQ(sgxfive_submit_render(e.dev, e.ctx, &cmd, 0, 0), -EINVAL);
	cmd = *sgxfive_render_last_cmd(e.r);
	cmd.mte_screen = 511 | 63 << 16;	/* tiling words not of this size */
	CHECK_EQ(sgxfive_submit_render(e.dev, e.ctx, &cmd, 0, 0), -EINVAL);
	cmd = *sgxfive_render_last_cmd(e.r);
	cmd.te_mtile2 = 0x02008008;
	CHECK_EQ(sgxfive_submit_render(e.dev, e.ctx, &cmd, 0, 0), -EINVAL);
	cmd = *sgxfive_render_last_cmd(e.r);
	cmd.mte_screen = 4096 | 63 << 16;	/* 4097 across */
	sgxfive_tiling_cmd(&cmd, 4097, 64);
	CHECK_EQ(sgxfive_submit_render(e.dev, e.ctx, &cmd, 0, 0), -EINVAL);
	cmd = *sgxfive_render_last_cmd(e.r);
	cmd.isp_bgobj = 0x1300;
	CHECK_EQ(sgxfive_submit_render(e.dev, e.ctx, &cmd, 0, 0), -EINVAL);
	/* A render flag beyond the geometry one; a short command. */
	{
		struct drm_sgxfive_job job = {
			.type = DRM_SGXFIVE_JOB_TYPE_RENDER, .context_handle = e.ctx,
			.flags = 2, .cmd_stream = (uintptr_t)sgxfive_render_last_cmd(e.r),
			.cmd_stream_len = DRM_SGXFIVE_RENDER_CMD_SIZE_V1,
		};

		CHECK_EQ(sgxfive_submit(e.dev, &job, 1, NULL), -EINVAL);
		job.flags = 0;
		job.cmd_stream_len = DRM_SGXFIVE_RENDER_CMD_SIZE_V1 - 8;
		CHECK_EQ(sgxfive_submit(e.dev, &job, 1, NULL), -EINVAL);
	}
	/* The reserved render heaps cannot be mapped. */
	CHECK_EQ(sgxfive_bo_create(e.dev, 4096, 0, &bo), 0);
	CHECK_EQ(sgxfive_vm_map(e.vm, 0x10000000, bo, 0, 4096, 0), -EINVAL);
	CHECK_EQ(sgxfive_vm_map(e.vm, 0x20000000, bo, 0, 4096, 0), -EINVAL);
	sgxfive_bo_destroy(bo);
	/* 32 render contexts per VM: this one and 31 more, then -ENOSPC. */
	while (n < 32 && !(ret = sgxfive_render_ctx_create(e.vm, 64, 64, &ctxs[n])))
		n++;
	CHECK_EQ(n, 31);
	CHECK_EQ(ret, -ENOSPC);
	CHECK_EQ(sgxfive_ctx_destroy(e.dev, ctxs[0]), 0);
	CHECK_EQ(sgxfive_render_ctx_create(e.vm, 64, 64, &t), 0);
	ctxs[0] = t;
	for (uint32_t i = 0; i < n; i++)
		sgxfive_ctx_destroy(e.dev, ctxs[i]);
	/* An unknown context type. */
	CHECK_EQ(sgxfive_ctx_create_type(e.vm, 2, &t), -EINVAL);
	/*
	 * A render context states its largest target, 1 to 4096 each way: none
	 * (what a caller of the older 24-byte struct sends), 0 or 4097 is refused.
	 */
	CHECK_EQ(sgxfive_ctx_create_type(e.vm, DRM_SGXFIVE_CTX_TYPE_RENDER, &t), -EINVAL);
	CHECK_EQ(sgxfive_render_ctx_create(e.vm, 0, 64, &t), -EINVAL);
	CHECK_EQ(sgxfive_render_ctx_create(e.vm, 64, 0, &t), -EINVAL);
	CHECK_EQ(sgxfive_render_ctx_create(e.vm, 4097, 64, &t), -EINVAL);
	CHECK_EQ(sgxfive_render_ctx_create(e.vm, 64, 4097, &t), -EINVAL);
	sgxfive_ctx_destroy(e.dev, xctx);
	env_fini(&e);
}

/*
 * A render context made for 4x targets (DRM_SGXFIVE_CTX_RENDER_AA_4X): only
 * a render context takes the flag, and no other bit; only such a context
 * takes a job whose TE_AA sets bit 31 or 30 (0xe0000000 at 4x), and it still
 * renders a single-sampled job as before.
 */
static void aa4(void)
{
	static const uint32_t ms[] = { 0xe0000000, 0x60000000, 0xa0000000, 0x40000000, 0x80000000 };
	struct drm_sgxfive_render_cmd cmd __attribute__((aligned(8)));
	struct sgxfive_tri_counts n;
	struct sgxfive_tri_params p;
	struct sgxfive_render *r;
	uint32_t ctx, t;
	struct env e;

	env_init(&e);
	sgxfive_tri_default(&p, 64, 64);
	CHECK_EQ(sgxfive_render_tri(e.r, &p, 0, 0), 0);
	CHECK_EQ(sgxfive_render_wait(e.r, NSEC), 0);
	cmd = *sgxfive_render_last_cmd(e.r);
	CHECK_EQ(cmd.te_aa, 0x20000000);
	/* A context made without the flag refuses a multisampled TE_AA. */
	for (unsigned int i = 0; i < sizeof(ms) / sizeof(ms[0]); i++) {
		cmd.te_aa = ms[i];
		CHECK_EQ(sgxfive_submit_render(e.dev, e.ctx, &cmd, 0, 0), -EINVAL);
	}
	/* The flag: render contexts only, no unknown bit. */
	CHECK_EQ(sgxfive_render_ctx_create_flags(e.vm, 64, 64, 2, &t), -EINVAL);
	CHECK_EQ(sgxfive_render_ctx_create_flags(e.vm, 64, 64, 0x80000001u, &t), -EINVAL);
	{
		struct drm_sgxfive_create_context_args a = {
			.type = DRM_SGXFIVE_CTX_TYPE_TRANSFER, .flags = DRM_SGXFIVE_CTX_RENDER_AA_4X,
			.vm_context_handle = sgxfive_vm_handle(e.vm),
		};

		CHECK_EQ(sgxfive_dev_ioctl(e.dev, DRM_IOCTL_SGXFIVE_CREATE_CONTEXT, &a), -EINVAL);
	}
	CHECK_EQ(sgxfive_render_ctx_create_flags(e.vm, 64, 64, 0, &ctx), 0);	/* as before */
	sgxfive_ctx_destroy(e.dev, ctx);
	CHECK_EQ(sgxfive_render_ctx_create_flags(e.vm, 4096, 4096,
						 DRM_SGXFIVE_CTX_RENDER_AA_4X, &ctx), 0);
	sgxfive_ctx_destroy(e.dev, ctx);
	CHECK_EQ(sgxfive_render_ctx_create_flags(e.vm, 64, 64, DRM_SGXFIVE_CTX_RENDER_AA_4X,
						 &ctx), 0);
	for (unsigned int i = 0; i < sizeof(ms) / sizeof(ms[0]); i++) {
		cmd.te_aa = ms[i];
		CHECK_EQ(sgxfive_submit_render(e.dev, ctx, &cmd, 0, 0), 0);
	}
	{	/* a command at a 4-byte offset (i686 stack): the call aligns its own copy */
		_Alignas(8) unsigned char raw[sizeof(cmd) + 8];
		struct drm_sgxfive_render_cmd *odd = (void *)(raw + 4);

		memcpy(odd, &cmd, sizeof(cmd));
		CHECK_EQ((uintptr_t)odd % 8, 4);
		CHECK_EQ(sgxfive_submit_render(e.dev, ctx, odd, 0, 0), 0);
	}
	sgxfive_ctx_destroy(e.dev, ctx);
	/* A 4x context renders a single-sampled triangle as any other. */
	CHECK_EQ(sgxfive_render_ctx_create_flags(e.vm, 64, 64, DRM_SGXFIVE_CTX_RENDER_AA_4X,
						 &ctx), 0);
	CHECK_EQ(sgxfive_render_create(e.vm, ctx, &r), 0);
	CHECK_EQ(sgxfive_render_tri(r, &p, 0, 0), 0);
	CHECK_EQ(sgxfive_render_wait(r, NSEC), 0);
	CHECK_EQ(sgxfive_tri_check(&p, sgxfive_render_fb(r), &n), 0);
	CHECK_EQ(n.other, 0);
	sgxfive_render_destroy(r);
	sgxfive_ctx_destroy(e.dev, ctx);
	env_fini(&e);
}

/* A render whose stream is mapped nowhere faults: the context is lost. */
static void fault(void)
{
	struct drm_sgxfive_render_cmd cmd __attribute__((aligned(8)));
	struct sgxfive_mock_stats st;
	struct sgxfive_tri_params p;
	struct sgxfive_tri_counts n;
	struct sgxfive_render *r2;
	uint32_t ctx2, sync;
	struct env e;

	env_init(&e);
	sgxfive_tri_default(&p, 64, 64);
	CHECK_EQ(sgxfive_render_tri(e.r, &p, 0, 0), 0);
	CHECK_EQ(sgxfive_render_wait(e.r, NSEC), 0);
	cmd = *sgxfive_render_last_cmd(e.r);
	cmd.vdm_ctrl_stream_base = 0x7e000000;	/* GENERAL, unmapped */
	CHECK_EQ(sgxfive_syncobj_create(e.dev, false, &sync), 0);
	CHECK_EQ(sgxfive_submit_render(e.dev, e.ctx, &cmd, 0, sync), 0);
	sgxfive_mock_get_stats(e.mock, &st);
	CHECK_EQ(st.faults, 1);
	CHECK_EQ(st.last_fault_addr, 0x7e000000);
	/* Its fence carries the fault, which the wait reports. */
	CHECK_EQ(sgxfive_syncobj_wait(e.dev, sync, 0, NSEC), -EIO);
	CHECK_EQ(sgxfive_submit_render(e.dev, e.ctx, &cmd, 0, 0), -ECANCELED);
	/* Another render context of the file still renders. */
	CHECK_EQ(sgxfive_render_ctx_create(e.vm, 64, 64, &ctx2), 0);
	CHECK_EQ(sgxfive_render_create(e.vm, ctx2, &r2), 0);
	CHECK_EQ(sgxfive_render_tri(r2, &p, 0, 0), 0);
	CHECK_EQ(sgxfive_render_wait(r2, NSEC), 0);
	CHECK_EQ(sgxfive_tri_check(&p, sgxfive_render_fb(r2), &n), 0);
	sgxfive_render_destroy(r2);
	sgxfive_ctx_destroy(e.dev, ctx2);
	sgxfive_syncobj_destroy(e.dev, sync);
	env_fini(&e);
}

/*
 * The engine's wait reports a render that faulted, once: here its stream page
 * is unmapped behind its back.
 */
static void fault_wait(void)
{
	struct sgxfive_tri_layout l;
	struct sgxfive_tri_params p;
	struct env e;

	env_init(&e);
	sgxfive_tri_default(&p, 64, 64);
	sgxfive_render_get_layout(e.r, &l);
	CHECK_EQ(sgxfive_vm_unmap(e.vm, l.gen, SGXFIVE_PAGE_SIZE), 0);
	CHECK_EQ(sgxfive_render_tri(e.r, &p, 0, 0), 0);
	CHECK_EQ(sgxfive_render_wait(e.r, NSEC), -EIO);
	CHECK_EQ(sgxfive_render_wait(e.r, NSEC), 0);
	/* The context is lost. */
	CHECK_EQ(sgxfive_render_tri(e.r, &p, 0, 0), -ECANCELED);
	env_fini(&e);
}

/*
 * Transfers keep PDS_EXEC_BASE at the PDS_PIXEL heap base: the kernel refuses
 * another value, and a second engine in the VM (whose PDS page is not the
 * first) still fills correctly; fills and renders interleave in one VM.
 */
static void transfers(void)
{
	const struct sgxfive_rect rect = { 4, 2, 40, 18 };
	struct sgxfive_prog_source *src = sgxfive_prog_asm_create();
	struct drm_sgxfive_transfer_cmd xcmd;
	struct sgxfive_xfer *x1, *x2;
	struct sgxfive_tri_params p;
	struct sgxfive_tri_counts n;
	struct sgxfive_bo *bo = NULL;
	struct sgxfive_xfer_layout l;
	uint32_t xctx, *dst = NULL, bad = 0;
	uint64_t addr;
	struct env e;

	env_init(&e);
	CHECK_EQ(sgxfive_ctx_create(e.vm, &xctx), 0);
	CHECK_EQ(sgxfive_xfer_create(e.vm, xctx, src, &x1), 0);
	CHECK_EQ(sgxfive_xfer_create(e.vm, xctx, src, &x2), 0);
	sgxfive_xfer_get_layout(x2, &l);
	CHECK(l.pds_page != 0x2e000000);
	CHECK_EQ(sgxfive_bo_create(e.dev, 4 * 4096, DRM_SGXFIVE_BO_ALLOW_CPU_ACCESS, &bo), 0);
	CHECK_EQ(sgxfive_bo_mmap(bo, (void **)&dst), 0);
	CHECK_EQ(sgxfive_vm_alloc(e.vm, DRM_SGXFIVE_HEAP_GENERAL, 4 * 4096, 4096, &addr), 0);
	CHECK_EQ(sgxfive_vm_map(e.vm, addr, bo, 0, 4 * 4096, 0), 0);
	sgxfive_tri_default(&p, 64, 64);
	for (int round = 0; round < 2; round++) {
		const struct sgxfive_surface s = { addr, 64, 64, 256 };
		struct sgxfive_xfer *x = round ? x2 : x1;
		uint32_t colour = round ? 0xff123456 : 0xff654321;

		memset(dst, 0, 4 * 4096);
		CHECK_EQ(sgxfive_xfer_fill(x, &s, &rect, colour, 0), 0);
		CHECK_EQ(sgxfive_render_tri(e.r, &p, 0, 0), 0);
		CHECK_EQ(sgxfive_xfer_wait(x, NSEC), 0);
		CHECK_EQ(sgxfive_render_wait(e.r, NSEC), 0);
		CHECK_EQ(sgxfive_xfer_last_cmd(x)->pds_exec_base, 0x2e000000);
		for (uint32_t y = 0; y < 64; y++)
			for (uint32_t xx = 0; xx < 64; xx++) {
				bool in = xx >= rect.x0 && xx < rect.x1 && y >= rect.y0 &&
					  y < rect.y1;

				bad += dst[y * 64 + xx] != (in ? colour : 0);
			}
		CHECK_EQ(bad, 0);
		CHECK_EQ(sgxfive_tri_check(&p, sgxfive_render_fb(e.r), &n), 0);
	}
	/* Any other PDS_EXEC_BASE is refused. */
	xcmd = *sgxfive_xfer_last_cmd(x2);
	xcmd.pds_exec_base = (uint32_t)l.pds_page;
	CHECK_EQ(sgxfive_submit_transfer(e.dev, xctx, 0, &xcmd, 0, 0), -EINVAL);
	sgxfive_xfer_destroy(x1);
	sgxfive_xfer_destroy(x2);
	sgxfive_vm_unmap(e.vm, addr, 4 * 4096);
	sgxfive_bo_destroy(bo);
	sgxfive_prog_source_destroy(src);
	sgxfive_ctx_destroy(e.dev, xctx);
	env_fini(&e);
}

/*
 * Q190's layered background on the mock: the knobs (struct sgxfive_mock_config bg_layer and
 * bg_src, the kernel's debugfs render_bg_layer and render_bg_src) and the kernel's rule: with
 * the layer on, a source that is not mapped in the context's VM is refused at submit
 * (-EINVAL); mapped, every background pixel is the source's texel the layer's coordinates
 * name (the identity here, the source being the target's own size); knob off: today's image.
 */
#define BGL_SRC	0x3e800000u

static void bg_layer_env(struct env *e, bool layer, uint32_t src, bool map, uint32_t w,
			 uint32_t h)
{
	const struct sgxfive_mock_config cfg = {
		.layout = SGXFIVE_MOCK_LAYOUT_REV1, .bg_layer = layer, .bg_src = src,
	};
	struct sgxfive_bo *bo = NULL;
	uint32_t *map_p = NULL;
	const uint64_t size = ((uint64_t)w * h * 4 + 4095) & ~4095ull;

	memset(e, 0, sizeof(*e));
	e->mock = sgxfive_mock_create(&cfg);
	CHECK_EQ(sgxfive_dev_open(sgxfive_mock_backend(e->mock), NULL, &e->dev), 0);
	CHECK_EQ(sgxfive_vm_create(e->dev, &e->vm), 0);
	CHECK_EQ(sgxfive_render_ctx_create(e->vm, SGXFIVE_TRI_MAX_W, SGXFIVE_TRI_MAX_H, &e->ctx),
		 0);
	if (map) {
		CHECK_EQ(sgxfive_bo_create(e->dev, size, DRM_SGXFIVE_BO_ALLOW_CPU_ACCESS, &bo), 0);
		CHECK_EQ(sgxfive_bo_mmap(bo, (void **)&map_p), 0);
		CHECK_EQ(sgxfive_vm_map(e->vm, BGL_SRC, bo, 0, size, 0), 0);
		sgxfive_bgl_fill(map_p, w, h);
	}
	CHECK_EQ(sgxfive_render_create(e->vm, e->ctx, &e->r), 0);
}

static void bg_layer(void)
{
	static const uint32_t sizes[][2] = { { 64, 64 }, { 128, 64 }, { 100, 60 }, { 32, 16 } };
	struct sgxfive_tri_counts n;
	struct sgxfive_tri_params p;
	struct env e;

	for (unsigned int i = 0; i < sizeof(sizes) / sizeof(sizes[0]); i++) {
		bg_layer_env(&e, true, BGL_SRC, true, sizes[i][0], sizes[i][1]);
		sgxfive_tri_default(&p, sizes[i][0], sizes[i][1]);
		p.bg_src = BGL_SRC;
		CHECK_EQ(sgxfive_render_tri(e.r, &p, 0, 0), 0);
		CHECK_EQ(sgxfive_render_wait(e.r, NSEC), 0);
		CHECK_EQ(sgxfive_tri_check(&p, sgxfive_render_fb(e.r), &n), 0);
		CHECK(n.tri > 0);
		CHECK_EQ(n.layer_in_place, n.bg);
		CHECK(n.bg > 0);
		CHECK_EQ(n.layer_elsewhere, 0);
		CHECK_EQ(n.layer_other, 0);
		CHECK_EQ(n.other, 0);
		CHECK_EQ(n.wrong_out, 0);
		CHECK_EQ(sgxfive_render_guard_dirty(e.r, &p), 0);
		/* the object the kernel builds is the layered one: the tag, not the user's words */
		env_fini(&e);
	}
	/*
	 * 64 x 64: every pixel is the triangle's or the layer's (the mock's edge rule: 1098 and
	 * 2998; the hardware's counts differ at the edges)
	 */
	bg_layer_env(&e, true, BGL_SRC, true, 64, 64);
	sgxfive_tri_default(&p, 64, 64);
	p.bg_src = BGL_SRC;
	CHECK_EQ(sgxfive_render_tri(e.r, &p, 0, 0), 0);
	CHECK_EQ(sgxfive_render_wait(e.r, NSEC), 0);
	CHECK_EQ(sgxfive_tri_check(&p, sgxfive_render_fb(e.r), &n), 0);
	CHECK_EQ(n.layer_in_place, 2998);
	CHECK_EQ(n.tri, 1098);
	CHECK_EQ(n.tri + n.layer_in_place, 64 * 64);
	env_fini(&e);

	/* knob on, source 0: refused at submit */
	bg_layer_env(&e, true, 0, true, 64, 64);
	sgxfive_tri_default(&p, 64, 64);
	p.bg_src = BGL_SRC;
	CHECK_EQ(sgxfive_render_tri(e.r, &p, 0, 0), -EINVAL);
	env_fini(&e);
	/* knob on, source set but not mapped: refused at submit */
	bg_layer_env(&e, true, BGL_SRC, false, 64, 64);
	CHECK_EQ(sgxfive_render_tri(e.r, &p, 0, 0), -EINVAL);
	env_fini(&e);
	/* knob off, no layer in the scene: today's image */
	bg_layer_env(&e, false, 0, false, 64, 64);
	sgxfive_tri_default(&p, 64, 64);
	CHECK_EQ(sgxfive_render_tri(e.r, &p, 0, 0), 0);
	CHECK_EQ(sgxfive_render_wait(e.r, NSEC), 0);
	CHECK_EQ(sgxfive_tri_check(&p, sgxfive_render_fb(e.r), &n), 0);
	CHECK_EQ(n.bg, 2998);
	CHECK_EQ(n.layer_in_place, 0);
	env_fini(&e);
}

/*
 * A context renders any target within the maximum it was created with, each
 * dimension on its own, and refuses a job for a larger one without losing
 * the context.
 */
static void max_size(void)
{
	static const uint32_t fits[][4] = {	/* max w, h; target w, h */
		{ 64, 64, 64, 64 }, { 64, 64, 32, 16 }, { 64, 64, 2, 2 },
		{ 1024, 600, 1024, 600 }, { 1024, 600, 600, 600 }, { 1024, 600, 640, 480 },
		{ 1024, 600, 640, 478 }, { 100, 60, 100, 60 },
	};
	static const uint32_t over[][4] = {
		{ 64, 64, 66, 64 }, { 64, 64, 64, 66 }, { 1024, 600, 600, 1024 },
		{ 1024, 600, 2048, 16 }, { 100, 60, 100, 62 },
	};
	struct sgxfive_tri_counts n;
	struct sgxfive_tri_params p;
	struct sgxfive_render *r;
	uint32_t ctx;
	struct env e;

	env_init(&e);
	for (unsigned int i = 0; i < sizeof(fits) / sizeof(fits[0]); i++) {
		CHECK_EQ(sgxfive_render_ctx_create(e.vm, fits[i][0], fits[i][1], &ctx), 0);
		CHECK_EQ(sgxfive_render_create(e.vm, ctx, &r), 0);
		sgxfive_tri_default(&p, fits[i][2], fits[i][3]);
		CHECK_EQ(sgxfive_render_tri(r, &p, 0, 0), 0);
		CHECK_EQ(sgxfive_render_wait(r, NSEC), 0);
		CHECK_EQ(sgxfive_tri_check(&p, sgxfive_render_fb(r), &n), 0);
		CHECK_EQ(n.other, 0);
		sgxfive_render_destroy(r);
		sgxfive_ctx_destroy(e.dev, ctx);
	}
	for (unsigned int i = 0; i < sizeof(over) / sizeof(over[0]); i++) {
		CHECK_EQ(sgxfive_render_ctx_create(e.vm, over[i][0], over[i][1], &ctx), 0);
		CHECK_EQ(sgxfive_render_create(e.vm, ctx, &r), 0);
		sgxfive_tri_default(&p, over[i][2], over[i][3]);
		CHECK_EQ(sgxfive_render_tri(r, &p, 0, 0), -EINVAL);
		/* Refused at submission: the context still renders what fits. */
		sgxfive_tri_default(&p, over[i][0], over[i][1]);
		CHECK_EQ(sgxfive_render_tri(r, &p, 0, 0), 0);
		CHECK_EQ(sgxfive_render_wait(r, NSEC), 0);
		CHECK_EQ(sgxfive_tri_check(&p, sgxfive_render_fb(r), &n), 0);
		sgxfive_render_destroy(r);
		sgxfive_ctx_destroy(e.dev, ctx);
	}
	env_fini(&e);
}

/*
 * A scene larger than the parameter buffer (the mock's render_pb_pages, as
 * debugfs sets the kernel's): the job completes with -ENOSPC, which the wait
 * reports once; the context is not lost and renders what fits. 0x62 pages
 * take 1024 x 768 but not 4096 x 4096, 0x23 not even 64 x 64, as on the
 * hardware; the default takes 4096 x 4096.
 */
static void pb_overflow(void)
{
	static const struct {
		uint32_t pages, w, h;
		int error;
	} runs[] = {
		{ 0x62, 1024, 768, 0 }, { 0x62, 4096, 4096, -ENOSPC }, { 0x62, 64, 64, 0 },
		{ 0x40, 1024, 768, 0 }, { 0x40, 4096, 4096, -ENOSPC },
		{ 0x23, 64, 64, -ENOSPC }, { 0x23, 1024, 768, -ENOSPC },
		{ 0, 4096, 4096, 0 },		/* the default, 0x422 */
	};
	struct sgxfive_tri_counts n;
	struct sgxfive_tri_params p;
	struct env e;

	for (unsigned int i = 0; i < sizeof(runs) / sizeof(runs[0]); i++) {
		const struct sgxfive_mock_config cfg = { .render_pb_pages = runs[i].pages };
		uint32_t sync;

		memset(&e, 0, sizeof(e));
		e.mock = sgxfive_mock_create(&cfg);
		CHECK_EQ(sgxfive_dev_open(sgxfive_mock_backend(e.mock), NULL, &e.dev), 0);
		CHECK_EQ(sgxfive_dev_info(e.dev)->job.render_pb_pages,
			 runs[i].pages ? runs[i].pages : 0x422);
		CHECK_EQ(sgxfive_vm_create(e.dev, &e.vm), 0);
		CHECK_EQ(sgxfive_render_ctx_create(e.vm, 4096, 4096, &e.ctx), 0);
		CHECK_EQ(sgxfive_render_create(e.vm, e.ctx, &e.r), 0);
		CHECK_EQ(sgxfive_syncobj_create(e.dev, false, &sync), 0);
		sgxfive_tri_default(&p, runs[i].w, runs[i].h);
		CHECK_EQ(sgxfive_render_tri(e.r, &p, 0, sync), 0);
		CHECK_EQ(sgxfive_render_wait(e.r, NSEC), runs[i].error);
		CHECK_EQ(sgxfive_render_wait(e.r, NSEC), 0);	/* reported once */
		CHECK_EQ(sgxfive_syncobj_wait(e.dev, sync, 0, NSEC), runs[i].error);
		if (!runs[i].error)
			CHECK_EQ(sgxfive_tri_check(&p, sgxfive_render_fb(e.r), &n), 0);
		/* Not lost: a scene that fits renders, and its job has no error. */
		sgxfive_tri_default(&p, 32, 16);
		p.colour = 0xffff0000;
		if (runs[i].pages == 0x23)
			p.width = p.height = 0;		/* nothing fits: skip */
		if (p.width) {
			CHECK_EQ(sgxfive_render_tri(e.r, &p, 0, 0), 0);
			CHECK_EQ(sgxfive_render_wait(e.r, NSEC), 0);
			CHECK_EQ(sgxfive_tri_check(&p, sgxfive_render_fb(e.r), &n), 0);
		} else {
			sgxfive_tri_default(&p, 64, 64);
			CHECK_EQ(sgxfive_render_tri(e.r, &p, 0, 0), 0);
			CHECK_EQ(sgxfive_render_wait(e.r, NSEC), -ENOSPC);
		}
		sgxfive_syncobj_destroy(e.dev, sync);
		env_fini(&e);
	}
}

/*
 * The kernel's debugfs render_final_pb_pages, as the mock's config: the next render context
 * takes it once; the render that closes a scene a geometry job opened has that PB, the next
 * scene the context's own again. With 0x23 pages 1024 x 768 overflows and with 0x40 it fits;
 * a second context, and a value the kernel would refuse, change nothing.
 */
static void final_pb(void)
{
	static const struct { uint32_t final; int error; } runs[] = {
		{ 0x40, 0 }, { 0, -ENOSPC }, { 0x423, -ENOSPC }, { 0x22, -ENOSPC },
	};
	struct sgxfive_tri_params p;
	struct sgxfive_render *r2;
	uint32_t ctx2;
	struct env e;

	for (unsigned int i = 0; i < sizeof(runs) / sizeof(runs[0]); i++) {
		const struct sgxfive_mock_config cfg = { .render_pb_pages = 0x23,
							 .render_final_pb_pages = runs[i].final };

		memset(&e, 0, sizeof(e));
		e.mock = sgxfive_mock_create(&cfg);
		CHECK_EQ(sgxfive_dev_open(sgxfive_mock_backend(e.mock), NULL, &e.dev), 0);
		CHECK_EQ(sgxfive_vm_create(e.dev, &e.vm), 0);
		CHECK_EQ(sgxfive_render_ctx_create(e.vm, 1024, 768, &e.ctx), 0);
		CHECK_EQ(sgxfive_render_create(e.vm, e.ctx, &e.r), 0);
		sgxfive_tri_default(&p, 1024, 768);
		CHECK_EQ(sgxfive_render_tri_flags(e.r, &p, 0, 0,
						  DRM_SGXFIVE_SUBMIT_JOB_RENDER_GEOMETRY), 0);
		CHECK_EQ(sgxfive_render_wait(e.r, NSEC), 0);
		CHECK_EQ(sgxfive_render_tri(e.r, &p, 0, 0), 0);
		CHECK_EQ(sgxfive_render_wait(e.r, NSEC), runs[i].error);
		/* the next scene, whole: the context's own PB */
		CHECK_EQ(sgxfive_render_tri(e.r, &p, 0, 0), 0);
		CHECK_EQ(sgxfive_render_wait(e.r, NSEC), -ENOSPC);
		/* a second context: the knob was taken */
		CHECK_EQ(sgxfive_render_ctx_create(e.vm, 1024, 768, &ctx2), 0);
		CHECK_EQ(sgxfive_render_create(e.vm, ctx2, &r2), 0);
		CHECK_EQ(sgxfive_render_tri_flags(r2, &p, 0, 0,
						  DRM_SGXFIVE_SUBMIT_JOB_RENDER_GEOMETRY), 0);
		CHECK_EQ(sgxfive_render_wait(r2, NSEC), 0);
		CHECK_EQ(sgxfive_render_tri(r2, &p, 0, 0), 0);
		CHECK_EQ(sgxfive_render_wait(r2, NSEC), -ENOSPC);
		sgxfive_render_destroy(r2);
		sgxfive_ctx_destroy(e.dev, ctx2);
		env_fini(&e);
	}
}

/*
 * fb_fill_set: the target's rows (pads included) hold fb_fill in place of the sentinel when
 * the job is kicked, the guard page after them the sentinel still. A geometry job draws
 * nothing, so its colour buffer is what the host wrote; a later render without it is back
 * to the sentinel and draws as ever.
 */
static void fb_fill(void)
{
	struct sgxfive_tri_counts n;
	struct sgxfive_tri_params p;
	const uint32_t *fb;
	uint32_t other = 0;
	struct env e;

	env_init(&e);
	sgxfive_tri_default(&p, 33, 17);
	p.fb_fill_set = true;
	p.fb_fill = 0x12345678;
	CHECK_EQ(sgxfive_render_tri_flags(e.r, &p, 0, 0, DRM_SGXFIVE_SUBMIT_JOB_RENDER_GEOMETRY), 0);
	CHECK_EQ(sgxfive_render_wait(e.r, NSEC), 0);
	fb = sgxfive_render_fb(e.r);
	for (uint32_t i = 0; i < sgxfive_tri_stride_px(33) * 17; i++)
		other += fb[i] != 0x12345678;
	CHECK_EQ(other, 0);
	CHECK_EQ(sgxfive_render_guard_dirty(e.r, &p), 0);
	sgxfive_tri_default(&p, 33, 17);
	CHECK_EQ(sgxfive_render_tri(e.r, &p, 0, 0), 0);
	CHECK_EQ(sgxfive_render_wait(e.r, NSEC), 0);
	CHECK_EQ(sgxfive_tri_check(&p, sgxfive_render_fb(e.r), &n), 0);
	CHECK_EQ(fb[33], SGXFIVE_TRI_SENTINEL);		/* row 0's pad pixel */
	CHECK_EQ(sgxfive_render_guard_dirty(e.r, &p), 0);
	env_fini(&e);
}

/*
 * fb_keep: the colour buffer is left as the engine's last job left it (no sentinel, no
 * fb_fill) for a reload in the next render (Q038, tri --keep-target). Refused (-EINVAL,
 * nothing submitted) with fb_fill_set, and with no buffer of the target's size to keep (the
 * engine's first render, or a larger target). A geometry job draws nothing on the mock, so
 * what the host or the last job put there survives it.
 */
static void fb_keep(void)
{
	struct sgxfive_tri_counts n;
	struct sgxfive_tri_params p;
	uint32_t *fb;
	uint32_t other = 0;
	struct env e;

	env_init(&e);
	sgxfive_tri_default(&p, 33, 17);
	p.fb_keep = true;
	CHECK_EQ(sgxfive_render_tri(e.r, &p, 0, 0), -EINVAL);	/* nothing to keep yet */
	CHECK_EQ(sgxfive_render_wait(e.r, NSEC), 0);
	p.fb_keep = false;
	p.fb_fill_set = true;
	p.fb_fill = 0x12345678;
	CHECK_EQ(sgxfive_render_tri_flags(e.r, &p, 0, 0, DRM_SGXFIVE_SUBMIT_JOB_RENDER_GEOMETRY), 0);
	CHECK_EQ(sgxfive_render_wait(e.r, NSEC), 0);
	fb = (uint32_t *)sgxfive_render_fb(e.r);
	fb[5] = 0xabcdef01;		/* a word the host changed after the job */
	p.fb_keep = true;
	CHECK_EQ(sgxfive_render_tri_flags(e.r, &p, 0, 0, DRM_SGXFIVE_SUBMIT_JOB_RENDER_GEOMETRY),
		 -EINVAL);		/* fb_keep and fb_fill_set */
	p.fb_fill_set = false;
	CHECK_EQ(sgxfive_render_tri_flags(e.r, &p, 0, 0, DRM_SGXFIVE_SUBMIT_JOB_RENDER_GEOMETRY), 0);
	CHECK_EQ(sgxfive_render_wait(e.r, NSEC), 0);
	CHECK_EQ(fb[5], 0xabcdef01);
	for (uint32_t i = 0; i < sgxfive_tri_stride_px(33) * 17; i++)
		other += i != 5 && fb[i] != 0x12345678;
	CHECK_EQ(other, 0);
	CHECK_EQ(sgxfive_render_guard_dirty(e.r, &p), 0);
	/* a larger target has no buffer of its size to keep */
	sgxfive_tri_default(&p, 1024, 768);
	p.fb_keep = true;
	CHECK_EQ(sgxfive_render_tri(e.r, &p, 0, 0), -EINVAL);
	CHECK_EQ(sgxfive_render_wait(e.r, NSEC), 0);
	CHECK_EQ(fb[5], 0xabcdef01);
	/* a kept render that draws: the mock draws every pixel of the window as ever */
	sgxfive_tri_default(&p, 33, 17);
	p.fb_keep = true;
	CHECK_EQ(sgxfive_render_tri(e.r, &p, 0, 0), 0);
	CHECK_EQ(sgxfive_render_wait(e.r, NSEC), 0);
	CHECK_EQ(sgxfive_tri_check(&p, sgxfive_render_fb(e.r), &n), 0);
	CHECK_EQ(sgxfive_render_guard_dirty(e.r, &p), 0);
	env_fini(&e);
}

/*
 * The scene hook: called on every render once its scene is built, with the engine's CPU
 * view, layout, params and command, before the poke hook; its error fails the render
 * unsubmitted. With sgxfive_tri_probe_apply it puts a probe's programs into the engine's
 * scene (tri --bg-pds/--bg-pixel): a background pixel shader that is a limm fill of
 * 0xff102030 paints the background so on the mock.
 */
struct scene_rec {
	int calls, order, ret;
	uint32_t fb, width;
	struct sgxfive_tri_probe *pr;
};

static int scene_rec_hook(void *priv, const struct sgxfive_tri_cpu *c,
			  const struct sgxfive_tri_layout *l, const struct sgxfive_tri_params *p,
			  struct drm_sgxfive_render_cmd *cmd)
{
	struct scene_rec *s = priv;

	s->calls++;
	s->order = s->order ? s->order : 1;
	s->fb = l->fb;
	s->width = p->width;
	if (s->ret)
		return s->ret;
	return s->pr ? sgxfive_tri_probe_apply(c, l, p, s->pr, cmd) : 0;
}

static int poke_rec_hook(void *priv, const struct sgxfive_poke_view *v, unsigned int n)
{
	struct scene_rec *s = priv;

	s->order = s->order ? s->order : 2;
	return 0;
}

static void scene_hook(void)
{
	struct sgxfive_tri_probe pr = { 0 };
	struct scene_rec s = { 0 };
	struct sgxfive_tri_layout l;
	struct sgxfive_tri_params p;
	struct sgxfive_tri_counts n;
	const uint32_t *usep;
	uint64_t w[2];
	uint32_t bg = 0, tri = 0;
	struct env e;

	env_init(&e);
	sgxfive_tri_default(&p, 64, 64);
	sgxfive_render_set_scene_hook(e.r, scene_rec_hook, &s);
	sgxfive_render_set_hook(e.r, poke_rec_hook, &s);
	CHECK_EQ(sgxfive_render_tri(e.r, &p, 0, 0), 0);
	CHECK_EQ(sgxfive_render_wait(e.r, NSEC), 0);
	sgxfive_render_get_layout(e.r, &l);
	CHECK_EQ(s.calls, 1);
	CHECK_EQ(s.order, 1);			/* before the poke hook */
	CHECK_EQ(s.fb, l.fb);
	CHECK_EQ(s.width, 64);
	CHECK_EQ(sgxfive_tri_check(&p, sgxfive_render_fb(e.r), &n), 0);
	/* an error: the render is not submitted */
	s.ret = -E2BIG;
	CHECK_EQ(sgxfive_render_tri(e.r, &p, 0, 0), -E2BIG);
	CHECK_EQ(sgxfive_render_wait(e.r, NSEC), 0);
	CHECK_EQ(s.calls, 2);
	/* a background pixel shader of the probe's: the background fill's words, 0xff102030 */
	usep = sgxfive_render_page(e.r, DRM_SGXFIVE_HEAP_USSE_PIXEL);
	w[0] = usep[SGXFIVE_TRI_UP_BGFILL / 4] | (uint64_t)usep[SGXFIVE_TRI_UP_BGFILL / 4 + 1] << 32;
	w[1] = usep[SGXFIVE_TRI_UP_BGFILL / 4 + 2] |
	       (uint64_t)usep[SGXFIVE_TRI_UP_BGFILL / 4 + 3] << 32;
	w[1] = sgxfive_limm_set(w[1], 0xff102030);
	pr.slot[SGXFIVE_TRI_SLOT_BGPIXEL] = (struct sgxfive_tri_prog){ w, 2, 0, 32 };
	s.ret = 0;
	s.pr = &pr;
	CHECK_EQ(sgxfive_render_tri(e.r, &p, 0, 0), 0);
	CHECK_EQ(sgxfive_render_wait(e.r, NSEC), 0);
	CHECK_EQ(s.calls, 3);
	for (uint32_t i = 0; i < 64 * 64; i++) {
		bg += sgxfive_render_fb(e.r)[i] == 0xff102030;
		tri += sgxfive_render_fb(e.r)[i] == p.colour;
	}
	CHECK(tri > 0);
	CHECK_EQ(bg + tri, 64 * 64);
	/* NULL: no hook */
	sgxfive_render_set_scene_hook(e.r, NULL, NULL);
	CHECK_EQ(sgxfive_render_tri(e.r, &p, 0, 0), 0);
	CHECK_EQ(sgxfive_render_wait(e.r, NSEC), 0);
	CHECK_EQ(s.calls, 3);
	CHECK_EQ(sgxfive_tri_check(&p, sgxfive_render_fb(e.r), &n), 0);
	env_fini(&e);
}

static long long file_size(const char *path)
{
	struct stat st;

	return stat(path, &st) ? -1 : (long long)st.st_size;
}

static void sleep_ms(long ms)
{
	struct timespec ts = { ms / 1000, (ms % 1000) * 1000000L };

	nanosleep(&ts, NULL);
}

/*
 * The park race of E1085: the kernel parks a closed render context when its last reference
 * goes, which can be after the close ioctl returns, and debugfs render_kept reads 0 bytes
 * until then. With debugfs_dir and kept_park_ms the mock's render context close leaves that
 * directory's render_kept empty for kept_park_ms, then puts its bytes back; a transfer
 * context's close, or kept_park_ms 0, leaves it alone.
 */
static void kept_park(void)
{
	const char *tmp = getenv("TMPDIR");
	char dir[4096], kept[4200], parking[4200];
	static const char bytes[4096] = { [0] = 0x47, [4095] = 0x02 };
	struct sgxfive_mock_config cfg = { 0 };
	char back[4096];
	uint32_t ctx, xctx;
	FILE *f;
	struct env e;
	int waited = 0;

	snprintf(dir, sizeof(dir), "%s/sgxfive-park.XXXXXX", tmp && *tmp ? tmp : "/tmp");
	if (!CHECK(mkdtemp(dir)))
		return;
	snprintf(kept, sizeof(kept), "%s/render_kept", dir);
	snprintf(parking, sizeof(parking), "%s/render_kept.parking", dir);
	f = fopen(kept, "wb");
	CHECK(f && fwrite(bytes, 1, sizeof(bytes), f) == sizeof(bytes));
	if (f)
		fclose(f);
	cfg.debugfs_dir = dir;
	cfg.kept_park_ms = 60;
	memset(&e, 0, sizeof(e));
	e.mock = sgxfive_mock_create(&cfg);
	CHECK_EQ(sgxfive_dev_open(sgxfive_mock_backend(e.mock), NULL, &e.dev), 0);
	CHECK_EQ(sgxfive_vm_create(e.dev, &e.vm), 0);
	CHECK_EQ(sgxfive_ctx_create(e.vm, &xctx), 0);
	CHECK_EQ(sgxfive_ctx_destroy(e.dev, xctx), 0);
	CHECK_EQ(file_size(kept), 4096);		/* a transfer context: no park */
	CHECK_EQ(sgxfive_render_ctx_create(e.vm, 64, 64, &ctx), 0);
	CHECK_EQ(sgxfive_ctx_destroy(e.dev, ctx), 0);
	CHECK_EQ(file_size(kept), 0);			/* closed, not parked yet */
	while (file_size(kept) != 4096 && waited < 3000) {
		sleep_ms(5);
		waited += 5;
	}
	CHECK(waited >= 40 && waited < 3000);
	f = fopen(kept, "rb");
	CHECK(f && fread(back, 1, sizeof(back), f) == sizeof(back));
	if (f)
		fclose(f);
	CHECK(!memcmp(back, bytes, sizeof(bytes)));
	CHECK_EQ(file_size(parking), -1);
	sgxfive_vm_destroy(e.vm);
	sgxfive_dev_close(e.dev);
	sgxfive_mock_destroy(e.mock);

	/* kept_park_ms 0: a render context's close leaves render_kept as it is */
	cfg.kept_park_ms = 0;
	e.mock = sgxfive_mock_create(&cfg);
	CHECK_EQ(sgxfive_dev_open(sgxfive_mock_backend(e.mock), NULL, &e.dev), 0);
	CHECK_EQ(sgxfive_vm_create(e.dev, &e.vm), 0);
	CHECK_EQ(sgxfive_render_ctx_create(e.vm, 64, 64, &ctx), 0);
	CHECK_EQ(sgxfive_ctx_destroy(e.dev, ctx), 0);
	CHECK_EQ(file_size(kept), 4096);
	sgxfive_vm_destroy(e.vm);
	sgxfive_dev_close(e.dev);
	sgxfive_mock_destroy(e.mock);
	unlink(kept);
	rmdir(dir);
}

int main(void)
{
	query();
	triangle();
	odd_width();
	rules();
	aa4();
	max_size();
	fault();
	fault_wait();
	pb_overflow();
	final_pb();
	transfers();
	bg_layer();
	fb_fill();
	fb_keep();
	scene_hook();
	kept_park();
	return tap_done();
}
