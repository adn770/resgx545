// SPDX-License-Identifier: MIT
/*
 * Pokes (include/sgxfive_poke.h): parsing, the checks against a job's views,
 * set and flip, the views of fills, copies and triangles, and, on the mock,
 * that a poke changes exactly the word it addresses in the job that is
 * submitted and nothing else.
 */
#include <errno.h>
#include <stdlib.h>
#include <string.h>

#include "sgxfive_mock.h"
#include "sgxfive_poke.h"
#include "sgxfive_render.h"
#include "sgxfive_xfer.h"
#include "tap.h"

#define NSEC 1000000000LL

static void parse(void)
{
	static const char *const bad[] = {
		"", "cmd", "cmd:", "cmd:1", "cmd:1=", "cmd:=1", "cmd:x=1", "cmd:1=x",
		"cmd:1~=1", "cmd:1=0x100000000", "frob:1=1", "pds:1=1", "pds::1=1",
		"cmd:pixev:1=1", "pds:abcdefghijklmnopq:1=1", "cmd:-1=1", "cmd:1=-1",
		"cmd:1==1", "cmd:1^1",
	};
	struct sgxfive_poke pk;

	CHECK_EQ(sgxfive_poke_parse("cmd:3=0x10", &pk), 0);
	CHECK_EQ(pk.space, SGXFIVE_POKE_CMD);
	CHECK_EQ(pk.index, 3);
	CHECK_EQ(pk.value, 0x10);
	CHECK(!pk.flip);
	CHECK(!strcmp(pk.slot, ""));
	CHECK_EQ(sgxfive_poke_parse("xfer:41^=0x80000000", &pk), 0);
	CHECK_EQ(pk.space, SGXFIVE_POKE_XFER);
	CHECK_EQ(pk.index, 41);
	CHECK_EQ(pk.value, 0x80000000);
	CHECK(pk.flip);
	CHECK_EQ(sgxfive_poke_parse("pds:pixev:0x13=0xffffffff", &pk), 0);
	CHECK_EQ(pk.space, SGXFIVE_POKE_PDS);
	CHECK(!strcmp(pk.slot, "pixev"));
	CHECK_EQ(pk.index, 0x13);
	CHECK_EQ(pk.value, 0xffffffff);
	for (uint32_t s = 0; s < SGXFIVE_POKE_SPACE_COUNT; s++) {
		char arg[64];

		snprintf(arg, sizeof(arg), "%s%s:1=2", sgxfive_poke_space_name(s),
			 s == SGXFIVE_POKE_PDS ? ":prim" : "");
		CHECK_EQ(sgxfive_poke_parse(arg, &pk), 0);
		CHECK_EQ(pk.space, s);
	}
	CHECK(!sgxfive_poke_space_name(SGXFIVE_POKE_SPACE_COUNT));
	for (size_t i = 0; i < sizeof(bad) / sizeof(bad[0]); i++)
		if (!CHECK_EQ(sgxfive_poke_parse(bad[i], &pk), -EINVAL))
			printf("#   %s\n", bad[i]);
}

