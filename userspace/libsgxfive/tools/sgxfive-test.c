// SPDX-License-Identifier: MIT
/*
 * sgxfive-test: the kernel's debugfs checks (dri/N/sgx/...) redone from
 * userspace through the sgxfive render node, and the hardware probes.
 *
 *   sgxfive-test [--mock[=rev1|harness|none]] [--mock-pb-pages=N] [--device PATH]
 *                [--programs=asm|fake] <command> [options]
 *
 *   query                         DEV_QUERY: GPU, firmware, job limits, heaps
 *   dummy [-n N]                  N dummy transfers chained through one syncobj
 *   fill  [--width W --height H --x X --y Y --stride S --colour C] [JOB OPTIONS]
 *   copy  [--width W --height H --sx X --sy Y --src-stride S --dx X --dy Y --dst-stride S]
 *         [--every-value]
 *         [JOB OPTIONS]
 *   isolation                     VM separation, faults, lost contexts, read-only maps
 *   tri   [--width W --height H -n N] [--max-width W --max-height H] [--fault]
 *         [--scratch N [--scratch-fill V]] [--kpoke-render N:SPEC]... [--move N:DX,DY]...
 *         [--geometry N]... [--keep-going] [--dump-render DIR] [JOB OPTIONS]
 *                                 the first triangle on a render context, N times,
 *                                 every pixel against the CPU reference; the context
 *                                 takes targets up to --max-width x --max-height
 *                                 (default: the target's size); --fault unmaps the
 *                                 scene's stream first, so the render faults;
 *                                 --scratch maps N more pages (their address printed)
 *                                 for a kernel poke to point a unit at, filled with V
 *                                 (default 0.25f) before each render, the dwords it
 *                                 changed reported page by page; --kpoke-render writes
 *                                 SPEC to debugfs kpoke just before render N (each
 *                                 render of the context its own kernel pokes); --move
 *                                 draws render N's triangle DX, DY pixels away;
 *                                 --geometry submits render N geometry only (the scene
 *                                 left open for the next render, nothing drawn);
 *                                 --keep-going reports every render, checked or not
 *                                 --dump-render DIR: after the renders, the kernel's
 *                                 debugfs render_param and render_tadata copied to
 *                                 DIR/tri.param.bin and DIR/tri.tadata.bin
 *   contexts [--width W --height H -n N]  N render contexts for targets up to W x H
 *                                 in one VM, and the memory they take (MemFree and
 *                                 LowFree of /proc/meminfo, before and after)
 *   regaccess                     client fill shaders that read and write SGX
 *                                 registers, read temporaries they did not write
 *                                 and kick code base 15
 *   probe [--temps N] [--coords] [--pixels] [--pds N --use USE] [--poke xfer:N=V]...
 *         [--low ADDR] [--late R:K=V] FILE...
 *                                 each FILE (tools/usse-asm output) as the fill
 *                                 shader of its own fill, with N temporaries
 *                                 (default 32) and a 64 KiB scratch buffer; prints
 *                                 o0 and the scratch dwords the program changed;
 *                                 --coords: as the copy shader of a copy whose
 *                                 source texel (x, y) is (y << 16) | x, so pa0 holds
 *                                 the pixel's coordinates; --pixels: every pixel too;
 *                                 --pds N --use USE: each FILE is a PDS program with N
 *                                 data dwords (U0-U2 in dwords 0-2 are set to kick the
 *                                 secondary USE task) as the fill's PDS secondary,
 *                                 USE its shader (a USE program that stores the
 *                                 secondary attributes sa0-sa15); --low ADDR: the scratch
 *                                 buffer mapped again at ADDR, a page in the first MiB
 *                                 (page 0 excepted), for the PDS's load and store; needs
 *                                 the kernel's debugfs sgx/vm_low; --late R:K=V: while
 *                                 the job runs, once scratch dword R leaves its fill
 *                                 (or after LATE_NS), the host writes V to dword K
 *   probe --tri SLOT[:N] [--slot SLOT=FILE[:N]]... [--width W --height H]
 *         [--max-width W --max-height H] [--vertices N [--copy-depth]] [--vtx-coords N]
 *         [--isp2 V] [--blk-add BIT=V[,V]]...
 *         [--blk N=V]... [--cmd N=V]... [--vdm N=V]... [--sideband V] [--temps N]
 *         [--pixels] [--dump-render DIR] [--kpoke SPEC]...
 *         [--obj2 FIRST [--obj2-blk N=V]... [--obj2-pixel FILE]] FILE...
 *                                 each FILE as the program SLOT (pixev, eot, vtxpds,
 *                                 vtxuse, pixel, pixtask, pixpds, state; a PDS one with
 *                                 N data dwords) of the
 *                                 first triangle's render, W x H (default 64 x 64),
 *                                 on a render context for up to --max-width x
 *                                 --max-height (default W x H); each --slot FILE
 *                                 replaces another slot's program in every render;
 *                                 --vertices N (3 to 15, whole triangles): copies of
 *                                 the triangle after it, for the vertex programs;
 *                                 --vtx-coords N (1 to 11): N more output dwords per
 *                                 vertex, coordinate sets of four and the rest
 *                                 (OUTSEL, coordsize);
 *                                 --copy-depth: copy c at clip z = c / 16; --isp2 V:
 *                                 ISP word 2 (stencil) V in the state block, in place
 *                                 of the wrap word; --blk-add BIT=V[,V]: presence
 *                                 bit BIT (2-5, or 7 with two words) and its words
 *                                 added to the state block, which grows; --blk N=V:
 *                                 the state block's word N is V; --cmd N=V: the
 *                                 render command's word N is V; --vdm N=V: the
 *                                 VDM stream's word N is V (after --vtx-coords), with
 *                                 N^=V flipped by V;
 *                                 --dump-render DIR: after the render, the kernel's
 *                                 debugfs render_param and render_tadata copied to
 *                                 DIR/NAME.param.bin and DIR/NAME.tadata.bin;
 *                                 --kpoke SPEC: written to the kernel's debugfs kpoke
 *                                 before each case's render (the job's kernel words).
 *                                 --sideband V (with an eot slot): the end-of-tile
 *                                 emitpix2's sideband, 0x200 by default.
 *                                 --obj2 FIRST (with --vertices): the copies from
 *                                 vertex FIRST on as a second object, its state block
 *                                 the first's with --obj2-blk N=V words set and its
 *                                 pixel shader --obj2-pixel FILE (or the default fill).
 *                                 Patched as the defaults (sgxfive_tri_probe.h), with
 *                                 the scratch buffer; prints the target's pixels as o0
 *                                 and every scratch dword changed
 *
 * JOB OPTIONS (fill, copy, tri), for sweeps (one job run many times with one
 * word changed each time):
 *   --poke SPACE:INDEX=VALUE, --poke SPACE:INDEX^=VALUE (repeatable)
 *                                 set or flip one word of the built job right before
 *                                 it is submitted (include/sgxfive_poke.h: cmd, xfer,
 *                                 vdm, eos, blk, pds:SLOT, tex, bg)
 *   --pixels                      every pixel of the target, a row a line
 *   --regs LO-HI                  the SGX registers LO to HI after the job, read-only
 *                                 through /dev/mem (hardware only)
 *   --every-value                 copy: a source with every value of every channel in
 *                                 each run of 256 pixels, a permutation per channel
 * They print the job's result, the target's hash, the pixels that differ from the
 * CPU reference (and the first) and the dwords written outside the target.
 *
 * fill, copy and isolation take their GPU programs from the assembled source
 * (our own code, default) or the fake test double (--programs=fake, mock only).
 *
 * A job that faults or hangs is recovered and fails: the commands report its
 * error as the wait returns it ("job faulted, context lost (...)"). A render
 * whose scene overflows the parameter buffer fails with -ENOSPC and keeps its
 * context ("scene overflowed the parameter buffer, context kept (...)"); on
 * the hardware debugfs sgx/render_pb_pages shrinks the PB of new render
 * contexts, in the mock --mock-pb-pages=N (0x23 to 0x422) does.
 *
 * Exit status: 0 all checks passed, 1 a check or call failed, 2 usage.
 */
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>

#include "sgxfive_mock.h"
#include "sgxfive_poke.h"
#include "sgxfive_render.h"
#include "sgxfive_tri_probe.h"
#include "sgxfive_xfer.h"

#define SENTINEL	0xdeadbeefu
#define WAIT_NS		(5LL * 1000000000LL)
/* A fault is found by the driver's BIF poll (a fault and no progress over two 50 ms
 * polls), not the 500 ms job timeout. */
#define FAULT_NS	(300LL * 1000000LL)
#define LATE_NS		(200LL * 1000000LL)	/* --late: how long the host waits for ready */

static long long now_ns(void)
{
	struct timespec ts;

	clock_gettime(CLOCK_MONOTONIC, &ts);
	return ts.tv_sec * 1000000000LL + ts.tv_nsec;
}

static const char *const heap_names[DRM_SGXFIVE_HEAP_COUNT] = {
	"GENERAL", "TEXTURE", "PDS_PIXEL", "PDS_VERTEX", "USSE_PIXEL", "USSE_VERTEX",
	"KERNEL_CODE", "KERNEL_DATA", "PARAMETERS", "TA_DATA",
};

#define KPR_MAX	16

struct opts {
	uint32_t width, height, x, y, stride, colour;
	uint32_t sx, sy, src_stride, dst_stride;
	uint32_t n;
	uint32_t max_width, max_height;	/* tri: the render context's; 0: the target's */
	bool fault;			/* tri: unmap the scene's stream page first */
	uint32_t scratch;		/* tri: pages of a scratch buffer for kernel pokes */
	uint32_t scratch_fill;		/* tri: the scratch buffer's dwords before a render */
	/* tri: kernel pokes written to debugfs kpoke just before render n (--kpoke-render) */
	struct { uint32_t n; const char *spec; } kpr[KPR_MAX];
	unsigned int nkpr;
	uint32_t geometry;		/* tri: renders submitted geometry only (bit n - 1) */
	const char *dump_dir;		/* tri: the scene's memory there after the renders */
	bool keep_going;		/* tri: go on after a render that does not check */
	/* tri: render n's triangle moved by dx, dy pixels (--move) */
	struct { uint32_t n; int32_t dx, dy; } moves[KPR_MAX];
	unsigned int nmoves;
	bool every_value;		/* copy: the every-value source pattern */
	/* job options (fill, copy, tri) */
	struct sgxfive_poke pokes[SGXFIVE_POKE_MAX];
	const char *poke_args[SGXFIVE_POKE_MAX];
	unsigned int npokes;
	bool pixels;			/* print every pixel of the target */
	bool regs;			/* print the registers regs_lo..regs_hi after the job */
	uint32_t regs_lo, regs_hi;
};

struct tool {
	struct sgxfive_mock *mock;
	struct sgxfive_dev *dev;
	struct sgxfive_prog_source *progs;
};

static int usage(void)
{
	fprintf(stderr,
		"usage: sgxfive-test [--mock[=rev1|harness|none]] [--mock-pb-pages=N]\n"
		"                    [--device PATH] [--programs=asm|fake] <command>\n"
		"       commands: query, dummy [-n N], isolation, regaccess,\n"
		"                 fill [--width W --height H --x X --y Y --stride S --colour C],\n"
		"                 copy [--width W --height H --sx X --sy Y --src-stride S\n"
		"                       --dx X --dy Y --dst-stride S --every-value],\n"
		"                 tri [--width W --height H -n N --max-width W --max-height H\n"
		"                      --fault --scratch N --scratch-fill V\n"
		"                      --kpoke-render N:SPEC --move N:DX,DY --geometry N\n"
		"                      --keep-going --dump-render DIR],\n"
		"                 fill, copy and tri also take [--poke SPACE:INDEX=VALUE]...\n"
		"                      [--poke SPACE:INDEX^=VALUE]... [--pixels] [--regs LO-HI],\n"
		"                 contexts [--width W --height H -n N],\n"
		"                 probe [--temps N] [--coords] [--pixels] [--pds N --use USE]\n"
		"                       [--poke xfer:N=V]... [--low ADDR] [--late R:K=V] FILE...,\n"
		"                 probe --tri SLOT[:N] [--slot SLOT=FILE[:N]]... [--width W\n"
		"                       --height H --max-width W --max-height H] [--vertices N]\n"
		"                       [--copy-depth] [--vtx-coords N] [--isp2 V]\n"
		"                       [--blk-add BIT=V[,V]]... [--blk N=V]...\n"
		"                       [--cmd N=V]... [--vdm N=V]... [--sideband V]\n"
		"                       [--dump-render DIR] [--kpoke SPEC]...\n"
		"                       [--obj2 FIRST [--obj2-blk N=V]... [--obj2-pixel FILE]]\n"
		"                       [--temps N] [--pixels] FILE...\n");
	return 2;
}

static int fail(const char *what, int err)
{
	fprintf(stderr, "sgxfive-test: %s: %s\n", what, strerror(-err));
	return 1;
}

/*
 * What a wait's error says about the job (sgxfive_syncobj_wait): a job that
 * faulted or hung was recovered and failed, and its context is lost; a render
 * whose scene overflowed the parameter buffer failed, and its context is
 * kept. Other errors are the wait's own, as strerror.
 */
static const char *job_error(int err, char *buf, size_t len)
{
	const char *what = err == -EIO ? "job faulted" : err == -ETIMEDOUT ? "job hung" :
			   err == -ECANCELED ? "job cancelled" : NULL;

	if (err == -ENOSPC)
		snprintf(buf, len, "scene overflowed the parameter buffer, context kept (%s)",
			 strerror(-err));
	else if (what)
		snprintf(buf, len, "%s, context lost (%s)", what, strerror(-err));
	else
		snprintf(buf, len, "%s", strerror(-err));
	return buf;
}

static int fail_job(const char *what, int err)
{
	char buf[96];

	fprintf(stderr, "sgxfive-test: %s: %s\n", what, job_error(err, buf, sizeof(buf)));
	return 1;
}

/* ---- Job results (fill, copy, tri) ------------------------------------------------- */

/*
 * The SGX register bank, physical (the laptop's: BAR 0 + 0x80000), and the
 * part of it --regs reads; SGXFIVE_REGS_BASE overrides the base.
 */
#define REGS_BASE	0x80080000ull
#define REGS_SIZE	0x4000u

/* The job: ok, rejected (the submission's error) or failed (the wait's). */
static void print_job(int submit_err, int wait_err)
{
	char buf[96];

	if (submit_err)
		printf("job: rejected (%s)\n", strerror(-submit_err));
	else if (wait_err)
		printf("job: failed: %s\n", job_error(wait_err, buf, sizeof(buf)));
	else
		printf("job: ok\n");
}