static void apply(void)
{
	static const uint8_t tmap[4] = { 2, 3, 0, 1 };
	uint32_t a[4] = { 0x10, 0x20, 0x30, 0x40 }, b[6] = { 0 };
	const struct sgxfive_poke_view v[] = {
		{ SGXFIVE_POKE_CMD, NULL, a, 4, NULL },
		{ SGXFIVE_POKE_PDS, "prim", b, 6, NULL },
		{ SGXFIVE_POKE_TEX, NULL, b + 2, 4, tmap },
	};
	struct sgxfive_poke pk[3];
	const struct sgxfive_poke_view *got;
	unsigned int bad = 99;

	sgxfive_poke_parse("cmd:3=7", &pk[0]);
	CHECK_EQ(sgxfive_poke_find(v, 3, &pk[0], &got), 0);
	CHECK(got == &v[0]);
	sgxfive_poke_parse("cmd:4=7", &pk[0]);
	CHECK_EQ(sgxfive_poke_find(v, 3, &pk[0], &got), -ERANGE);
	sgxfive_poke_parse("xfer:0=7", &pk[0]);
	CHECK_EQ(sgxfive_poke_find(v, 3, &pk[0], &got), -ENOENT);
	sgxfive_poke_parse("pds:sec:0=7", &pk[0]);
	CHECK_EQ(sgxfive_poke_find(v, 3, &pk[0], &got), -ENOENT);
	sgxfive_poke_parse("pds:prim:5=7", &pk[0]);
	CHECK_EQ(sgxfive_poke_find(v, 3, &pk[0], &got), 0);
	CHECK(got == &v[1]);

	/* set, flip, and a mapped view */
	sgxfive_poke_parse("cmd:1=0xabc", &pk[0]);
	sgxfive_poke_parse("cmd:2^=0x101", &pk[1]);
	sgxfive_poke_parse("tex:0=0x55", &pk[2]);
	CHECK_EQ(sgxfive_poke_apply(v, 3, pk, 3, &bad), 0);
	CHECK_EQ(a[0], 0x10);
	CHECK_EQ(a[1], 0xabc);
	CHECK_EQ(a[2], 0x30 ^ 0x101);
	CHECK_EQ(a[3], 0x40);
	CHECK_EQ(b[4], 0x55);		/* T0 is the view's word 2 */
	CHECK_EQ(b[2] | b[3] | b[5], 0);

	/* nothing is written when one poke is bad; bad says which */
	sgxfive_poke_parse("cmd:0=1", &pk[0]);
	sgxfive_poke_parse("bg:0=1", &pk[1]);
	CHECK_EQ(sgxfive_poke_apply(v, 3, pk, 2, &bad), -ENOENT);
	CHECK_EQ(bad, 1);
	CHECK_EQ(a[0], 0x10);
	sgxfive_poke_parse("tex:4=1", &pk[1]);
	CHECK_EQ(sgxfive_poke_apply(v, 3, pk, 2, &bad), -ERANGE);
	CHECK_EQ(a[0], 0x10);

	/* the hash: FNV-1a 64 of the bytes */
	CHECK_EQ(sgxfive_hash_dwords(NULL, 0), 0xcbf29ce484222325ull);
	a[0] = 0x64636261;		/* "abcd" */
	CHECK_EQ(sgxfive_hash_dwords(a, 1), 0xfc179f83ee0724ddull);
}

static uint32_t view_count(const struct sgxfive_poke_view *v, unsigned int n, uint32_t space,
			   const char *slot)
{
	for (unsigned int i = 0; i < n; i++)
		if (v[i].space == space && (!slot || (v[i].slot && !strcmp(v[i].slot, slot))))
			return v[i].count;
	return 0;
}