/* A target's pixels (row y at px + y * stride dwords) and their CPU reference. */
struct target {
	uint32_t width, height, stride;
	const uint32_t *px;
	/* Whether v is right at (x, y); *want the expected value. */
	bool (*ok)(const void *ctx, uint32_t x, uint32_t y, uint32_t v, uint32_t *want);
	const void *ctx;
};

/*
 * The target's hash (sgxfive_hash_dwords of its pixels, row after row), the
 * pixels that differ from the reference and the first of them, the dwords
 * written outside it, and with --pixels every pixel.
 */
static void print_target(const struct target *g, uint32_t outside, bool pixels)
{
	const uint64_t n = (uint64_t)g->width * g->height;
	uint32_t *buf = calloc(n + 1, 4), bad = 0, fx = 0, fy = 0, fv = 0, fw = 0;

	if (!buf) {
		printf("target: %ux%u (out of memory)\n", g->width, g->height);
		return;
	}
	for (uint32_t y = 0; y < g->height; y++)
		for (uint32_t x = 0; x < g->width; x++) {
			const uint32_t v = g->px[(uint64_t)y * g->stride + x];
			uint32_t want;

			buf[(uint64_t)y * g->width + x] = v;
			if (!g->ok(g->ctx, x, y, v, &want) && !bad++) {
				fx = x;
				fy = y;
				fv = v;
				fw = want;
			}
		}
	printf("target: %ux%u hash 0x%016llx\n", g->width, g->height,
	       (unsigned long long)sgxfive_hash_dwords(buf, n));
	if (bad)
		printf("diff: %u of %llu pixels, first (%u, %u) 0x%08x expected 0x%08x\n", bad,
		       (unsigned long long)n, fx, fy, fv, fw);
	else
		printf("diff: 0 of %llu pixels\n", (unsigned long long)n);
	printf("outside: %u dwords\n", outside);
	for (uint32_t y = 0; pixels && y < g->height; y++) {
		printf("row %u:", y);
		for (uint32_t x = 0; x < g->width; x++)
			printf(" 0x%08x", buf[(uint64_t)y * g->width + x]);
		putchar('\n');
	}
	free(buf);
}

/* --regs: the registers LO..HI after the job, read-only through /dev/mem. */
static void print_regs(const struct tool *t, const struct opts *o)
{
	const char *env = getenv("SGXFIVE_REGS_BASE");
	const unsigned long long base = env ? strtoull(env, NULL, 0) : REGS_BASE;
	const size_t len = ((size_t)o->regs_hi + 4 + SGXFIVE_PAGE_SIZE - 1) &
			   ~(size_t)(SGXFIVE_PAGE_SIZE - 1);
	volatile const uint32_t *m;
	int fd;

	if (!o->regs)
		return;
	if (t->mock) {
		printf("regs: not available on the mock\n");
		return;
	}
	fd = open("/dev/mem", O_RDONLY | O_SYNC);
	if (fd < 0) {
		printf("regs: /dev/mem: %s\n", strerror(errno));
		return;
	}
	m = mmap(NULL, len, PROT_READ, MAP_SHARED, fd, (off_t)base);
	close(fd);
	if (m == MAP_FAILED) {
		printf("regs: mmap 0x%llx: %s\n", base, strerror(errno));
		return;
	}
	printf("regs: 0x%04x-0x%04x at 0x%llx\n", o->regs_lo, o->regs_hi, base);
	for (uint32_t off = o->regs_lo; off <= o->regs_hi; off += 4)
		printf("reg 0x%04x 0x%08x\n", off, m[off / 4]);
	munmap((void *)m, len);
}

/* ---- query -------------------------------------------------------------------------- */

static int cmd_query(struct tool *t)
{
	const struct sgxfive_info *i = sgxfive_dev_info(t->dev);

	printf("device          %s\n", sgxfive_dev_path(t->dev));
	printf("core_id         0x%08x\n", i->gpu.core_id);
	printf("core_revision   0x%08x\n", i->gpu.core_revision);
	if (i->gpu.flags & DRM_SGXFIVE_GPU_INFO_SW_VALID)
		printf("core_sw         %u rev 0x%x\n", i->gpu.core_id_sw,
		       i->gpu.core_revision_sw);
	printf("host_bridge_rev %u\n", i->gpu.host_bridge_rev);
	printf("quirks          0x%llx%s\n", (unsigned long long)i->gpu.quirks,
	       i->gpu.quirks & DRM_SGXFIVE_QUIRK_SAMPLE_CACHE ? " SAMPLE_CACHE" : "");
	printf("ddk             %u.%u.%u build %u options 0x%x\n", i->fw.ddk_version >> 16,
	       (i->fw.ddk_version >> 8) & 0xff, i->fw.ddk_version & 0xff, i->fw.ddk_build,
	       i->fw.build_options);
	printf("fw_format       %u\n", i->fw.fw_format);
	printf("fw_state        %u\n", i->fw.state);
	printf("job_types       0x%llx\n", (unsigned long long)i->job.job_types);
	printf("max_jobs        %u\n", i->job.max_jobs);
	printf("max_sync_ops    %u\n", i->job.max_sync_ops);
	printf("transfer_cmd    0x%x\n", i->job.transfer_cmd_size);
	printf("max_updates     %u\n", i->job.max_updates);
	printf("render_cmd      0x%x pb 0x%x pages max %ux%u\n", i->job.render_cmd_size,
	       i->job.render_pb_pages, i->job.render_max_width, i->job.render_max_height);
	printf("pixel_parts     %u\n", i->runtime.num_pixel_partitions);
	printf("tile            %ux%u\n", i->runtime.tile_width, i->runtime.tile_height);
	for (uint32_t h = 0; h < DRM_SGXFIVE_HEAP_COUNT && h < i->num_heaps; h++) {
		const struct drm_sgxfive_heap *hp = &i->heaps[h];
		char name[32];

		snprintf(name, sizeof(name), "heap %s", heap_names[h]);
		if (!hp->size) {
			printf("%-16s absent\n", name);
			continue;
		}
		printf("%-16s base 0x%08llx size 0x%08llx%s%s\n", name,
		       (unsigned long long)hp->base, (unsigned long long)hp->size,
		       hp->flags & DRM_SGXFIVE_HEAP_RESERVED ? " RESERVED" : "",
		       hp->flags & DRM_SGXFIVE_HEAP_FIXED_WINDOWS ? " FIXED_WINDOWS" : "");
	}
	return 0;
}

/* ---- Shared set-up ------------------------------------------------------------------ */

struct side {
	struct sgxfive_vm *vm;
	uint32_t ctx;
	struct sgxfive_xfer *x;
};

static int side_init(struct tool *t, struct side *s)
{
	int ret;

	memset(s, 0, sizeof(*s));
	ret = sgxfive_vm_create(t->dev, &s->vm);
	if (!ret)
		ret = sgxfive_ctx_create(s->vm, &s->ctx);
	if (!ret && t->progs)
		ret = sgxfive_xfer_create(s->vm, s->ctx, t->progs, &s->x);
	return ret;
}

static void side_fini(struct tool *t, struct side *s)
{
	sgxfive_xfer_destroy(s->x);
	if (s->ctx)
		sgxfive_ctx_destroy(t->dev, s->ctx);
	sgxfive_vm_destroy(s->vm);
}

/* A CPU-visible BO of `pages` pages at addr (0: allocate in GENERAL), set to SENTINEL. */
static int surface(struct tool *t, struct sgxfive_vm *vm, uint32_t pages, uint32_t flags,
		   uint64_t *addr, struct sgxfive_bo **bo, uint32_t **map)
{
	const uint64_t size = pages * (uint64_t)SGXFIVE_PAGE_SIZE;
	void *p = NULL;
	int ret;

	ret = sgxfive_bo_create(t->dev, size, DRM_SGXFIVE_BO_ALLOW_CPU_ACCESS, bo);
	if (!ret)
		ret = sgxfive_bo_mmap(*bo, &p);
	if (!ret && !*addr)
		ret = sgxfive_vm_alloc(vm, DRM_SGXFIVE_HEAP_GENERAL, size, SGXFIVE_PAGE_SIZE, addr);
	if (!ret)
		ret = sgxfive_vm_map(vm, *addr, *bo, 0, size, flags);
	if (ret)
		return ret;
	*map = p;
	for (uint64_t i = 0; i < size / 4; i++)
		(*map)[i] = SENTINEL;
	return 0;
}

static uint32_t pages_for(uint32_t stride, uint32_t rows)
{
	const uint64_t bytes = (uint64_t)stride * rows;

	/* The surface plus one guard page. */
	return (uint32_t)((bytes + SGXFIVE_PAGE_SIZE - 1) / SGXFIVE_PAGE_SIZE) + 1;
}

/* ---- dummy -------------------------------------------------------------------------- */

static int cmd_dummy(struct tool *t, const struct opts *o)
{
	struct side s;
	uint32_t sync = 0;
	int ret = side_init(t, &s);

	if (!ret)
		ret = sgxfive_syncobj_create(t->dev, false, &sync);
	for (uint32_t i = 0; !ret && i < o->n; i++)
		ret = sgxfive_submit_transfer(t->dev, s.ctx, DRM_SGXFIVE_SUBMIT_JOB_TRANSFER_DUMMY,
					      NULL, i ? sync : 0, sync);
	if (!ret)
		ret = sgxfive_syncobj_wait(t->dev, sync, 0, WAIT_NS);
	if (sync)
		sgxfive_syncobj_destroy(t->dev, sync);
	side_fini(t, &s);
	if (ret)
		return fail("dummy", ret);
	printf("dummy: %u jobs ok\n", o->n);
	return 0;
}

/* ---- fill and copy ------------------------------------------------------------------ */

static bool in_rect(const struct sgxfive_rect *r, uint32_t x, uint32_t y)
{
	return x >= r->x0 && x < r->x1 && y >= r->y0 && y < r->y1;
}

/* The dwords of a destination buffer of `words` dwords outside rect that are not SENTINEL. */
static uint32_t outside_rect(const uint32_t *p, uint32_t words, uint32_t stride_words,
			     const struct sgxfive_rect *r)
{
	uint32_t n = 0;

	for (uint32_t i = 0; i < words; i++)
		n += !in_rect(r, i % stride_words, i / stride_words) && p[i] != SENTINEL;
	return n;
}

static bool fill_ok(const void *ctx, uint32_t x, uint32_t y, uint32_t v, uint32_t *want)
{
	*want = *(const uint32_t *)ctx;
	return v == *want;
}

/* Wait for a fill or copy unless its submission failed; print the job line; the error. */
static int xfer_job(struct side *s, int submit_err)
{
	int wait_err = 0;

	if (!submit_err)
		wait_err = sgxfive_xfer_wait(s->x, WAIT_NS);
	print_job(submit_err, wait_err);
	return submit_err ? submit_err : wait_err;
}

static int cmd_fill(struct tool *t, const struct opts *o)
{
	const struct sgxfive_rect r = { o->x, o->y, o->x + o->width, o->y + o->height };
	const uint32_t rows = o->y + o->height, pages = pages_for(o->stride, rows);
	struct sgxfive_bo *bo = NULL;
	struct sgxfive_surface dst;
	uint32_t *p = NULL, bad = 0;
	uint64_t addr = 0;
	struct side s;
	int ret = side_init(t, &s);

	if (!ret)
		ret = surface(t, s.vm, pages, 0, &addr, &bo, &p);
	dst = (struct sgxfive_surface){ addr, o->stride / 4, rows, o->stride };
	if (!ret) {
		sgxfive_xfer_set_hook(s.x, sgxfive_poke_hook,
				      &(struct sgxfive_poke_set){ o->pokes, o->npokes });
		ret = xfer_job(&s, sgxfive_xfer_fill(s.x, &dst, &r, o->colour, 0));
		print_regs(t, o);
		print_target(&(struct target){ o->width, o->height, o->stride / 4,
					       p + (uint64_t)o->y * (o->stride / 4) + o->x,
					       fill_ok, &o->colour },
			     outside_rect(p, pages * 1024, o->stride / 4, &r), o->pixels);
	}
	for (uint32_t i = 0; !ret && i < pages * 1024; i++) {
		uint32_t x = i % (o->stride / 4), y = i / (o->stride / 4);
		bool in = in_rect(&r, x, y);

		if (p[i] != (in ? o->colour : SENTINEL) && !bad++)
			printf("fill: dword %u (%u, %u) = 0x%08x\n", i, x, y, p[i]);
	}
	sgxfive_bo_destroy(bo);
	side_fini(t, &s);
	if (ret)
		return fail("fill", ret);
	if (bad) {
		printf("fill: FAIL, %u wrong dwords\n", bad);
		return 1;
	}
	printf("fill: ok, %ux%u at (%u, %u), stride %u, colour 0x%08x\n", o->width, o->height,
	       o->x, o->y, o->stride, o->colour);
	return 0;
}

/*
 * The copy's source texel (x, y) of a source sw pixels wide. --every-value: n = y * sw + x
 * runs through every byte value in each channel, each through its own permutation (odd
 * multipliers), so any per-channel function of the value shows in one job.
 */
static uint32_t pattern(const struct opts *o, uint32_t x, uint32_t y)
{
	const uint32_t n = (y * (o->src_stride / 4) + x) & 0xff;

	if (o->every_value)
		return n << 24 | ((n * 167 + 13) & 0xff) << 16 | ((n * 29 + 101) & 0xff) << 8 |
		       ((n * 93 + 57) & 0xff);
	return 0xa5000000 | (y & 0xff) << 16 | (x & 0xff) << 8 | ((x ^ y) & 0xff);
}

/* The copy's reference: the source pattern at (sx, sy) + (x, y). */
static bool copy_ok(const void *ctx, uint32_t x, uint32_t y, uint32_t v, uint32_t *want)
{
	const struct opts *o = ctx;

	*want = pattern(o, o->sx + x, o->sy + y);
	return v == *want;
}