/* The views come from the built job's sizes. */
static void layouts(void)
{
	struct sgxfive_prog_source *src = sgxfive_prog_asm_create();
	struct sgxfive_poke_view v[SGXFIVE_POKE_VIEWS_MAX];
	unsigned int n;

	n = sgxfive_render_poke_layout(v);
	CHECK_EQ(view_count(v, n, SGXFIVE_POKE_CMD, NULL), sizeof(struct drm_sgxfive_render_cmd) / 4);
	CHECK_EQ(view_count(v, n, SGXFIVE_POKE_VDM, NULL), SGXFIVE_TRI_VDM_WORDS);
	CHECK_EQ(view_count(v, n, SGXFIVE_POKE_EOS, NULL), SGXFIVE_TRI_EOS_WORDS);
	CHECK_EQ(view_count(v, n, SGXFIVE_POKE_BLK, NULL), SGXFIVE_TRI_BLOCK_WORDS);
	CHECK_EQ(view_count(v, n, SGXFIVE_POKE_PDS, "vtx"), 8);
	CHECK_EQ(view_count(v, n, SGXFIVE_POKE_PDS, "state"), 8);
	CHECK_EQ(view_count(v, n, SGXFIVE_POKE_PDS, "eos"), 8);
	CHECK_EQ(view_count(v, n, SGXFIVE_POKE_PDS, "prim"), 4);
	CHECK_EQ(view_count(v, n, SGXFIVE_POKE_PDS, "bgprim"), 4);
	CHECK_EQ(view_count(v, n, SGXFIVE_POKE_PDS, "sec"), 4);
	CHECK_EQ(view_count(v, n, SGXFIVE_POKE_PDS, "pixev"), 20);
	CHECK_EQ(view_count(v, n, SGXFIVE_POKE_XFER, NULL), 0);
	CHECK_EQ(view_count(v, n, SGXFIVE_POKE_TEX, NULL), 0);
	CHECK_EQ(view_count(v, n, SGXFIVE_POKE_BG, NULL), 0);
	for (unsigned int i = 0; i < n; i++)
		CHECK(!v[i].words);

	n = sgxfive_xfer_poke_layout(src, false, v);
	CHECK_EQ(view_count(v, n, SGXFIVE_POKE_XFER, NULL),
		 sizeof(struct drm_sgxfive_transfer_cmd) / 4);
	CHECK_EQ(view_count(v, n, SGXFIVE_POKE_BG, NULL), SGXFIVE_BGOBJ_DWORDS);
	CHECK_EQ(view_count(v, n, SGXFIVE_POKE_PDS, "prim"), 4);
	CHECK_EQ(view_count(v, n, SGXFIVE_POKE_PDS, "sec"), 4);
	CHECK_EQ(view_count(v, n, SGXFIVE_POKE_PDS, "pixev"), 20);
	CHECK_EQ(view_count(v, n, SGXFIVE_POKE_TEX, NULL), 0);
	CHECK_EQ(view_count(v, n, SGXFIVE_POKE_CMD, NULL), 0);

	n = sgxfive_xfer_poke_layout(src, true, v);
	/* a copy's object has one layer, its view room for two (the layer probes) */
	CHECK_EQ(view_count(v, n, SGXFIVE_POKE_BG, NULL), SGXFIVE_BGOBJ2_DWORDS);
	CHECK_EQ(view_count(v, n, SGXFIVE_POKE_PDS, "prim"), 12);
	CHECK_EQ(view_count(v, n, SGXFIVE_POKE_TEX, NULL), 4);
	sgxfive_prog_source_destroy(src);
}

/* ---- On the mock: exactly the addressed word changes in the submitted job ----------- */

#define XPAGES	3
#define RPAGES	5

/* The command and the pages of a job, as one array of dwords. */
struct snap {
	uint32_t w[256 / 4 + RPAGES * 1024];
	uint32_t n;
};

static const uint32_t xheaps[XPAGES] = {
	DRM_SGXFIVE_HEAP_PDS_PIXEL, DRM_SGXFIVE_HEAP_USSE_PIXEL, DRM_SGXFIVE_HEAP_GENERAL,
};
static const uint32_t rheaps[RPAGES] = {
	DRM_SGXFIVE_HEAP_PDS_VERTEX, DRM_SGXFIVE_HEAP_USSE_VERTEX, DRM_SGXFIVE_HEAP_PDS_PIXEL,
	DRM_SGXFIVE_HEAP_USSE_PIXEL, DRM_SGXFIVE_HEAP_GENERAL,
};

static void snap_add(struct snap *s, const void *p, uint32_t bytes)
{
	memcpy(s->w + s->n, p, bytes);
	s->n += bytes / 4;
}

/* Where a word of the job sits in a snapshot: -1 if in no page. */
static int64_t snap_pos(const void *word, const void *cmd, uint32_t cmd_bytes,
			const void *const *pages, unsigned int npages)
{
	const uint8_t *w = word;

	if (w >= (const uint8_t *)cmd && w < (const uint8_t *)cmd + cmd_bytes)
		return (w - (const uint8_t *)cmd) / 4;
	for (unsigned int i = 0; i < npages; i++)
		if (w >= (const uint8_t *)pages[i] && w < (const uint8_t *)pages[i] + 4096)
			return cmd_bytes / 4 + i * 1024 + (w - (const uint8_t *)pages[i]) / 4;
	return -1;
}

/* The one word a and b differ in, -1 if none, -2 if more than one. */
static int64_t diff_one(const struct snap *a, const struct snap *b)
{
	int64_t at = -1;

	for (uint32_t i = 0; i < a->n; i++)
		if (a->w[i] != b->w[i]) {
			if (at >= 0)
				return -2;
			at = i;
		}
	return at;
}