static int cmd_copy(struct tool *t, const struct opts *o)
{
	const struct sgxfive_rect r = { o->x, o->y, o->x + o->width, o->y + o->height };
	const uint32_t srows = o->sy + o->height, drows = o->y + o->height;
	const uint32_t spages = pages_for(o->src_stride, srows);
	const uint32_t dpages = pages_for(o->dst_stride, drows);
	struct sgxfive_bo *sbo = NULL, *dbo = NULL;
	struct sgxfive_surface src, dst;
	uint32_t *s = NULL, *d = NULL, bad = 0;
	const uint32_t sw = o->src_stride / 4, dw = o->dst_stride / 4;
	uint64_t saddr = 0, daddr = 0;
	struct side sd;
	int ret = side_init(t, &sd);

	if (!ret)
		ret = surface(t, sd.vm, spages, DRM_SGXFIVE_VM_MAP_READ_ONLY, &saddr, &sbo, &s);
	if (!ret)
		ret = surface(t, sd.vm, dpages, 0, &daddr, &dbo, &d);
	for (uint32_t i = 0; !ret && i < spages * 1024; i++)
		s[i] = pattern(o, i % sw, i / sw);
	src = (struct sgxfive_surface){ saddr, sw, srows, o->src_stride };
	dst = (struct sgxfive_surface){ daddr, dw, drows, o->dst_stride };
	if (!ret) {
		sgxfive_xfer_set_hook(sd.x, sgxfive_poke_hook,
				      &(struct sgxfive_poke_set){ o->pokes, o->npokes });
		ret = xfer_job(&sd, sgxfive_xfer_copy(sd.x, &src, o->sx, o->sy, &dst, &r, 0));
		print_regs(t, o);
		print_target(&(struct target){ o->width, o->height, dw,
					       d + (uint64_t)o->y * dw + o->x, copy_ok, o },
			     outside_rect(d, dpages * 1024, dw, &r), o->pixels);
	}
	for (uint32_t i = 0; !ret && i < dpages * 1024; i++) {
		uint32_t x = i % dw, y = i / dw;
		bool in = in_rect(&r, x, y);
		uint32_t want = in ? pattern(o, o->sx + x - r.x0, o->sy + y - r.y0) : SENTINEL;

		if (d[i] != want && !bad++)
			printf("copy: dword %u (%u, %u) = 0x%08x, expected 0x%08x\n", i, x, y,
			       d[i], want);
	}
	sgxfive_bo_destroy(sbo);
	sgxfive_bo_destroy(dbo);
	side_fini(t, &sd);
	if (ret)
		return fail("copy", ret);
	if (bad) {
		printf("copy: FAIL, %u wrong dwords\n", bad);
		return 1;
	}
	printf("copy: ok, %ux%u from (%u, %u) to (%u, %u)\n", o->width, o->height, o->sx,
	       o->sy, o->x, o->y);
	return 0;
}

/* ---- isolation ---------------------------------------------------------------------- */

static int check(int *failed, bool ok, const char *name)
{
	printf("%s %s\n", ok ? "PASS" : "FAIL", name);
	*failed += !ok;
	return ok;
}

static bool untouched(const uint32_t *p, uint32_t words)
{
	for (uint32_t i = 0; i < words; i++)
		if (p[i] != SENTINEL)
			return false;
	return true;
}

static bool filled(const uint32_t *p, uint32_t words, uint32_t colour)
{
	for (uint32_t i = 0; i < words; i++)
		if (p[i] != colour)
			return false;
	return true;
}

/*
 * The xfer_iso / alias_ro / xfer_ro checks: two VMs, a transfer context in
 * each. Order matters: the fault checks lose context A, then context B.
 */
static int cmd_isolation(struct tool *t)
{
	const struct sgxfive_info *info = sgxfive_dev_info(t->dev);
	const struct sgxfive_rect r = { 0, 0, 64, 32 };
	struct sgxfive_bo *ba = NULL, *bb = NULL, *bo = NULL, *bro = NULL, *bk = NULL;
	struct sgxfive_bo *bq = NULL, *bm = NULL;
	uint32_t *pa = NULL, *pb = NULL, *po = NULL, *pro = NULL, *pq = NULL, *pm = NULL;
	uint64_t shared = 0, only_b = 0, ro = 0, only_d = 0, mine = 0;
	struct sgxfive_surface dst = { 0, 64, 32, 256 };
	struct side A, B, C = { 0 }, D = { 0 };
	struct sgxfive_vm *banned_vm = NULL;
	uint32_t banned_ctx = 0;
	long long t0;
	int failed = 0, ret;

	ret = side_init(t, &A);
	if (!ret)
		ret = side_init(t, &B);
	if (ret)
		return fail("isolation set-up", ret);

	/* 1. The kernel heaps can never be mapped. */
	ret = sgxfive_bo_create(t->dev, SGXFIVE_PAGE_SIZE, 0, &bk);
	check(&failed, !ret && sgxfive_vm_map(A.vm,
		info->heaps[DRM_SGXFIVE_HEAP_KERNEL_CODE].base, bk, 0, SGXFIVE_PAGE_SIZE, 0) ==
		-EINVAL && sgxfive_vm_map(A.vm, info->heaps[DRM_SGXFIVE_HEAP_KERNEL_DATA].base,
		bk, 0, SGXFIVE_PAGE_SIZE, DRM_SGXFIVE_VM_MAP_READ_ONLY) == -EINVAL,
	      "kernel-heap-unmappable");

	/* 2. One address, two VMs, two BOs: a fill through A lands only in A's BO. */
	ret = surface(t, A.vm, 2, 0, &shared, &ba, &pa);
	if (!ret)
		ret = surface(t, B.vm, 2, 0, &shared, &bb, &pb);
	dst.addr = shared;
	if (!ret)
		ret = sgxfive_xfer_fill(A.x, &dst, &r, 0xff0000aa, 0);
	if (!ret)
		ret = sgxfive_xfer_wait(A.x, WAIT_NS);
	check(&failed, !ret && filled(pa, 2048, 0xff0000aa) && untouched(pb, 2048),
	      "same-address-separate-vms");

	/* 3. An address mapped only in B: A's fill faults and writes nothing. */
	if (!ret)
		ret = sgxfive_vm_alloc(B.vm, DRM_SGXFIVE_HEAP_GENERAL, 0x100000, 0x100000,
				       &only_b);
	if (!ret)
		ret = surface(t, B.vm, 2, 0, &only_b, &bo, &po);
	dst.addr = only_b;
	if (!ret)
		ret = sgxfive_xfer_fill(A.x, &dst, &r, 0xff0000bb, 0);
	t0 = now_ns();
	/* The job is recovered and fails: its fence carries the fault. */
	check(&failed, !ret && sgxfive_xfer_wait(A.x, WAIT_NS) == -EIO && untouched(po, 2048),
	      "other-vm-address-faults");
	t0 = now_ns() - t0;
	printf("fault recovered after %lld ms\n", t0 / 1000000);
	check(&failed, !ret && t0 < FAULT_NS, "fault-recovered-quickly");

	/* 4. The faulting context is lost. */
	check(&failed, sgxfive_submit_transfer(t->dev, A.ctx,
		DRM_SGXFIVE_SUBMIT_JOB_TRANSFER_DUMMY, NULL, 0, 0) == -ECANCELED,
	      "lost-context-cancelled");

	/* 5. Context B is unaffected. */
	ret = sgxfive_xfer_fill(B.x, &dst, &r, 0xff0000cc, 0);
	if (!ret)
		ret = sgxfive_xfer_wait(B.x, WAIT_NS);
	check(&failed, !ret && filled(po, 2048, 0xff0000cc), "other-context-survives");

	/*
	 * 6. A job queued right behind a faulting one, on another context, still
	 * runs: the recovery reset re-runs it.
	 */
	ret = side_init(t, &C);
	if (!ret)
		ret = side_init(t, &D);
	if (!ret)
		ret = surface(t, D.vm, 2, 0, &only_d, &bq, &pq);
	if (!ret)
		ret = surface(t, D.vm, 2, 0, &mine, &bm, &pm);
	if (!ret) {
		dst.addr = only_d;
		ret = sgxfive_xfer_fill(C.x, &dst, &r, 0xff0000ee, 0);
	}
	if (!ret) {
		dst.addr = mine;
		ret = sgxfive_xfer_fill(D.x, &dst, &r, 0xff0000ff, 0);
	}
	if (!ret)
		ret = sgxfive_xfer_wait(D.x, WAIT_NS);	/* re-run: no error */
	check(&failed, !ret && filled(pm, 2048, 0xff0000ff) && untouched(pq, 2048) &&
		       sgxfive_xfer_wait(C.x, WAIT_NS) == -EIO &&
		       sgxfive_submit_transfer(t->dev, C.ctx,
			       DRM_SGXFIVE_SUBMIT_JOB_TRANSFER_DUMMY, NULL, 0, 0) == -ECANCELED,
	      "queued-innocent-job-reruns");

	/* 7. A read-only mapping cannot be written by the GPU. */
	ret = surface(t, B.vm, 2, DRM_SGXFIVE_VM_MAP_READ_ONLY, &ro, &bro, &pro);
	dst.addr = ro;
	if (!ret)
		ret = sgxfive_xfer_fill(B.x, &dst, &r, 0xff0000dd, 0);
	check(&failed, !ret && sgxfive_xfer_wait(B.x, WAIT_NS) == -EIO && untouched(pro, 2048) &&
		       sgxfive_xfer_fill(B.x, &dst, &r, 0xff0000dd, 0) == -ECANCELED,
	      "read-only-faults");

	/*
	 * 8. That was the file's third fault within a minute: it may neither
	 * create contexts nor submit, even to a context that never faulted.
	 */
	ret = sgxfive_vm_create(t->dev, &banned_vm);
	check(&failed, !ret && sgxfive_ctx_create(banned_vm, &banned_ctx) == -ECANCELED &&
		       sgxfive_submit_transfer(t->dev, D.ctx,
			       DRM_SGXFIVE_SUBMIT_JOB_TRANSFER_DUMMY, NULL, 0, 0) == -ECANCELED,
	      "faulting-file-banned");
	if (banned_ctx)
		sgxfive_ctx_destroy(t->dev, banned_ctx);
	sgxfive_vm_destroy(banned_vm);

	sgxfive_bo_destroy(bk);
	sgxfive_bo_destroy(ba);
	sgxfive_bo_destroy(bb);
	sgxfive_bo_destroy(bo);
	sgxfive_bo_destroy(bro);
	sgxfive_bo_destroy(bq);
	sgxfive_bo_destroy(bm);
	side_fini(t, &A);
	side_fini(t, &B);
	side_fini(t, &C);
	side_fini(t, &D);
	return failed ? 1 : 0;
}

/* ---- regaccess: can a client's shader reach SGX registers? --------------------------- */

/*
 * The register-access probe: fill shaders that touch SGX registers with the
 * instructions the EDM uses for MMIO (doc/specs/hw_spec.md §10), run as an
 * ordinary client fill. The words are tools/usse-asm output for the source
 * beside them (tests/test_cli.py checks that).
 */
static const uint64_t probe_ldr[] = {
	0xFA44070000000000ull,	/* phas #0, #0, pixel, end, parallel */
	0xFE21000020000007ull,	/* ldr r0, #7, drc0 (CORE_ID, 0x1c) */
	0xF920000000000000ull,	/* wdf drc0 */
	0x2885100120000000ull,	/* mov.skipinv.end o0, r0 */
};

static const uint64_t probe_str[] = {
	0xFA44070000000000ull,	/* phas #0, #0, pixel, end, parallel */
	0xFCA16170001E0001ull,	/* mov.skipinv r0, #0x5AFE0001 */
	0xFE2900002001401Full,	/* str #671, r0 (USE_G0, 0xa7c) */
	0xFCA7F1810000AA55ull,	/* mov.skipinv.end o0, #0xFF00AA55 */
};

/* A page directory's physical address (BIF_DIR_LIST_BASE0, 0xc84). */
static const uint64_t probe_ldr_dirlist[] = {
	0xFA44070000000000ull,	/* phas #0, #0, pixel, end, parallel */
	0xFE21000020018021ull,	/* ldr r0, #801, drc0 */
	0xF920000000000000ull,	/* wdf drc0 */
	0x2885100120000000ull,	/* mov.skipinv.end o0, r0 */
};

/* As probe_ldr, with r0 set first: does the ldr write r0 at all? */
static const uint64_t probe_ldr_marked[] = {
	0xFA44070000000000ull,	/* phas #0, #0, pixel, end, parallel */
	0xFCA0408000111111ull,	/* mov.skipinv r0, #0x11111111 */
	0xFE21000020000007ull,	/* ldr r0, #7, drc0 (CORE_ID, 0x1c) */
	0xF920000000000000ull,	/* wdf drc0 */
	0x2885100120000000ull,	/* mov.skipinv.end o0, r0 */
};

/* A store, then a load of the same register: did the store land? */
static const uint64_t probe_str_ldr[] = {
	0xFA44070000000000ull,	/* phas #0, #0, pixel, end, parallel */
	0xFCA16170001E0002ull,	/* mov.skipinv r0, #0x5AFE0002 */
	0xFE2900002001401Full,	/* str #671, r0 (USE_G0, 0xa7c) */
	0xFE2100002021401Full,	/* ldr r1, #671, drc0 */
	0xF920000000000000ull,	/* wdf drc0 */
	0x2885100120000080ull,	/* mov.skipinv.end o0, r1 */
};

/* A temporary the program never writes: what did earlier tasks leave? */
static const uint64_t probe_uninit[] = {
	0xFA44070000000000ull,	/* phas #0, #0, pixel, end, parallel */
	0x2885100120000000ull,	/* mov.skipinv.end o0, r0 */
};

/* A program source that is inner's, but with words for the fill shader. */
struct probe_source {
	struct sgxfive_prog_source base;
	struct sgxfive_prog_source *inner;
	const uint64_t *words;
	uint32_t n;
	bool cbase15;		/* the PDS primary kicks code base 15 instead */
	uint32_t id;		/* the program the words replace: USE_FILL or USE_COPY */
	uint32_t temps;		/* at least this many temporaries */
	uint64_t scratch;	/* 0, or where SCRATCH_IMM immediates point */
	const uint64_t *pds;	/* a PDS probe: the words replacing PDS_SEC (one per slot) */
	uint32_t pds_n;
	uint32_t pds_data;	/* its data segment, dwords */
};

/*
 * The secondary attributes a PDS probe may write with douta: sa0-sa15, which
 * the probe's USE program stores (douta writes secondary attributes).
 */
#define PROBE_PDS_ATTRS	16
#define DOUTU1_PIXEL	4	/* U1 of a pixel task: SDSOFT (fw_format.md §9.4) */

/*
 * A limm "mov d, #imm" whose immediate is SCRATCH_IMM | k (k < 0x10000) loads
 * the scratch buffer's address + k instead: probes of loads and stores address
 * a buffer the host fills and reads back.
 */
#define LIMM_MASK	0xFF30000000000000ull
#define LIMM_VAL	0xFC20000000000000ull
#define SCRATCH_IMM	0x5CAF0000u
#define SCRATCH_PAGES	16			/* 64 KiB */
#define SCRATCH_FILL(i)	(0xD0000000u | (i))	/* dword i of the scratch buffer, before */

static int probe_meta(struct sgxfive_prog_source *src, uint32_t id, struct sgxfive_prog_meta *m)
{
	struct probe_source *p = (struct probe_source *)src;
	int ret = p->inner->ops->meta(p->inner, id, m);

	if (!ret && p->pds && id == SGXFIVE_PROG_PDS_SEC) {
		m->size = p->pds_n * 4;
		m->data_size = p->pds_data * 4;
		m->attrs = PROBE_PDS_ATTRS;
		return 0;
	}
	if (!ret && id == p->id) {
		m->size = p->n * 8;
		if (m->temps < 4)
			m->temps = 4;		/* r0 */
		if (m->temps < p->temps)
			m->temps = p->temps;
	}
	return ret;
}

static int probe_build(struct sgxfive_prog_source *src, uint32_t id,
		       const struct sgxfive_prog_env *env, void *out)
{
	struct probe_source *p = (struct probe_source *)src;
	int ret;

	if (p->pds && id == SGXFIVE_PROG_PDS_SEC) {
		uint32_t *w = out;

		/* the probe's words, with its U0-U2 (data dwords 0-2) kicking the secondary task */
		for (uint32_t i = 0; i < p->pds_n; i++)
			w[i] = (uint32_t)p->pds[i];
		w[0] = env->doutu[SGXFIVE_PROG_USE_SEC];
		w[1] = DOUTU1_PIXEL;
		w[2] = 0;
		return 0;
	}
	if (id == p->id) {
		uint64_t *w = out;

		memcpy(out, p->words, p->n * 8);
		for (uint32_t i = 0; p->scratch && i < p->n; i++) {
			uint32_t imm = sgxfive_limm_get(w[i]);

			if ((w[i] & LIMM_MASK) == LIMM_VAL && (imm & ~0xffffu) == SCRATCH_IMM)
				w[i] = sgxfive_limm_set(w[i],
							(uint32_t)p->scratch + (imm & 0xffff));
		}
		return 0;
	}
	ret = p->inner->ops->build(p->inner, id, env, out);
	if (!ret && id == SGXFIVE_PROG_PDS_PRIM && p->cbase15) {
		uint32_t u0;

		/* Its DOUTU word U0 (the KICKONLY data, byte 0): EXE 0, CBASE 15. */
		memcpy(&u0, out, 4);
		u0 = (u0 & 0xff000000u) | 0xf;
		memcpy(out, &u0, 4);
	}
	return ret;
}

static void probe_destroy(struct sgxfive_prog_source *src)
{
}

static const struct sgxfive_prog_source_ops probe_ops = {
	.meta = probe_meta, .build = probe_build, .destroy = probe_destroy,
};

/* Fill 64x32 with the probe as the fill shader; report what reached memory. */
static int run_probe(struct tool *t, const char *name, const uint64_t *words, uint32_t n,
		     bool cbase15)
{
	struct probe_source src = {
		{ &probe_ops, name }, t->progs, words, n, cbase15, SGXFIVE_PROG_USE_FILL, 0, 0,
		NULL, 0, 0,
	};
	struct sgxfive_prog_source *saved = t->progs;
	const struct sgxfive_rect r = { 0, 0, 64, 32 };
	struct sgxfive_surface dst = { 0, 64, 32, 256 };
	struct sgxfive_bo *bo = NULL;
	uint32_t *p = NULL, same = 0;
	uint64_t addr = 0;
	struct side s;
	char why[96];
	int ret, job = 0;

	t->progs = &src.base;
	ret = side_init(t, &s);
	t->progs = saved;
	if (!ret)
		ret = surface(t, s.vm, 2, 0, &addr, &bo, &p);
	dst.addr = addr;
	if (!ret)
		ret = sgxfive_xfer_fill(s.x, &dst, &r, 0, 0);
	if (!ret)
		job = sgxfive_xfer_wait(s.x, WAIT_NS);
	if (p)
		for (uint32_t i = 0; i < 2048; i++)
			same += p[i] == p[0];
	if (ret) {
		printf("%s: failed: %s\n", name, strerror(-ret));
	} else if (job) {
		printf("%s: job failed: %s\n", name, job_error(job, why, sizeof(why)));
	} else {
		uint32_t val[8], cnt[8], nv = 0, other = 0;

		printf("%s: job completed, dword 0 = 0x%08x, %u of 2048 equal\n", name, p[0], same);
		for (uint32_t i = 0; i < 2048; i++) {
			uint32_t k = 0;

			while (k < nv && val[k] != p[i])
				k++;
			if (k < nv)
				cnt[k]++;
			else if (nv < 8)
				val[nv] = p[i], cnt[nv++] = 1;
			else
				other++;
		}
		for (uint32_t k = 0; k < nv; k++)
			printf("  0x%08x x%u\n", val[k], cnt[k]);
		if (other)
			printf("  (%u dwords with other values)\n", other);
		for (uint32_t y = 0; y < 4; y++)
			printf("  row %u: %08x %08x %08x %08x ... %08x\n", y, p[y * 64], p[y * 64 + 1],
			       p[y * 64 + 2], p[y * 64 + 3], p[y * 64 + 63]);
	}
	sgxfive_bo_destroy(bo);
	side_fini(t, &s);
	return 0;
}

static int cmd_regaccess(struct tool *t)
{
	run_probe(t, "uninit-temps", probe_uninit, 2, false);
	run_probe(t, "ldr-core-id", probe_ldr, 4, false);
	run_probe(t, "ldr-marked", probe_ldr_marked, 5, false);
	run_probe(t, "ldr-dir-list-base0", probe_ldr_dirlist, 4, false);
	run_probe(t, "str-use-g0", probe_str, 4, false);
	run_probe(t, "str-then-ldr-use-g0", probe_str_ldr, 6, false);
	run_probe(t, "kick-code-base-15", probe_ldr, 4, true);
	return 0;
}

/* ---- probe: our own programs as the fill shader --------------------------------------- */

#define PROBE_MAX_WORDS	256

struct probe_file {
	const char *name;	/* the file's base name without .bin */
	char label[64];
	uint64_t words[PROBE_MAX_WORDS];
	uint32_t n;
};

/*
 * Read a raw little-endian program (tools/usse-asm -o) into f: USSE words (width 8) or
 * PDS words (width 4, one per slot of f->words).
 */
static int probe_read(const char *path, struct probe_file *f, unsigned int width)
{
	const char *base = strrchr(path, '/');
	uint8_t buf[PROBE_MAX_WORDS * 8 + 1];
	size_t len, dot;
	FILE *fp = fopen(path, "rb");

	if (!fp) {
		fprintf(stderr, "sgxfive-test: %s: %s\n", path, strerror(errno));
		return -1;
	}
	len = fread(buf, 1, sizeof(buf), fp);
	fclose(fp);
	if (!len || len % width || len > PROBE_MAX_WORDS * width) {
		fprintf(stderr, "sgxfive-test: %s: not 1 to %u %s words\n", path,
			PROBE_MAX_WORDS, width == 8 ? "USSE" : "PDS");
		return -1;
	}
	f->n = (uint32_t)(len / width);
	for (uint32_t i = 0; i < f->n; i++) {
		f->words[i] = 0;
		for (unsigned int b = 0; b < width; b++)
			f->words[i] |= (uint64_t)buf[i * width + b] << (8 * b);
	}
	base = base ? base + 1 : path;
	dot = strcspn(base, ".");
	snprintf(f->label, sizeof(f->label), "%.*s", (int)dot, base);
	f->name = f->label;
	return 0;
}

static bool pixels_all(const uint32_t *p, uint32_t n, uint32_t v)
{
	for (uint32_t i = 0; i < n; i++)
		if (p[i] != v)
			return false;
	return true;
}

struct probe_opts {
	uint32_t temps;		/* at least this many temporaries */
	bool coords;		/* the copy shader of a copy of the coordinates */
	bool pixels;		/* print every pixel */
	uint32_t pds_data;	/* 0, or the files are PDS programs with this many data dwords */
	struct probe_file use;	/* with pds_data: the fill's shader (stores sa0-sa15) */
	struct sgxfive_poke pokes[SGXFIVE_POKE_MAX];	/* --poke: words of the fill's command */
	const char *poke_args[SGXFIVE_POKE_MAX];
	unsigned int npokes;
	uint64_t low;		/* --low ADDR: the scratch also there (0: not) */
	bool late;		/* --late R:K=V: the host writes V to scratch dword K */
	uint32_t late_ready, late_dword, late_value;	/* once dword R leaves its fill */
	struct probe_tri {	/* --tri */
		int slot;	/* the slot the files replace, or -1: a fill probe */
		uint32_t data;	/* a PDS slot's data dwords */
		struct probe_file fixed[SGXFIVE_TRI_SLOT_COUNT];	/* --slot (n 0: none) */
		uint32_t fixed_data[SGXFIVE_TRI_SLOT_COUNT];
		uint32_t width, height, max_width, max_height;	/* 0: the default */
		uint32_t vertices;	/* --vertices: 0, or the triangle and copies of it */
		uint32_t coords;	/* --vtx-coords: more output dwords per vertex */
		bool copy_depth;	/* --copy-depth: the copies at z = c / 16 */
		bool isp2_set;		/* --isp2 V: ISP word 2 in the state block */
		uint32_t isp2;
		uint32_t blk_mask;	/* --blk N=V: state block words set */
		uint32_t blk_val[SGXFIVE_TRI_BLOCK_WORDS];
		uint32_t add_mask;	/* --blk-add BIT=V[,V]: presence bits added */
		uint32_t add_val[16][2];
		uint32_t cmd_mask;	/* --cmd N=V: render command words set */
		uint32_t cmd_val[SGXFIVE_TRI_PROBE_CMD_WORDS];
		uint32_t vdm_mask;	/* --vdm N=V: VDM stream words set */
		uint32_t vdm_val[SGXFIVE_TRI_VDM_WORDS];
		uint32_t vdm_xor_mask;	/* --vdm N^=V: VDM stream words flipped */
		uint32_t vdm_xor_val[SGXFIVE_TRI_VDM_WORDS];
		bool sideband_set;	/* --sideband V: the end-of-tile emitpix2's */
		uint32_t sideband;
		uint32_t obj2;		/* --obj2 FIRST: 0, or the second object's first vertex */
		uint32_t obj2_blk_mask;	/* --obj2-blk N=V: its state block words set */
		uint32_t obj2_blk_val[SGXFIVE_TRI_PROBE_BLK2_WORDS];
		struct probe_file obj2_pixel;	/* --obj2-pixel FILE (n 0: the default fill) */
		const char *dump_dir;	/* --dump-render DIR: the render's memory there */
		const char *kpoke[KPR_MAX];	/* --kpoke SPEC: written before each render */
		unsigned int nkpoke;
	} tri;
};

/* The texel (x, y) of a --coords probe's source. */
static uint32_t coord_texel(uint32_t x, uint32_t y)
{
	return y << 16 | x;
}

/* The scratch dwords changed, at most max_shown of them: how many changed. */
static uint32_t probe_scratch(const char *name, const uint32_t *sp, uint32_t max_shown)
{
	uint32_t shown = 0;

	for (uint32_t i = 0; i < SCRATCH_PAGES * SGXFIVE_PAGE_SIZE / 4; i++) {
		if (sp[i] == SCRATCH_FILL(i))
			continue;
		if (shown++ < max_shown)
			printf("probe %s: scratch +0x%03x 0x%08x\n", name, i * 4, sp[i]);
	}
	if (shown > max_shown)
		printf("probe %s: scratch %u more changed\n", name, shown - max_shown);
	return shown;
}

/*
 * A probe's readback: the target's width x height pixels as o0 (the value, or the four
 * most frequent when they differ; every pixel, row by row, with pixels) and the scratch
 * dwords changed, at most max_shown of them.
 */
static void probe_report(const char *name, const uint32_t *p, uint32_t width,
			 uint32_t height, bool pixels, const uint32_t *sp, uint32_t max_shown)
{
	const uint32_t total = width * height;
	uint32_t val[64], cnt[64], nv = 0, other = 0;

	for (uint32_t i = 0; i < total; i++) {
		uint32_t k = 0;

		while (k < nv && val[k] != p[i])
			k++;
		if (k < nv)
			cnt[k]++;
		else if (nv < 64)
			val[nv] = p[i], cnt[nv++] = 1;
		else
			other++;
	}
	/* the most frequent first */
	for (uint32_t a = 1; a < nv; a++)
		for (uint32_t b = a; b > 0 && cnt[b] > cnt[b - 1]; b--) {
			uint32_t tv = val[b], tc = cnt[b];

			val[b] = val[b - 1], cnt[b] = cnt[b - 1];
			val[b - 1] = tv, cnt[b - 1] = tc;
		}
	if (nv == 1) {
		printf("probe %s: o0 0x%08x (%u of %u)\n", name, val[0], total, total);
	} else {
		printf("probe %s: o0 mixed", name);
		for (uint32_t k = 0; k < nv; k++) {
			if (k < 4)
				printf(" 0x%08x x%u", val[k], cnt[k]);
			else
				other += cnt[k];
		}
		if (other)
			printf(" other x%u", other);
		printf("\n");
	}
	for (uint32_t y = 0; pixels && y < height; y++) {
		printf("probe %s: row %u:", name, y);
		for (uint32_t x = 0; x < width; x++)
			printf(" %08x", p[y * width + x]);
		printf("\n");
	}
	probe_scratch(name, sp, max_shown);
}

/*
 * A failed probe's readback: the scratch dwords changed, at most max_shown of them, or
 * that none was. What ran before a render hung or faulted may have stored there.
 */
static void probe_report_failed(const char *name, const uint32_t *sp, uint32_t max_shown)
{
	if (!probe_scratch(name, sp, max_shown))
		printf("probe %s: scratch unchanged\n", name);
}

/*
 * One probe: a 64x32 fill whose shader is the file's program, with temps
 * temporaries and a 64 KiB scratch buffer (dword i = SCRATCH_FILL(i)) its
 * SCRATCH_IMM immediates point at; with coords, a 64x32 copy whose shader
 * is the program and whose source texel (x, y) is coord_texel(x, y). Prints
 * o0 as the surface holds it (the four most frequent values when the pixels
 * differ; every pixel, row by row, with pixels) and every scratch dword the
 * program changed; a failed job is reported, with the scratch, and recovered from.
 */