struct xenv {
	struct sgxfive_mock *mock;
	struct sgxfive_dev *dev;
	struct sgxfive_vm *vm;
	uint32_t ctx;
	struct sgxfive_xfer *x;
	struct sgxfive_prog_source *src;
	struct sgxfive_bo *sbo, *dbo;
	struct sgxfive_surface s, d;
};

static void xenv_init(struct xenv *e)
{
	const struct sgxfive_mock_config cfg = { .layout = SGXFIVE_MOCK_LAYOUT_REV1 };
	void *p;

	memset(e, 0, sizeof(*e));
	e->mock = sgxfive_mock_create(&cfg);
	e->src = sgxfive_prog_asm_create();
	sgxfive_dev_open(sgxfive_mock_backend(e->mock), NULL, &e->dev);
	sgxfive_vm_create(e->dev, &e->vm);
	sgxfive_ctx_create(e->vm, &e->ctx);
	sgxfive_xfer_create(e->vm, e->ctx, e->src, &e->x);
	e->s = (struct sgxfive_surface){ 0, 64, 32, 256 };
	e->d = e->s;
	sgxfive_bo_create(e->dev, 2 * 4096 * 4, DRM_SGXFIVE_BO_ALLOW_CPU_ACCESS, &e->sbo);
	sgxfive_bo_create(e->dev, 2 * 4096 * 4, DRM_SGXFIVE_BO_ALLOW_CPU_ACCESS, &e->dbo);
	sgxfive_bo_mmap(e->sbo, &p);
	sgxfive_vm_alloc(e->vm, DRM_SGXFIVE_HEAP_GENERAL, 8 * 4096, 4096, &e->s.addr);
	sgxfive_vm_map(e->vm, e->s.addr, e->sbo, 0, 8 * 4096, 0);
	sgxfive_vm_alloc(e->vm, DRM_SGXFIVE_HEAP_GENERAL, 8 * 4096, 4096, &e->d.addr);
	sgxfive_vm_map(e->vm, e->d.addr, e->dbo, 0, 8 * 4096, 0);
}

static void xenv_fini(struct xenv *e)
{
	sgxfive_xfer_destroy(e->x);
	sgxfive_bo_destroy(e->sbo);
	sgxfive_bo_destroy(e->dbo);
	sgxfive_ctx_destroy(e->dev, e->ctx);
	sgxfive_vm_destroy(e->vm);
	sgxfive_dev_close(e->dev);
	sgxfive_prog_source_destroy(e->src);
	sgxfive_mock_destroy(e->mock);
}

static int xrun(struct xenv *e, bool copy, struct snap *s)
{
	const struct sgxfive_rect r = { 0, 0, 64, 32 };
	const void *pages[XPAGES];
	int ret;

	ret = copy ? sgxfive_xfer_copy(e->x, &e->s, 0, 0, &e->d, &r, 0)
		   : sgxfive_xfer_fill(e->x, &e->d, &r, 0xff336699, 0);
	s->n = 0;
	snap_add(s, sgxfive_xfer_last_cmd(e->x), sizeof(struct drm_sgxfive_transfer_cmd));
	for (unsigned int i = 0; i < XPAGES; i++) {
		pages[i] = sgxfive_xfer_page(e->x, xheaps[i]);
		snap_add(s, pages[i], 4096);
	}
	sgxfive_xfer_wait(e->x, NSEC);
	return ret;
}

/* Where poke pk's word is in a transfer job's snapshot, from a pointer into its pages. */
static int64_t xpos(struct xenv *e, bool copy, const struct sgxfive_poke *pk)
{
	struct sgxfive_poke_view v[SGXFIVE_POKE_VIEWS_MAX];
	const struct sgxfive_poke_view *got;
	const void *pages[XPAGES];
	const uint32_t *word;
	unsigned int n = sgxfive_xfer_poke_views(e->x, copy, v);

	for (unsigned int i = 0; i < XPAGES; i++)
		pages[i] = sgxfive_xfer_page(e->x, xheaps[i]);
	if (sgxfive_poke_find(v, n, pk, &got))
		return -3;
	word = &got->words[got->map ? got->map[pk->index] : pk->index];
	return snap_pos(word, sgxfive_xfer_last_cmd(e->x),
			sizeof(struct drm_sgxfive_transfer_cmd), pages, XPAGES);
}