/*
 * --late: while the job runs, wait for scratch dword late_ready to leave its fill (a
 * shader's "ready"), at most LATE_NS, then write late_value to dword late_dword. The
 * scratch is write-combined on the CPU: the reads go to memory, the fence drains the write.
 */
static void probe_late(const char *name, uint32_t *sp, const struct probe_opts *po)
{
	volatile uint32_t *v = sp;
	const long long t0 = now_ns();
	long long t = t0;
	bool ready;

	while (!(ready = v[po->late_ready] != SCRATCH_FILL(po->late_ready)) && t - t0 < LATE_NS)
		t = now_ns();
	v[po->late_dword] = po->late_value;
	__atomic_thread_fence(__ATOMIC_SEQ_CST);
	printf("probe %s: late: ready (scratch +0x%03x) %s %lld us; scratch +0x%03x = 0x%08x "
	       "written\n", name, po->late_ready * 4, ready ? "seen after" : "not seen in",
	       (t - t0) / 1000, po->late_dword * 4, po->late_value);
}

static void probe_one(struct tool *t, const struct probe_file *f, const struct probe_opts *po)
{
	struct probe_source src = {
		{ &probe_ops, f->name }, t->progs, f->words, f->n, false,
		po->coords ? SGXFIVE_PROG_USE_COPY : SGXFIVE_PROG_USE_FILL, po->temps, 0,
		NULL, 0, 0,
	};

	if (po->pds_data) {
		/* the file is the fill's PDS secondary; the fill's shader is the given one */
		src.words = po->use.words;
		src.n = po->use.n;
		src.pds = f->words;
		src.pds_n = f->n;
		src.pds_data = po->pds_data;
	}
	struct sgxfive_prog_source *saved = t->progs;
	const struct sgxfive_rect r = { 0, 0, 64, 32 };
	struct sgxfive_surface dst = { 0, 64, 32, 256 };
	struct sgxfive_bo *bo = NULL, *sbo = NULL, *cbo = NULL;
	uint32_t *p = NULL, *sp = NULL, *cp = NULL;
	uint64_t addr = 0, saddr = 0, caddr = 0;
	struct side s;
	char why[96];
	int ret;

	t->progs = &src.base;
	ret = side_init(t, &s);
	t->progs = saved;
	if (!ret)
		ret = surface(t, s.vm, 2, 0, &addr, &bo, &p);
	if (!ret)
		ret = surface(t, s.vm, SCRATCH_PAGES, 0, &saddr, &sbo, &sp);
	if (!ret && po->low &&
	    (ret = sgxfive_vm_map(s.vm, po->low, sbo, 0, SCRATCH_PAGES * SGXFIVE_PAGE_SIZE, 0))) {
		printf("probe %s: failed: scratch at 0x%08llx: %s\n", f->name,
		       (unsigned long long)po->low, strerror(-ret));
		goto out;
	}
	if (!ret && po->coords)
		ret = surface(t, s.vm, 3, DRM_SGXFIVE_VM_MAP_READ_ONLY, &caddr, &cbo, &cp);
	for (uint32_t i = 0; !ret && po->coords && i < 2048; i++)
		cp[i] = coord_texel(i % 64, i / 64);
	if (!ret) {
		for (uint32_t i = 0; i < SCRATCH_PAGES * SGXFIVE_PAGE_SIZE / 4; i++)
			sp[i] = SCRATCH_FILL(i);
		src.scratch = saddr;
		printf("probe %s: scratch at 0x%08llx (%u KiB)\n", f->name,
		       (unsigned long long)saddr, SCRATCH_PAGES * SGXFIVE_PAGE_SIZE / 1024);
		if (po->low)
			printf("probe %s: scratch also at 0x%08llx\n", f->name,
			       (unsigned long long)po->low);
		dst.addr = addr;
		if (po->npokes) {
			printf("probe %s: pokes", f->name);
			for (unsigned int k = 0; k < po->npokes; k++)
				printf(" %s", po->poke_args[k]);
			printf("\n");
			sgxfive_xfer_set_hook(s.x, sgxfive_poke_hook,
					      &(struct sgxfive_poke_set){ po->pokes, po->npokes });
		}
		if (po->coords) {
			const struct sgxfive_surface csrc = { caddr, 64, 32, 256 };

			ret = sgxfive_xfer_copy(s.x, &csrc, 0, 0, &dst, &r, 0);
		} else {
			ret = sgxfive_xfer_fill(s.x, &dst, &r, 0, 0);
		}
	}
	if (!ret && po->late)
		probe_late(f->name, sp, po);
	if (ret) {
		printf("probe %s: failed: %s\n", f->name, strerror(-ret));
	} else if ((ret = sgxfive_xfer_wait(s.x, WAIT_NS))) {
		/* faulted or hung: recovered, the job failed and the context is lost */
		printf("probe %s: failed: %s\n", f->name, job_error(ret, why, sizeof(why)));
		probe_report_failed(f->name, sp, 32);
	} else if (pixels_all(p, 2048, SENTINEL)) {
		/* the job completed without writing a pixel */
		printf("probe %s: failed: no pixel written\n", f->name);
	} else {
		probe_report(f->name, p, 64, 32, po->pixels, sp, 32);
	}
out:
	sgxfive_bo_destroy(cbo);
	sgxfive_bo_destroy(sbo);
	sgxfive_bo_destroy(bo);
	side_fini(t, &s);
}

/* ---- probe --tri: our own programs in the first triangle's render --------------------- */

/* "SLOT" or "SLOT:N" (N data dwords, a PDS slot's): 0, or -1 if not well formed. */
static int probe_tri_slot(const char *arg, int *slot, uint32_t *data)
{
	char name[16], *end;
	const char *colon = strchr(arg, ':');
	size_t len = colon ? (size_t)(colon - arg) : strlen(arg);
	unsigned long v = 0;

	if (len >= sizeof(name))
		return -1;
	memcpy(name, arg, len);
	name[len] = 0;
	*slot = sgxfive_tri_slot_find(name);
	if (*slot < 0)
		return -1;
	if (colon) {
		v = strtoul(colon + 1, &end, 0);
		if (*end || !colon[1])
			return -1;
	}
	*data = (uint32_t)v;
	if (!sgxfive_tri_slot_is_pds(*slot))
		return colon ? -1 : 0;
	/* whole rows of four dwords, at most two banks of 64 */
	return !colon || v < 4 || v % 4 || v > 128 ? -1 : 0;
}

/* --slot SLOT=FILE[:N]: 0, 2 (usage) or 1 (the file). */
static int probe_tri_fixed(const char *arg, struct probe_tri *pt)
{
	const char *eq = strchr(arg, '=');
	char spec[32], path[4096];
	const char *colon;
	int slot;
	uint32_t data;

	if (!eq || (size_t)(eq - arg) >= 16 || strlen(eq + 1) >= sizeof(path))
		return usage();
	/* SLOT, then an optional :N at the end of FILE */
	snprintf(path, sizeof(path), "%s", eq + 1);
	colon = strrchr(path, ':');
	if (colon && colon[1] && strspn(colon + 1, "0123456789xabcdefABCDEF") == strlen(colon + 1))
		path[colon - path] = 0;
	else
		colon = NULL;
	snprintf(spec, sizeof(spec), "%.*s%s%s", (int)(eq - arg), arg, colon ? ":" : "",
		 colon ? colon + 1 : "");
	if (probe_tri_slot(spec, &slot, &data) || pt->fixed[slot].n)
		return usage();
	if (probe_read(path, &pt->fixed[slot], sgxfive_tri_slot_is_pds(slot) ? 4 : 8))
		return 1;
	if (data && pt->fixed[slot].n <= data) {
		fprintf(stderr, "sgxfive-test: %s: no code after %u data dwords\n", path, data);
		return 1;
	}
	pt->fixed_data[slot] = data;
	return 0;
}

/* --width/--height/--max-width/--max-height V: true if opt is one (V parsed or not). */
static bool probe_tri_size(const char *opt, const char *val, struct probe_tri *pt)
{
	uint32_t *v = !strcmp(opt, "--width") ? &pt->width : !strcmp(opt, "--height") ?
		      &pt->height : !strcmp(opt, "--max-width") ? &pt->max_width :
		      !strcmp(opt, "--max-height") ? &pt->max_height : NULL;

	char *end;
	unsigned long long x;

	if (!v || !val)
		return false;
	/* a bad value becomes one probe_tri_check refuses */
	x = strtoull(val, &end, 0);
	*v = *end || !*val || !x || x > SGXFIVE_TRI_MAX_W ? UINT32_MAX : (uint32_t)x;
	return true;
}

/* The --tri options as a whole, with their defaults filled in: 0, or -1 (usage). */
static int probe_tri_check(struct probe_opts *po)
{
	struct probe_tri *pt = &po->tri;
	bool fixed = false;

	for (unsigned int k = 0; k < SGXFIVE_TRI_SLOT_COUNT; k++)
		fixed |= pt->fixed[k].n != 0;
	if (pt->slot < 0)
		return fixed || pt->width || pt->height || pt->max_width || pt->max_height ||
		       pt->vertices || pt->coords || pt->copy_depth || pt->isp2_set || pt->blk_mask ||
		       pt->add_mask ||
		       pt->cmd_mask || pt->vdm_mask || pt->vdm_xor_mask || pt->sideband_set || pt->dump_dir ||
		       pt->nkpoke || pt->obj2 || pt->obj2_blk_mask || pt->obj2_pixel.n ? -1 : 0;
	if (pt->copy_depth && !pt->vertices)
		return -1;
	/* the second object: whole triangles among the copies, and its words only with it */
	if (pt->obj2 && (pt->obj2 % 3 || pt->obj2 >= pt->vertices))
		return -1;
	if (!pt->obj2 && (pt->obj2_blk_mask || pt->obj2_pixel.n))
		return -1;
	if (pt->sideband_set && pt->slot != SGXFIVE_TRI_SLOT_EOT && !pt->fixed[SGXFIVE_TRI_SLOT_EOT].n)
		return -1;
	if (po->coords || po->pds_data || po->use.n || pt->fixed[pt->slot].n)
		return -1;
	pt->width = pt->width ? pt->width : 64;
	pt->height = pt->height ? pt->height : 64;
	pt->max_width = pt->max_width ? pt->max_width : pt->width;
	pt->max_height = pt->max_height ? pt->max_height : pt->height;
	if (pt->width % 2 || pt->height % 2 || pt->max_width > SGXFIVE_TRI_MAX_W ||
	    pt->max_height > SGXFIVE_TRI_MAX_H || pt->width > pt->max_width ||
	    pt->height > pt->max_height)
		return -1;
	return 0;
}

static int kpoke_write(const char *spec);	/* below, with the tri command's */

/*
 * --dump-render: the kernel's debugfs render_param and render_tadata (the newest render
 * context's parameter slot from its PB on, and its TA data; SGXFIVE_DEBUGFS overrides
 * their directory, for the tests) copied to DIR/NAME.param.bin and DIR/NAME.tadata.bin,
 * while the probe's render context lives; after a failed job (failed) recovery has reset
 * the TA data but kept the PB pages. Returns 0 or -errno.
 */
static int dump_render(const char *dir, const char *name, bool failed)
{
	static const char *const what[2] = { "param", "tadata" };
	const char *dbg = getenv("SGXFIVE_DEBUGFS");
	long long size[2] = { 0, 0 };
	static char buf[65536];
	char path[4096];
	int ret = 0;

	for (unsigned int i = 0; i < 2 && !ret; i++) {
		int in, out;
		ssize_t n;

		snprintf(path, sizeof(path), "%s/render_%s",
			 dbg ? dbg : "/sys/kernel/debug/dri/0/sgx", what[i]);
		in = open(path, O_RDONLY);
		if (in < 0)
			return -errno;
		snprintf(path, sizeof(path), "%s/%s.%s.bin", dir, name, what[i]);
		out = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
		if (out < 0) {
			ret = -errno;
			close(in);
			break;
		}
		while ((n = read(in, buf, sizeof(buf))) > 0) {
			if (write(out, buf, (size_t)n) != n) {
				ret = errno ? -errno : -EIO;
				break;
			}
			size[i] += n;
		}
		if (n < 0)
			ret = -errno;
		close(out);
		close(in);
	}
	if (!ret)
		printf("probe %s: render memory to %s/%s.{param,tadata}.bin (%lld, %lld bytes)%s\n",
		       name, dir, name, size[0], size[1], failed ? " after the failure" : "");
	return ret;
}

/*
 * One --tri probe: the first triangle's W x H render (sgxfive_tri_probe.h) with the
 * file's program in its slot and the --slot programs in theirs, every USE replacement
 * with temps temporaries, a 64 KiB scratch buffer (dword i = SCRATCH_FILL(i)) the
 * scratch immediates point at, on a render context of its own. Prints the slots
 * replaced, then as a fill probe the target's pixels as o0 and every scratch dword
 * changed (several tiles may each store their own); a failed render is reported, with the
 * scratch, and recovered from.
 */
static void probe_tri_one(struct tool *t, const struct probe_file *f,
			  const struct probe_opts *po)
{
	const struct probe_tri *pt = &po->tri;
	struct sgxfive_tri_probe pr = { 0 };
	struct sgxfive_tri_params p;
	struct sgxfive_tri_rig *g = NULL;
	struct sgxfive_vm *vm = NULL;
	struct sgxfive_bo *sbo = NULL;
	uint32_t *sp = NULL, ctx = 0;
	uint64_t saddr = 0;
	bool submitted = false;
	char why[96];
	int ret;

	for (unsigned int k = 0; k < SGXFIVE_TRI_SLOT_COUNT; k++)
		if (pt->fixed[k].n)
			pr.slot[k] = (struct sgxfive_tri_prog){ pt->fixed[k].words, pt->fixed[k].n,
								pt->fixed_data[k], po->temps };
	pr.slot[pt->slot] = (struct sgxfive_tri_prog){ f->words, f->n, pt->data, po->temps };
	pr.vertices = pt->vertices;
	pr.coords = pt->coords;
	pr.copy_depth = pt->copy_depth;
	pr.isp2_set = pt->isp2_set;
	pr.isp2 = pt->isp2;
	pr.blk_mask = pt->blk_mask;
	memcpy(pr.blk_val, pt->blk_val, sizeof(pr.blk_val));
	pr.add_mask = pt->add_mask;
	memcpy(pr.add_val, pt->add_val, sizeof(pr.add_val));
	pr.cmd_mask = pt->cmd_mask;
	memcpy(pr.cmd_val, pt->cmd_val, sizeof(pr.cmd_val));
	pr.vdm_mask = pt->vdm_mask;
	memcpy(pr.vdm_val, pt->vdm_val, sizeof(pr.vdm_val));
	pr.vdm_xor_mask = pt->vdm_xor_mask;
	memcpy(pr.vdm_xor_val, pt->vdm_xor_val, sizeof(pr.vdm_xor_val));
	pr.sideband_set = pt->sideband_set;
	pr.sideband = pt->sideband;
	pr.obj2_first = pt->obj2;
	pr.obj2_blk_mask = pt->obj2_blk_mask;
	memcpy(pr.obj2_blk_val, pt->obj2_blk_val, sizeof(pr.obj2_blk_val));
	if (pt->obj2_pixel.n)
		pr.obj2_pixel = (struct sgxfive_tri_prog){ pt->obj2_pixel.words, pt->obj2_pixel.n,
							   0, po->temps };
	ret = sgxfive_vm_create(t->dev, &vm);
	if (!ret)
		ret = sgxfive_render_ctx_create(vm, pt->max_width, pt->max_height, &ctx);
	if (!ret)
		ret = sgxfive_tri_rig_create(vm, ctx, pt->max_width, pt->max_height, &g);
	if (!ret)
		ret = surface(t, vm, SCRATCH_PAGES, 0, &saddr, &sbo, &sp);
	if (!ret) {
		for (uint32_t i = 0; i < SCRATCH_PAGES * SGXFIVE_PAGE_SIZE / 4; i++)
			sp[i] = SCRATCH_FILL(i);
		pr.scratch = (uint32_t)saddr;
		printf("probe %s: scratch at 0x%08llx (%u KiB)\n", f->name,
		       (unsigned long long)saddr, SCRATCH_PAGES * SGXFIVE_PAGE_SIZE / 1024);
		printf("probe %s: tri %ux%u", f->name, pt->width, pt->height);
		if (pt->vertices)
			printf(" (%u vertices%s)", pt->vertices,
			       pt->copy_depth ? ", at depths" : "");
		if (pt->coords)
			printf(" (%u coordinates)", pt->coords);
		if (pt->isp2_set)
			printf(" (isp2 0x%08x)", pt->isp2);
		if (pt->add_mask)
			printf(" (blk-add 0x%02x)", pt->add_mask);
		if (pt->blk_mask) {
			printf(" (block words");
			for (unsigned int k = 0; k < SGXFIVE_TRI_BLOCK_WORDS; k++)
				if (pt->blk_mask >> k & 1)
					printf(" %u", k);
			printf(")");
		}
		if (pt->cmd_mask) {
			printf(" (command words");
			for (unsigned int k = 0; k < SGXFIVE_TRI_PROBE_CMD_WORDS; k++)
				if (pt->cmd_mask >> k & 1)
					printf(" %u", k);
			printf(")");
		}
		if (pt->vdm_mask || pt->vdm_xor_mask) {
			printf(" (VDM words");
			for (unsigned int k = 0; k < SGXFIVE_TRI_VDM_WORDS; k++) {
				if (pt->vdm_mask >> k & 1)
					printf(" %u", k);
				if (pt->vdm_xor_mask >> k & 1)
					printf(" ^%u", k);
			}
			printf(")");
		}
		if (pt->sideband_set)
			printf(" (sideband 0x%08x)", pt->sideband);
		if (pt->obj2) {
			printf(" (obj2 from %u:", pt->obj2);
			if (pt->obj2_blk_mask) {
				printf(" block words");
				for (unsigned int k = 0; k < SGXFIVE_TRI_PROBE_BLK2_WORDS; k++)
					if (pt->obj2_blk_mask >> k & 1)
						printf(" %u", k);
			}
			printf("%s%s)", pt->obj2_blk_mask && pt->obj2_pixel.n ? "," : "",
			       pt->obj2_pixel.n ? " pixel" : "");
		}
		printf(",");
		for (unsigned int k = 0; k < SGXFIVE_TRI_SLOT_COUNT; k++)
			if (pr.slot[k].n)
				printf(" %s", sgxfive_tri_slot_name(k));
		printf(" replaced\n");
		if (pt->nkpoke) {
			printf("probe %s: kpoke", f->name);
			for (unsigned int k = 0; k < pt->nkpoke; k++)
				printf(" %s", pt->kpoke[k]);
			printf("\n");
		}
		/* the kernel takes them for the next render, this case's */
		for (unsigned int k = 0; k < pt->nkpoke && !ret; k++)
			ret = kpoke_write(pt->kpoke[k]);
		sgxfive_tri_default(&p, pt->width, pt->height);
		if (!ret)
			ret = sgxfive_tri_rig_build(g, &p, &pr);
		if (!ret)
			ret = sgxfive_tri_rig_submit(g);
		submitted = !ret;
	}
	if (ret) {
		printf("probe %s: failed: %s\n", f->name, strerror(-ret));
	} else if ((ret = sgxfive_tri_rig_wait(g, WAIT_NS))) {
		/* faulted, hung or overflowed: recovered, the render failed */
		printf("probe %s: failed: %s\n", f->name, job_error(ret, why, sizeof(why)));
		probe_report_failed(f->name, sp, SCRATCH_PAGES * SGXFIVE_PAGE_SIZE / 4);
	} else if (pixels_all(g->fb, pt->width * pt->height, SGXFIVE_TRI_SENTINEL)) {
		printf("probe %s: failed: no pixel written\n", f->name);
	} else {
		probe_report(f->name, g->fb, pt->width, pt->height, po->pixels, sp,
			     SCRATCH_PAGES * SGXFIVE_PAGE_SIZE / 4);
	}
	/* what the TA wrote, before the context goes: after a failure too, how far it got */
	if (submitted && pt->dump_dir) {
		int dr = dump_render(pt->dump_dir, f->name, ret != 0);

		if (dr)
			printf("probe %s: failed: --dump-render: %s\n", f->name, strerror(-dr));
	}
	sgxfive_tri_rig_destroy(g);
	sgxfive_bo_destroy(sbo);
	if (ctx)
		sgxfive_ctx_destroy(t->dev, ctx);
	sgxfive_vm_destroy(vm);
}

static int cmd_probe(struct tool *t, struct probe_file *files, uint32_t n,
		     const struct probe_opts *po)
{
	for (uint32_t i = 0; i < n; i++) {
		if (po->tri.slot >= 0)
			probe_tri_one(t, &files[i], po);
		else
			probe_one(t, &files[i], po);
	}
	return 0;
}

/* ---- main --------------------------------------------------------------------------- */

/* ---- tri ---------------------------------------------------------------------------- */

/* The image as text, one character a pixel: # triangle, . background, ? other. */
static void tri_show(const struct sgxfive_tri_params *p, const uint32_t *fb)
{
	for (uint32_t y = 0; y < p->height && y < 128; y++) {
		for (uint32_t x = 0; x < p->width && x < 128; x++) {
			uint32_t v = fb[y * p->width + x];

			putchar(v == p->colour ? '#' : v == p->bg_colour ? '.' :
				v == SGXFIVE_TRI_SENTINEL ? 's' : '?');
		}
		putchar('\n');
	}
}

/* The triangle's reference: its colour inside, the background outside, either at edges. */
static bool tri_ok(const void *ctx, uint32_t x, uint32_t y, uint32_t v, uint32_t *want)
{
	const struct sgxfive_tri_params *p = ctx;
	const int e = sgxfive_tri_expect(p, x, y);

	*want = e ? p->colour : p->bg_colour;
	return v == *want || (e < 0 && v == p->bg_colour);
}

/*
 * tri --scratch: pages in the GENERAL heap that nothing of the scene uses, for a kernel
 * poke to point a unit's base at; filled before each render, what changed reported after.
 */
struct scratch {
	struct sgxfive_bo *bo;
	uint32_t *map;
	uint64_t addr, size;
};

static int scratch_create(struct tool *t, struct sgxfive_vm *vm, uint32_t pages,
			  struct scratch *s)
{
	void *map;
	int ret;

	s->size = (uint64_t)pages * SGXFIVE_PAGE_SIZE;
	ret = sgxfive_bo_create(t->dev, s->size, DRM_SGXFIVE_BO_ALLOW_CPU_ACCESS, &s->bo);
	if (!ret)
		ret = sgxfive_bo_mmap(s->bo, &map);
	if (!ret)
		ret = sgxfive_vm_alloc(vm, DRM_SGXFIVE_HEAP_GENERAL, s->size, SGXFIVE_PAGE_SIZE,
				       &s->addr);
	if (!ret)
		ret = sgxfive_vm_map(vm, s->addr, s->bo, 0, s->size, 0);
	if (ret) {
		sgxfive_bo_destroy(s->bo);
		s->bo = NULL;
		return ret;
	}
	s->map = map;
	return 0;
}

static void scratch_fill(const struct scratch *s, uint32_t v)
{
	for (uint64_t i = 0; i < s->size / 4; i++)
		s->map[i] = v;
}

static void scratch_report(const struct scratch *s, uint32_t v)
{
	const uint32_t per_page = SGXFIVE_PAGE_SIZE / 4;
	uint32_t total = 0;

	for (uint64_t pg = 0; pg < s->size / SGXFIVE_PAGE_SIZE; pg++) {
		const uint32_t *w = s->map + pg * per_page;
		uint32_t n = 0, first = 0;

		for (uint32_t i = 0; i < per_page; i++)
			if (w[i] != v && !n++)
				first = i;
		if (n)
			printf("scratch page %llu: %u changed, first +0x%x 0x%08x\n",
			       (unsigned long long)pg, n, first * 4, w[first]);
		total += n;
	}
	printf("scratch: %u dwords changed\n", total);
}

static void scratch_destroy(struct sgxfive_vm *vm, struct scratch *s)
{
	if (!s->bo)
		return;
	sgxfive_vm_unmap(vm, s->addr, s->size);
	sgxfive_bo_destroy(s->bo);
}

/*
 * One line to the kernel's debugfs kpoke (SGXFIVE_KPOKE overrides the path, for the
 * tests): the kernel arms it for the next job of its kind. One write(2), appending and
 * never seeking: the debugfs file has no seek, which stdio's append mode does.
 */
static int kpoke_write(const char *spec)
{
	const char *path = getenv("SGXFIVE_KPOKE");
	char line[128];
	int fd, n, ret = 0;

	n = snprintf(line, sizeof(line), "%s\n", spec);
	if (n < 0 || (size_t)n >= sizeof(line))
		return -EINVAL;
	fd = open(path ? path : "/sys/kernel/debug/dri/0/sgx/kpoke", O_WRONLY | O_APPEND);
	if (fd < 0)
		return -errno;
	if (write(fd, line, (size_t)n) != n)
		ret = errno ? -errno : -EIO;
	close(fd);
	return ret;
}

/*
 * The first triangle from userspace: a render
 * context, our programs and scene in the VM, n renders with alternating
 * colours, every pixel against the CPU reference and the guard area intact.
 */
static int cmd_tri(struct tool *t, const struct opts *o)
{
	static const uint32_t colours[2][2] = {
		{ 0xff00ff00, 0xff203040 }, { 0xffff0000, 0xff000080 },
	};
	struct sgxfive_render *r = NULL;
	struct sgxfive_poke_set pokes = { o->pokes, o->npokes };
	struct sgxfive_tri_params p;
	struct sgxfive_vm *vm = NULL;
	uint32_t ctx = 0, ok = 0;
	int bad = 0;
	const uint32_t max_w = o->max_width == UINT32_MAX ? o->width : o->max_width;
	const uint32_t max_h = o->max_height == UINT32_MAX ? o->height : o->max_height;
	struct scratch sc = { 0 };
	int ret;

	ret = sgxfive_vm_create(t->dev, &vm);
	if (!ret)
		ret = sgxfive_render_ctx_create(vm, max_w, max_h, &ctx);
	if (!ret)
		ret = sgxfive_render_create(vm, ctx, &r);
	if (ret) {
		fail("render context", ret);
		goto out;
	}
	printf("tri: render context for targets up to %ux%u\n", max_w, max_h);
	if (o->scratch) {
		ret = scratch_create(t, vm, o->scratch, &sc);
		if (ret) {
			fail("scratch buffer", ret);
			goto out;
		}
		printf("scratch: 0x%08llx %u pages, fill 0x%08x\n", (unsigned long long)sc.addr,
		       o->scratch, o->scratch_fill);
	}
	if (o->fault) {
		struct sgxfive_tri_layout l;

		sgxfive_render_get_layout(r, &l);
		ret = sgxfive_vm_unmap(vm, l.gen, SGXFIVE_PAGE_SIZE);
		if (ret) {
			fail("unmap the stream", ret);
			goto out;
		}
	}
	sgxfive_render_set_hook(r, sgxfive_poke_hook, &pokes);	/* none: no change */
	for (uint32_t i = 0; i < o->n; i++) {
		struct sgxfive_tri_counts n;
		bool geometry;
		long long t0 = now_ns();
		uint32_t guard;
		int wait_err = 0;

		sgxfive_tri_default(&p, o->width, o->height);
		p.colour = colours[i % 2][0];
		p.bg_colour = colours[i % 2][1];
		for (unsigned int k = 0; k < o->nmoves; k++) {
			if (o->moves[k].n != i + 1)
				continue;
			for (int v = 0; v < 3; v++) {
				p.v[v][0] += 16 * o->moves[k].dx;
				p.v[v][1] += 16 * o->moves[k].dy;
			}
			printf("tri: render %u moved by %d,%d\n", i + 1, o->moves[k].dx,
			       o->moves[k].dy);
		}
		for (unsigned int k = 0; k < o->nkpr; k++) {
			if (o->kpr[k].n != i + 1)
				continue;
			ret = kpoke_write(o->kpr[k].spec);
			if (ret) {
				fail("kpoke", ret);
				goto out;
			}
			printf("tri: kpoke before render %u: %s\n", i + 1, o->kpr[k].spec);
		}
		if (sc.bo)
			scratch_fill(&sc, o->scratch_fill);
		geometry = o->geometry >> i & 1;
		ret = sgxfive_render_tri_flags(r, &p, 0, 0,
					       geometry ? DRM_SGXFIVE_SUBMIT_JOB_RENDER_GEOMETRY : 0);
		if (!ret)
			wait_err = sgxfive_render_wait(r, WAIT_NS);
		print_job(ret, wait_err);
		if (geometry && !ret && !wait_err) {
			printf("tri %ux%u #%u: geometry only, the scene left open\n", p.width,
			       p.height, i + 1);
			ok++;
			continue;
		}
		print_regs(t, o);
		if (sc.bo)
			scratch_report(&sc, o->scratch_fill);
		if (sgxfive_render_fb(r)) {	/* none before the first scene is built */
			struct sgxfive_tri_layout l;

			print_target(&(struct target){ p.width, p.height, p.width,
						       sgxfive_render_fb(r), tri_ok, &p },
				     sgxfive_render_guard_dirty(r, &p), o->pixels);
			sgxfive_render_get_layout(r, &l);
			printf("layout: fb 0x%08x\n", l.fb);
		}
		if (ret) {
			fail("render", ret);
			break;
		}
		ret = wait_err;
		if (ret) {
			fail_job("render", ret);
			break;
		}
		ret = sgxfive_tri_check(&p, sgxfive_render_fb(r), &n);
		guard = sgxfive_render_guard_dirty(r, &p);
		printf("tri %ux%u #%u: %u triangle, %u background, %u other; wrong %u inside, "
		       "%u outside, %u at edges; %u if flipped; guard %u\n", p.width, p.height,
		       i + 1, n.tri, n.bg, n.other, n.wrong_in, n.wrong_out, n.wrong_edge,
		       n.flipped, guard);
		printf("tri %ux%u #%u: %lld us\n", p.width, p.height, i + 1,
		       (now_ns() - t0) / 1000);
		if (ret || guard) {
			if (!o->npokes)
				tri_show(&p, sgxfive_render_fb(r));
			if (o->keep_going) {
				bad = ret ? ret : -EIO;
				ret = 0;
				continue;
			}
			ret = ret ? ret : -EIO;
			break;
		}
		ok++;
	}
	/* what the TA wrote for the last scene, before the context goes */
	if (!ret && o->dump_dir) {
		ret = dump_render(o->dump_dir, "tri", false);
		if (ret)
			fail("--dump-render", ret);
	}
	if (!ret && bad) {
		ret = bad;
		printf("tri: %u of %u renders ok\n", ok, o->n);
	} else if (!ret) {
		printf("tri: %u renders ok\n", ok);
	} else {
		printf("tri: FAILED after %u renders\n", ok);
	}
out:
	sgxfive_render_destroy(r);
	scratch_destroy(vm, &sc);
	if (ctx)
		sgxfive_ctx_destroy(t->dev, ctx);
	sgxfive_vm_destroy(vm);
	return ret ? 1 : 0;
}