static void xfer_pokes(bool copy)
{
	struct sgxfive_prog_source *src = sgxfive_prog_asm_create();
	struct sgxfive_poke_view v[SGXFIVE_POKE_VIEWS_MAX];
	unsigned int n = sgxfive_xfer_poke_layout(src, copy, v);
	static struct snap a, b;

	for (unsigned int k = 0; k < n; k++) {
		/* first and last word of every view, a flip and a set */
		for (unsigned int j = 0; j < 2; j++) {
			struct sgxfive_poke pk = {
				.space = v[k].space, .index = j ? v[k].count - 1 : 0,
				.value = j ? 0x80000001u : 0x00010000u, .flip = j,
			};
			struct xenv e;
			int64_t at, want;

			if (v[k].slot)
				snprintf(pk.slot, sizeof(pk.slot), "%s", v[k].slot);
			xenv_init(&e);
			CHECK_EQ(xrun(&e, copy, &a), 0);
			sgxfive_xfer_set_hook(e.x, sgxfive_poke_hook,
					      &(struct sgxfive_poke_set){ &pk, 1 });
			xrun(&e, copy, &b);
			at = diff_one(&a, &b);
			want = xpos(&e, copy, &pk);
			if (!CHECK(at >= 0 && at == want))
				printf("#   %s %s:%s:%u: diff at %lld, want %lld\n",
				       copy ? "copy" : "fill", sgxfive_poke_space_name(pk.space),
				       pk.slot, pk.index, (long long)at, (long long)want);
			if (at >= 0)
				CHECK_EQ(b.w[at], pk.flip ? a.w[at] ^ pk.value : pk.value);
			xenv_fini(&e);
		}
	}
	sgxfive_prog_source_destroy(src);
}

/* A space the job does not have, or an index past a view: refused, nothing submitted. */
static void xfer_refused(void)
{
	struct xenv e;
	struct sgxfive_poke pk;
	struct sgxfive_poke_set set = { &pk, 1 };
	const struct sgxfive_rect r = { 0, 0, 64, 32 };

	xenv_init(&e);
	sgxfive_poke_parse("cmd:0=1", &pk);
	sgxfive_xfer_set_hook(e.x, sgxfive_poke_hook, &set);
	CHECK_EQ(sgxfive_xfer_fill(e.x, &e.d, &r, 0, 0), -ENOENT);
	sgxfive_poke_parse("xfer:42=1", &pk);
	CHECK_EQ(sgxfive_xfer_fill(e.x, &e.d, &r, 0, 0), -ERANGE);
	sgxfive_poke_parse("tex:0=1", &pk);
	CHECK_EQ(sgxfive_xfer_fill(e.x, &e.d, &r, 0, 0), -ENOENT);
	CHECK_EQ(sgxfive_xfer_copy(e.x, &e.s, 0, 0, &e.d, &r, 0), 0);
	CHECK_EQ(sgxfive_xfer_wait(e.x, NSEC), 0);
	sgxfive_xfer_set_hook(e.x, NULL, NULL);
	CHECK_EQ(sgxfive_xfer_fill(e.x, &e.d, &r, 0, 0), 0);
	CHECK_EQ(sgxfive_xfer_wait(e.x, NSEC), 0);
	xenv_fini(&e);
}

struct renv {
	struct sgxfive_mock *mock;
	struct sgxfive_dev *dev;
	struct sgxfive_vm *vm;
	uint32_t ctx;
	struct sgxfive_render *r;
	struct sgxfive_tri_params p;
};

static void renv_init(struct renv *e)
{
	const struct sgxfive_mock_config cfg = { .layout = SGXFIVE_MOCK_LAYOUT_REV1 };

	memset(e, 0, sizeof(*e));
	e->mock = sgxfive_mock_create(&cfg);
	sgxfive_dev_open(sgxfive_mock_backend(e->mock), NULL, &e->dev);
	sgxfive_vm_create(e->dev, &e->vm);
	sgxfive_render_ctx_create(e->vm, 64, 64, &e->ctx);
	sgxfive_render_create(e->vm, e->ctx, &e->r);
	sgxfive_tri_default(&e->p, 64, 64);
}