/* ---- contexts ----------------------------------------------------------------------- */

/* MemFree and, on a 32-bit kernel with highmem, LowFree in KiB; -1 if absent. */
static void meminfo(long long *mem_free, long long *low_free)
{
	FILE *f = fopen("/proc/meminfo", "r");
	char line[128];

	*mem_free = *low_free = -1;
	if (!f)
		return;
	while (fgets(line, sizeof(line), f)) {
		sscanf(line, "MemFree: %lld kB", mem_free);
		sscanf(line, "LowFree: %lld kB", low_free);
	}
	fclose(f);
}

/*
 * The memory render contexts pin:
 * n render contexts for targets up to W x H in one VM, /proc/meminfo before
 * and after creating them. Other activity on the machine shows up too, so
 * compare runs, not single numbers.
 */
static int cmd_contexts(struct tool *t, const struct opts *o)
{
	uint32_t ctxs[64], n = 0;
	long long free0, low0, free1, low1;
	struct sgxfive_vm *vm = NULL;
	int ret;

	if (o->n > sizeof(ctxs) / sizeof(ctxs[0]))
		return fail("contexts", -E2BIG);
	ret = sgxfive_vm_create(t->dev, &vm);
	if (ret)
		return fail("vm", ret);
	meminfo(&free0, &low0);
	for (; n < o->n; n++) {
		ret = sgxfive_render_ctx_create(vm, o->width, o->height, &ctxs[n]);
		if (ret) {
			char what[32];

			snprintf(what, sizeof(what), "render context %u", n + 1);
			fail(what, ret);
			break;
		}
	}
	meminfo(&free1, &low1);
	if (!ret) {
		printf("contexts: %u render contexts for targets up to %ux%u: ", n, o->width,
		       o->height);
		if (free0 < 0 || free1 < 0)
			printf("no /proc/meminfo\n");
		else
			printf("MemFree -%lld KiB (%lld KiB each)%s", free0 - free1,
			       n ? (free0 - free1) / n : 0, low0 < 0 || low1 < 0 ? "\n" : ", ");
		if (free0 >= 0 && free1 >= 0 && low0 >= 0 && low1 >= 0)
			printf("LowFree -%lld KiB (%lld KiB each)\n", low0 - low1,
			       n ? (low0 - low1) / n : 0);
	}
	while (n)
		sgxfive_ctx_destroy(t->dev, ctxs[--n]);
	sgxfive_vm_destroy(vm);
	if (!ret)
		printf("contexts: destroyed\n");
	return ret ? 1 : 0;
}

static bool parse_u32(const char *s, uint32_t *v)
{
	char *end;
	unsigned long long x;

	errno = 0;
	x = strtoull(s, &end, 0);
	if (errno || !*s || *end || x > 0xffffffffull)
		return false;
	*v = (uint32_t)x;
	return true;
}

/* --regs LO-HI: dword-aligned offsets in the register bank, LO <= HI. */
static bool parse_regs(const char *s, struct opts *o)
{
	const char *dash = strchr(s, '-');
	char lo[24];

	if (!dash || dash == s || (size_t)(dash - s) >= sizeof(lo))
		return false;
	memcpy(lo, s, (size_t)(dash - s));
	lo[dash - s] = 0;
	if (!parse_u32(lo, &o->regs_lo) || !parse_u32(dash + 1, &o->regs_hi))
		return false;
	o->regs = true;
	return !(o->regs_lo % 4) && !(o->regs_hi % 4) && o->regs_lo <= o->regs_hi &&
	       o->regs_hi < REGS_SIZE;
}

static int parse_opts(int argc, char **argv, struct opts *o)
{
	static const struct { const char *name; size_t off; } names[] = {
		{ "--width", offsetof(struct opts, width) },
		{ "--height", offsetof(struct opts, height) },
		{ "--x", offsetof(struct opts, x) }, { "--y", offsetof(struct opts, y) },
		{ "--dx", offsetof(struct opts, x) }, { "--dy", offsetof(struct opts, y) },
		{ "--stride", offsetof(struct opts, stride) },
		{ "--dst-stride", offsetof(struct opts, dst_stride) },
		{ "--src-stride", offsetof(struct opts, src_stride) },
		{ "--sx", offsetof(struct opts, sx) }, { "--sy", offsetof(struct opts, sy) },
		{ "--colour", offsetof(struct opts, colour) },
		{ "-n", offsetof(struct opts, n) },
		{ "--max-width", offsetof(struct opts, max_width) },
		{ "--max-height", offsetof(struct opts, max_height) },
		{ "--scratch", offsetof(struct opts, scratch) },
		{ "--scratch-fill", offsetof(struct opts, scratch_fill) },
	};

	for (int i = 0; i < argc; i += 2) {
		bool ok = false;

		if (!strcmp(argv[i], "--keep-going")) {
			o->keep_going = true;
			i--;		/* a flag: no value */
			continue;
		}
		if (!strcmp(argv[i], "--fault") || !strcmp(argv[i], "--pixels") ||
		    !strcmp(argv[i], "--every-value")) {
			*(argv[i][2] == 'f' ? &o->fault :
			  argv[i][2] == 'p' ? &o->pixels : &o->every_value) = true;
			i--;		/* a flag: no value */
			continue;
		}
		if (!strcmp(argv[i], "--poke") && i + 1 < argc) {
			if (o->npokes == SGXFIVE_POKE_MAX ||
			    sgxfive_poke_parse(argv[i + 1], &o->pokes[o->npokes])) {
				fprintf(stderr, "sgxfive-test: bad poke %s\n", argv[i + 1]);
				return -1;
			}
			o->poke_args[o->npokes++] = argv[i + 1];
			continue;
		}
		if (!strcmp(argv[i], "--kpoke-render") && i + 1 < argc) {
			char *end;
			unsigned long n = strtoul(argv[i + 1], &end, 0);

			if (o->nkpr == KPR_MAX || end == argv[i + 1] || *end != ':' || !end[1]) {
				fprintf(stderr, "sgxfive-test: bad --kpoke-render %s (N:SPEC)\n",
					argv[i + 1]);
				return -1;
			}
			o->kpr[o->nkpr].n = (uint32_t)n;
			o->kpr[o->nkpr++].spec = end + 1;
			continue;
		}
		if (!strcmp(argv[i], "--geometry") && i + 1 < argc) {
			uint32_t n;

			if (!parse_u32(argv[i + 1], &n) || !n || n > 32) {
				fprintf(stderr, "sgxfive-test: bad --geometry %s\n", argv[i + 1]);
				return -1;
			}
			o->geometry |= 1u << (n - 1);
			continue;
		}
		if (!strcmp(argv[i], "--dump-render") && i + 1 < argc) {
			o->dump_dir = argv[++i];
			continue;
		}
		if (!strcmp(argv[i], "--move") && i + 1 < argc) {
			char *end, *e2;
			unsigned long n = strtoul(argv[i + 1], &end, 0);
			long dx, dy;

			if (o->nmoves == KPR_MAX || end == argv[i + 1] || *end != ':')
				goto bad_move;
			dx = strtol(end + 1, &e2, 0);
			if (e2 == end + 1 || *e2 != ',')
				goto bad_move;
			dy = strtol(e2 + 1, &end, 0);
			if (end == e2 + 1 || *end)
				goto bad_move;
			o->moves[o->nmoves].n = (uint32_t)n;
			o->moves[o->nmoves].dx = (int32_t)dx;
			o->moves[o->nmoves++].dy = (int32_t)dy;
			continue;
bad_move:
			fprintf(stderr, "sgxfive-test: bad --move %s (N:DX,DY)\n", argv[i + 1]);
			return -1;
		}
		if (!strcmp(argv[i], "--regs") && i + 1 < argc) {
			if (!parse_regs(argv[i + 1], o)) {
				fprintf(stderr, "sgxfive-test: bad register range %s (LO-HI, "
					"dword-aligned, below 0x%x)\n", argv[i + 1], REGS_SIZE);
				return -1;
			}
			continue;
		}
		for (size_t k = 0; k < sizeof(names) / sizeof(names[0]) && !ok; k++)
			if (!strcmp(argv[i], names[k].name) && i + 1 < argc)
				ok = parse_u32(argv[i + 1],
					       (uint32_t *)((char *)o + names[k].off));
		if (!ok) {
			fprintf(stderr, "sgxfive-test: bad option %s\n", argv[i]);
			return -1;
		}
	}
	return 0;
}

/* Every poke against the job's layout: a space it has, an index inside it. */
static int check_pokes(const struct tool *t, const char *cmd, const struct opts *o)
{
	struct sgxfive_poke_view v[SGXFIVE_POKE_VIEWS_MAX];
	const struct sgxfive_poke_view *got;
	const bool tri = !strcmp(cmd, "tri");
	const unsigned int nv = tri ? sgxfive_render_poke_layout(v) :
			       sgxfive_xfer_poke_layout(t->progs, !strcmp(cmd, "copy"), v);

	for (unsigned int i = 0; i < o->npokes; i++) {
		const struct sgxfive_poke *pk = &o->pokes[i];
		int ret = sgxfive_poke_find(v, nv, pk, &got);

		if (ret == -ENOENT) {
			fprintf(stderr, "sgxfive-test: --poke %s: a %s job has no %s%s%s\n",
				o->poke_args[i], cmd, sgxfive_poke_space_name(pk->space),
				pk->slot[0] ? ":" : "", pk->slot);
			return -1;
		}
		if (ret) {
			for (unsigned int k = 0; k < nv; k++)
				if (v[k].space == pk->space &&
				    (!v[k].slot || !strcmp(v[k].slot, pk->slot)))
					got = &v[k];
			fprintf(stderr, "sgxfive-test: --poke %s: index %u out of range (%u "
				"words)\n", o->poke_args[i], pk->index, got->count);
			return -1;
		}
	}
	return 0;
}

int main(int argc, char **argv)
{
	struct opts o = {
		.width = 64, .height = 32, .stride = 256, .colour = 0xff336699,
		.src_stride = 256, .dst_stride = 256, .n = 8,
		.max_width = UINT32_MAX, .max_height = UINT32_MAX,
		.scratch_fill = 0x3e800000,	/* 0.25f */
	};
	struct sgxfive_mock_config mcfg = { 0 };
	const char *device = NULL, *cmd;
	char *pb_end;
	bool use_mock = false, needs_programs, fake = false;
	struct tool t = { 0 };
	struct probe_file *probes = NULL;
	static struct probe_opts popts = { .temps = 32, .tri.slot = -1 };
	uint32_t nprobes = 0;
	int i = 1, ret;

	for (; i < argc && !strncmp(argv[i], "--", 2); i++) {
		if (!strcmp(argv[i], "--mock") || !strcmp(argv[i], "--mock=rev1")) {
			use_mock = true;
		} else if (!strcmp(argv[i], "--mock=harness")) {
			use_mock = true;
			mcfg.layout = SGXFIVE_MOCK_LAYOUT_HARNESS;
		} else if (!strcmp(argv[i], "--mock=none")) {
			use_mock = true;
			mcfg.no_sgxfive = true;
		} else if (!strcmp(argv[i], "--programs=asm")) {
			fake = false;
		} else if (!strcmp(argv[i], "--programs=fake")) {
			fake = true;
		} else if (!strncmp(argv[i], "--mock-pb-pages=", 16)) {
			mcfg.render_pb_pages = strtoul(argv[i] + 16, &pb_end, 0);
			if (*pb_end || pb_end == argv[i] + 16 || mcfg.render_pb_pages < 0x23 ||
			    mcfg.render_pb_pages > 0x422)
				return usage();
		} else if (!strcmp(argv[i], "--device") && i + 1 < argc) {
			device = argv[++i];
		} else {
			return usage();
		}
	}
	if (i >= argc || (mcfg.render_pb_pages && !use_mock))
		return usage();
	cmd = argv[i++];
	if (strcmp(cmd, "query") && strcmp(cmd, "dummy") && strcmp(cmd, "fill") &&
	    strcmp(cmd, "copy") && strcmp(cmd, "isolation") && strcmp(cmd, "regaccess") &&
	    strcmp(cmd, "tri") && strcmp(cmd, "contexts") && strcmp(cmd, "probe"))
		return usage();
	if (!strcmp(cmd, "probe")) {
		for (; i < argc && !strncmp(argv[i], "--", 2); i++) {
			char *end;
			unsigned long v;

			if (!strcmp(argv[i], "--coords")) {
				popts.coords = true;
				continue;
			}
			if (!strcmp(argv[i], "--pixels")) {
				popts.pixels = true;
				continue;
			}
			if (!strcmp(argv[i], "--low") && i + 1 < argc) {
				/* a page of the first MiB, page 0 excepted, room for the scratch */
				v = strtoul(argv[++i], &end, 0);
				if (*end || v < SGXFIVE_PAGE_SIZE || v % SGXFIVE_PAGE_SIZE ||
				    v + SCRATCH_PAGES * SGXFIVE_PAGE_SIZE > 0x100000)
					return usage();
				popts.low = v;
				continue;
			}
			if (!strcmp(argv[i], "--late") && i + 1 < argc) {
				/* R:K=V, two distinct dwords of the scratch and a 32-bit value */
				const uint32_t n = SCRATCH_PAGES * SGXFIVE_PAGE_SIZE / 4;
				unsigned long long r, k, val;
				int used = -1;

				if (sscanf(argv[++i], "%lli:%lli=%lli%n", &r, &k, &val, &used) != 3 ||
				    argv[i][used] || r >= n || k >= n || r == k || val > 0xffffffffULL)
					return usage();
				popts.late = true;
				popts.late_ready = (uint32_t)r;
				popts.late_dword = (uint32_t)k;
				popts.late_value = (uint32_t)val;
				continue;
			}
			if (!strcmp(argv[i], "--poke") && i + 1 < argc) {
				/* the fill's transfer command only: its 42 dwords */
				struct sgxfive_poke *pk = &popts.pokes[popts.npokes];

				if (popts.npokes == SGXFIVE_POKE_MAX ||
				    sgxfive_poke_parse(argv[i + 1], pk) ||
				    pk->space != SGXFIVE_POKE_XFER || pk->index >= 42) {
					fprintf(stderr, "sgxfive-test: probe --poke %s: xfer:0-41 "
						"only\n", argv[i + 1]);
					return 2;
				}
				popts.poke_args[popts.npokes++] = argv[++i];
				continue;
			}
			if (!strcmp(argv[i], "--tri") && i + 1 < argc) {
				if (probe_tri_slot(argv[++i], &popts.tri.slot, &popts.tri.data))
					return usage();
				continue;
			}
			if (!strcmp(argv[i], "--slot") && i + 1 < argc) {
				ret = probe_tri_fixed(argv[++i], &popts.tri);
				if (ret)
					return ret;
				continue;
			}
			if (!strcmp(argv[i], "--vertices") && i + 1 < argc) {
				v = strtoul(argv[++i], &end, 0);
				/* whole triangles that fit the vertex buffer */
				if (*end || !v || v % 3 || v > SGXFIVE_TRI_PROBE_MAX_VERTICES)
					return usage();
				popts.tri.vertices = (uint32_t)v;
				continue;
			}
			if (!strcmp(argv[i], "--dump-render") && i + 1 < argc) {
				popts.tri.dump_dir = argv[++i];
				continue;
			}
			if (!strcmp(argv[i], "--kpoke") && i + 1 < argc) {
				if (popts.tri.nkpoke == KPR_MAX)
					return usage();
				popts.tri.kpoke[popts.tri.nkpoke++] = argv[++i];
				continue;
			}
			if (!strcmp(argv[i], "--obj2") && i + 1 < argc) {
				v = strtoul(argv[++i], &end, 0);
				if (*end || !v || v >= SGXFIVE_TRI_PROBE_MAX_VERTICES)
					return usage();
				popts.tri.obj2 = (uint32_t)v;
				continue;
			}
			if (!strcmp(argv[i], "--obj2-blk") && i + 1 < argc) {
				char *eq;
				unsigned long n;

				n = strtoul(argv[++i], &eq, 0);
				if (*eq != '=' || eq == argv[i] || n >= SGXFIVE_TRI_PROBE_BLK2_WORDS ||
				    !eq[1])
					return usage();
				v = strtoul(eq + 1, &end, 0);
				if (*end || v > UINT32_MAX)
					return usage();
				popts.tri.obj2_blk_mask |= 1u << n;
				popts.tri.obj2_blk_val[n] = (uint32_t)v;
				continue;
			}
			if (!strcmp(argv[i], "--obj2-pixel") && i + 1 < argc) {
				if (popts.tri.obj2_pixel.n || probe_read(argv[++i], &popts.tri.obj2_pixel, 8))
					return usage();
				continue;
			}
			if (!strcmp(argv[i], "--copy-depth")) {
				popts.tri.copy_depth = true;
				continue;
			}
			if (!strcmp(argv[i], "--blk") && i + 1 < argc) {
				char *eq;
				unsigned long n;

				n = strtoul(argv[++i], &eq, 0);
				if (*eq != '=' || eq == argv[i] || n >= SGXFIVE_TRI_BLOCK_WORDS ||
				    !eq[1])
					return usage();
				v = strtoul(eq + 1, &end, 0);
				if (*end || v > UINT32_MAX)
					return usage();
				popts.tri.blk_mask |= 1u << n;
				popts.tri.blk_val[n] = (uint32_t)v;
				continue;
			}
			if (!strcmp(argv[i], "--cmd") && i + 1 < argc) {
				char *eq;
				unsigned long n;

				n = strtoul(argv[++i], &eq, 0);
				if (*eq != '=' || eq == argv[i] || n >= SGXFIVE_TRI_PROBE_CMD_WORDS ||
				    !eq[1])
					return usage();
				v = strtoul(eq + 1, &end, 0);
				if (*end || v > UINT32_MAX)
					return usage();
				popts.tri.cmd_mask |= 1u << n;
				popts.tri.cmd_val[n] = (uint32_t)v;
				continue;
			}
			if (!strcmp(argv[i], "--vdm") && i + 1 < argc) {
				char *eq;
				unsigned long n;

				bool flip;

				n = strtoul(argv[++i], &eq, 0);
				flip = eq[0] == '^';
				eq += flip;
				if (*eq != '=' || eq == argv[i] + flip || n >= SGXFIVE_TRI_VDM_WORDS ||
				    !eq[1])
					return usage();
				v = strtoul(eq + 1, &end, 0);
				if (*end || v > UINT32_MAX)
					return usage();
				if (flip) {
					popts.tri.vdm_xor_mask |= 1u << n;
					popts.tri.vdm_xor_val[n] = (uint32_t)v;
				} else {
					popts.tri.vdm_mask |= 1u << n;
					popts.tri.vdm_val[n] = (uint32_t)v;
				}
				continue;
			}
			if (!strcmp(argv[i], "--blk-add") && i + 1 < argc) {
				/* bits 2-5 one word, 7 two */
				char *eq, *p;
				unsigned long bit = strtoul(argv[++i], &eq, 0);
				unsigned int n, want;

				if (*eq != '=' || eq == argv[i] || !((bit >= 2 && bit <= 5) || bit == 7))
					return usage();
				want = bit == 7 ? 2 : 1;
				for (n = 0, p = eq + 1; n < want; n++, p = end + 1) {
					v = strtoul(p, &end, 0);
					if (end == p || v > UINT32_MAX ||
					    (n + 1 < want ? *end != ',' : *end != '\0'))
						return usage();
					popts.tri.add_val[bit][n] = (uint32_t)v;
				}
				popts.tri.add_mask |= 1u << bit;
				continue;
			}
			if (!strcmp(argv[i], "--isp2") && i + 1 < argc) {
				v = strtoul(argv[++i], &end, 0);
				if (*end || end == argv[i] || v > UINT32_MAX)
					return usage();
				popts.tri.isp2_set = true;
				popts.tri.isp2 = (uint32_t)v;
				continue;
			}
			if (!strcmp(argv[i], "--sideband") && i + 1 < argc) {
				v = strtoul(argv[++i], &end, 0);
				if (*end || end == argv[i] || v > UINT32_MAX)
					return usage();
				popts.tri.sideband_set = true;
				popts.tri.sideband = (uint32_t)v;
				continue;
			}
			if (!strcmp(argv[i], "--vtx-coords") && i + 1 < argc) {
				v = strtoul(argv[++i], &end, 0);
				/* the vertex size field: 4 position dwords + N, at most 15 */
				if (*end || !v || v > 11)
					return usage();
				popts.tri.coords = (uint32_t)v;
				continue;
			}
			if (probe_tri_size(argv[i], i + 1 < argc ? argv[i + 1] : NULL, &popts.tri)) {
				i++;
				continue;
			}
			if (!strcmp(argv[i], "--use") && i + 1 < argc) {
				if (probe_read(argv[++i], &popts.use, 8))
					return 1;
				continue;
			}
			if (!strcmp(argv[i], "--pds") && i + 1 < argc) {
				v = strtoul(argv[++i], &end, 0);
				/* whole rows of four dwords; row 0 holds U0-U2 */
				if (*end || v < 4 || v % 4 || v > 128)
					return usage();
				popts.pds_data = (uint32_t)v;
				continue;
			}
			if (strcmp(argv[i], "--temps") || i + 1 >= argc)
				return usage();
			v = strtoul(argv[++i], &end, 0);
			if (*end || v < 1 || v > 128)
				return usage();
			popts.temps = (uint32_t)v;
		}
		if (i >= argc || (popts.pds_data && !popts.use.n) || (popts.pds_data && popts.coords) ||
		    probe_tri_check(&popts))
			return usage();
		nprobes = (uint32_t)(argc - i);
		probes = calloc(nprobes, sizeof(*probes));
		if (!probes)
			return fail("probe", -ENOMEM);
		for (uint32_t k = 0; k < nprobes; k++) {
			const bool tri_pds = popts.tri.slot >= 0 &&
					     sgxfive_tri_slot_is_pds(popts.tri.slot);
			const uint32_t data = tri_pds ? popts.tri.data : popts.pds_data;

			if (probe_read(argv[i + k], &probes[k], popts.pds_data || tri_pds ? 4 : 8) ||
			    (data && probes[k].n <= data)) {
				free(probes);
				return 1;
			}
		}
		i = argc;
	}
	if (!strcmp(cmd, "tri")) {
		o.height = 64;			/* the first triangle's 64 x 64 */
		o.n = 1;
	}
	if (!strcmp(cmd, "contexts")) {
		o.height = 64;			/* 32 contexts for 64 x 64 targets */
		o.n = 32;
	}
	if (parse_opts(argc - i, argv + i, &o))
		return 2;
	if ((o.npokes || o.pixels || o.regs) && strcmp(cmd, "fill") && strcmp(cmd, "copy") &&
	    strcmp(cmd, "tri")) {
		fprintf(stderr, "sgxfive-test: --poke, --pixels and --regs are for fill, copy "
			"and tri\n");
		return 2;
	}
	if (o.dump_dir && strcmp(cmd, "tri")) {
		fprintf(stderr, "sgxfive-test: --dump-render is for tri (probe takes its own)\n");
		return 2;
	}
	if (o.geometry && (strcmp(cmd, "tri") || o.geometry >> (o.n - 1))) {
		fprintf(stderr, "sgxfive-test: --geometry is for tri, renders 1 to %u (the last "
			"render closes the scene)\n", o.n - 1);
		return 2;
	}
	for (unsigned int k = 0; k < o.nkpr + o.nmoves; k++) {
		const uint32_t n = k < o.nkpr ? o.kpr[k].n : o.moves[k - o.nkpr].n;

		if (strcmp(cmd, "tri") || !n || n > o.n) {
			fprintf(stderr, "sgxfive-test: --kpoke-render and --move are for tri, "
				"render 1 to %u\n", o.n);
			return 2;
		}
	}
	if (o.every_value && strcmp(cmd, "copy")) {
		fprintf(stderr, "sgxfive-test: --every-value is for copy\n");
		return 2;
	}

	/*
	 * Programs: our assembled ones by default. The fake source's images are
	 * not runnable; refuse to send them to a real GPU.
	 */
	needs_programs = !strcmp(cmd, "fill") || !strcmp(cmd, "copy") ||
			 !strcmp(cmd, "isolation") || !strcmp(cmd, "regaccess") || !strcmp(cmd, "probe");
	if (needs_programs && fake && !use_mock) {
		fprintf(stderr, "sgxfive-test: the fake program source is for the mock only "
			"(use --mock, or the default --programs=asm)\n");
		return 2;
	}
	if (needs_programs) {
		t.progs = fake ? sgxfive_prog_fake_create() : sgxfive_prog_asm_create();
		if (!t.progs)
			return fail("programs", -ENOMEM);
	}
	if (o.npokes && check_pokes(&t, cmd, &o)) {
		sgxfive_prog_source_destroy(t.progs);
		return 2;
	}

	if (use_mock)
		t.mock = sgxfive_mock_create(&mcfg);
	ret = sgxfive_dev_open(use_mock ? sgxfive_mock_backend(t.mock) : NULL, device, &t.dev);
	if (!ret && needs_programs)
		printf("programs %s\n", t.progs->name);
	if (ret) {
		if (ret == -ENODEV && !device)
			fprintf(stderr, "sgxfive-test: no sgxfive render node found\n");
		else
			fail(device ? device : "open", ret);
		ret = 1;
	} else if (!strcmp(cmd, "query")) {
		ret = cmd_query(&t);
	} else if (!strcmp(cmd, "dummy")) {
		ret = cmd_dummy(&t, &o);
	} else if (!strcmp(cmd, "fill")) {
		ret = cmd_fill(&t, &o);
	} else if (!strcmp(cmd, "copy")) {
		ret = cmd_copy(&t, &o);
	} else if (!strcmp(cmd, "regaccess")) {
		ret = cmd_regaccess(&t);
	} else if (!strcmp(cmd, "probe")) {
		ret = cmd_probe(&t, probes, nprobes, &popts);
	} else if (!strcmp(cmd, "tri")) {
		ret = cmd_tri(&t, &o);
	} else if (!strcmp(cmd, "contexts")) {
		ret = cmd_contexts(&t, &o);
	} else {
		ret = cmd_isolation(&t);
	}
	sgxfive_dev_close(t.dev);
	sgxfive_prog_source_destroy(t.progs);
	sgxfive_mock_destroy(t.mock);
	free(probes);
	return ret;
}