static void renv_fini(struct renv *e)
{
	sgxfive_render_destroy(e->r);
	sgxfive_ctx_destroy(e->dev, e->ctx);
	sgxfive_vm_destroy(e->vm);
	sgxfive_dev_close(e->dev);
	sgxfive_mock_destroy(e->mock);
}

static int rrun(struct renv *e, struct snap *s)
{
	int ret = sgxfive_render_tri(e->r, &e->p, 0, 0);

	s->n = 0;
	snap_add(s, sgxfive_render_last_cmd(e->r), sizeof(struct drm_sgxfive_render_cmd));
	for (unsigned int i = 0; i < RPAGES; i++)
		snap_add(s, sgxfive_render_page(e->r, rheaps[i]), 4096);
	sgxfive_render_wait(e->r, NSEC);
	return ret;
}

static void render_pokes(void)
{
	struct sgxfive_poke_view v[SGXFIVE_POKE_VIEWS_MAX];
	unsigned int n = sgxfive_render_poke_layout(v);
	static struct snap a, b;

	for (unsigned int k = 0; k < n; k++) {
		for (unsigned int j = 0; j < 2; j++) {
			struct sgxfive_poke pk = {
				.space = v[k].space, .index = j ? v[k].count - 1 : 0,
				.value = j ? 0x80000001u : 0x00010000u, .flip = j,
			};
			struct sgxfive_poke_view rv[SGXFIVE_POKE_VIEWS_MAX];
			const struct sgxfive_poke_view *got;
			const void *pages[RPAGES];
			struct renv e;
			int64_t at, want;
			unsigned int rn;

			if (v[k].slot)
				snprintf(pk.slot, sizeof(pk.slot), "%s", v[k].slot);
			renv_init(&e);
			CHECK_EQ(rrun(&e, &a), 0);
			sgxfive_render_set_hook(e.r, sgxfive_poke_hook,
						&(struct sgxfive_poke_set){ &pk, 1 });
			rrun(&e, &b);
			at = diff_one(&a, &b);
			rn = sgxfive_render_poke_views(e.r, rv);
			for (unsigned int i = 0; i < RPAGES; i++)
				pages[i] = sgxfive_render_page(e.r, rheaps[i]);
			want = sgxfive_poke_find(rv, rn, &pk, &got) ? -3 :
			       snap_pos(&got->words[pk.index], sgxfive_render_last_cmd(e.r),
					sizeof(struct drm_sgxfive_render_cmd), pages, RPAGES);
			if (!CHECK(at >= 0 && at == want))
				printf("#   tri %s:%s:%u: diff at %lld, want %lld\n",
				       sgxfive_poke_space_name(pk.space), pk.slot, pk.index,
				       (long long)at, (long long)want);
			if (at >= 0)
				CHECK_EQ(b.w[at], pk.flip ? a.w[at] ^ pk.value : pk.value);
			renv_fini(&e);
		}
	}
}

static void render_refused(void)
{
	struct renv e;
	struct sgxfive_poke pk;
	struct sgxfive_poke_set set = { &pk, 1 };

	renv_init(&e);
	sgxfive_poke_parse("xfer:0=1", &pk);
	sgxfive_render_set_hook(e.r, sgxfive_poke_hook, &set);
	CHECK_EQ(sgxfive_render_tri(e.r, &e.p, 0, 0), -ENOENT);
	sgxfive_poke_parse("cmd:26=1", &pk);
	CHECK_EQ(sgxfive_render_tri(e.r, &e.p, 0, 0), -ERANGE);
	sgxfive_poke_parse("pds:frob:0=1", &pk);
	CHECK_EQ(sgxfive_render_tri(e.r, &e.p, 0, 0), -ENOENT);
	sgxfive_render_set_hook(e.r, NULL, NULL);
	CHECK_EQ(sgxfive_render_tri(e.r, &e.p, 0, 0), 0);
	CHECK_EQ(sgxfive_render_wait(e.r, NSEC), 0);
	renv_fini(&e);
}

int main(void)
{
	parse();
	apply();
	layouts();
	xfer_pokes(false);
	xfer_pokes(true);
	xfer_refused();
	render_pokes();
	render_refused();
	return tap_done();
}
