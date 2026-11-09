// SPDX-License-Identifier: MIT
/*
 * Probe programs in the first triangle's render (sgxfive_tri_probe.h): the
 * caller's programs in place of the scene's, patched as render.c patches the
 * defaults, and a render engine whose pages the caller can see.
 */
#include <errno.h>
#include <stdlib.h>
#include <string.h>

#include "sgxfive_tri_probe.h"

static const char *const slot_names[SGXFIVE_TRI_SLOT_COUNT] = {
	[SGXFIVE_TRI_SLOT_PIXEV] = "pixev", [SGXFIVE_TRI_SLOT_EOT] = "eot",
	[SGXFIVE_TRI_SLOT_VTXPDS] = "vtxpds", [SGXFIVE_TRI_SLOT_VTXUSE] = "vtxuse",
	[SGXFIVE_TRI_SLOT_PIXEL] = "pixel", [SGXFIVE_TRI_SLOT_PIXTASK] = "pixtask",
	[SGXFIVE_TRI_SLOT_PIXPDS] = "pixpds", [SGXFIVE_TRI_SLOT_STATE] = "state",
	[SGXFIVE_TRI_SLOT_BGPDS] = "bgpds", [SGXFIVE_TRI_SLOT_BGPIXEL] = "bgpixel",
};

int sgxfive_tri_slot_find(const char *name)
{
	for (int i = 0; i < SGXFIVE_TRI_SLOT_COUNT; i++)
		if (!strcmp(name, slot_names[i]))
			return i;
	return -1;
}

const char *sgxfive_tri_slot_name(unsigned int slot)
{
	return slot < SGXFIVE_TRI_SLOT_COUNT ? slot_names[slot] : "?";
}

bool sgxfive_tri_slot_is_pds(unsigned int slot)
{
	return slot == SGXFIVE_TRI_SLOT_PIXEV || slot == SGXFIVE_TRI_SLOT_VTXPDS ||
	       slot == SGXFIVE_TRI_SLOT_PIXPDS || slot == SGXFIVE_TRI_SLOT_BGPDS;
}

/* Per slot: its place (page offset and end), the data dwords patched, default temps. */
static const struct {
	uint32_t off, end, min_data, temps;
} slot_place[SGXFIVE_TRI_SLOT_COUNT] = {
	[SGXFIVE_TRI_SLOT_PIXEV] = { SGXFIVE_TRI_PP_PIXEV, SGXFIVE_TRI_PROBE_PP_PIXPDS, 16, 0 },
	[SGXFIVE_TRI_SLOT_EOT] = { SGXFIVE_TRI_PROBE_UP_EOT, SGXFIVE_TRI_PROBE_UP_BGPIXEL, 0, 4 },
	[SGXFIVE_TRI_SLOT_VTXPDS] = { SGXFIVE_TRI_PROBE_PV_VTX, SGXFIVE_PAGE_SIZE, 8, 0 },
	[SGXFIVE_TRI_SLOT_VTXUSE] = { SGXFIVE_TRI_PROBE_UV_VTX, SGXFIVE_PAGE_SIZE, 0, 0 },
	[SGXFIVE_TRI_SLOT_PIXEL] = { SGXFIVE_TRI_PROBE_UP_PIXEL, SGXFIVE_TRI_PROBE_UP_PIXTASK, 0, 0 },
	[SGXFIVE_TRI_SLOT_PIXTASK] = { SGXFIVE_TRI_PROBE_UP_PIXTASK, SGXFIVE_TRI_PROBE_UP_EOT, 0, 0 },
	[SGXFIVE_TRI_SLOT_PIXPDS] = { SGXFIVE_TRI_PROBE_PP_PIXPDS, SGXFIVE_TRI_PROBE_PP_BGPDS, 4, 0 },
	[SGXFIVE_TRI_SLOT_STATE] = { SGXFIVE_TRI_UV_MTE18, SGXFIVE_TRI_UV_MTE2, 0, 0 },
	[SGXFIVE_TRI_SLOT_BGPDS] = { SGXFIVE_TRI_PROBE_PP_BGPDS, SGXFIVE_PAGE_SIZE, 4, 0 },
	[SGXFIVE_TRI_SLOT_BGPIXEL] = { SGXFIVE_TRI_PROBE_UP_BGPIXEL, SGXFIVE_PAGE_SIZE, 0, 0 },
};

#define EOT_MIN_WORDS	6	/* phas, the four PBE movs, the emitpix2 */
#define PDS_MAX_DATA	128	/* two banks of 64 dwords */
#define USE_MAX_TEMPS	128
#define PRIM_DATA	4		/* tri_pds_prim's data dwords (TRI_PDS_PRIM_DATA) */
#define VDM_DATA_ROWS	0x7fu	/* the vertex task's data rows, VDM word 7 */
#define VDM_INDEX_COUNT	0x3fffffu	/* the index list's count, VDM word 2 */
/* The state block (render.c): OUTSEL's vertex size in dwords, [19:16]; coordsize. */
#define BLK_ISP2	3		/* with isp2_set */
#define BLK_WRAP	12
#define BLK_OUTSEL	13
#define PRESENT_ISP2	(1u << 2)
#define PRESENT_WRAP	(1u << 9)
#define ISP0_ISP2_PRESENT	(1u << 8)
/* blk_add: the presence bits a probe may add, the words each bit adds, the room */
#define ADD_ALLOWED	(0x3cu | 1u << 7)
#define BLOCK_MAX_WORDS	32		/* SGXFIVE_TRI_PV_BLOCK to _PV_EOSBLOCK */
#define VDM_ATTR_ROWS	0xffu
#define MTE18_MOVE2	6		/* use_mtest18's mov.repeat2 o16, pa16 */
#define REPEAT_SHIFT	44		/* a mov's repeat count - 1, enc[47:44] */
#define BLK_COORDSIZE	16
#define OUTSEL_VTX_SIZE	0xf0000u
#define VDM_OUTPUT_SIZE	0xff000000u	/* the vertex task's, VDM word 7 */
#define OUTSEL_VTX_SIZE_MAX	15

/* A limm "mov d, #imm" (as sgxfive-test's probes): class 31, bit 53 set, 52 clear. */
#define LIMM_MASK	0xFF30000000000000ull
#define LIMM_VAL	0xFC20000000000000ull
/* phas: class 31, enc[54:52] = 4 (isa/usse/forms/class-31-cache-control-phas.toml), next phase in [17:0]. */
#define PHAS_MASK	0xFF70000000000000ull
#define PHAS_VAL	0xFA40000000000000ull
#define PHAS_NEXT	0x3ffffull
/* br #n: n instructions from the br itself, signed 18 bits (isa/usse/). */
#define BR_VAL		0xF800004000000000ull
#define BR_OFFSET	0x3ffffull

static int check(unsigned int slot, const struct sgxfive_tri_prog *g)
{
	const uint32_t width = sgxfive_tri_slot_is_pds(slot) ? 4 : 8;

	if (!g->n)
		return 0;
	if ((uint64_t)g->n * width > slot_place[slot].end - slot_place[slot].off)
		return -EINVAL;
	if (sgxfive_tri_slot_is_pds(slot))
		return g->data % 4 || g->data < slot_place[slot].min_data ||
		       g->data > PDS_MAX_DATA || g->n <= g->data ? -EINVAL : 0;
	if (g->temps > USE_MAX_TEMPS)
		return -EINVAL;
	return slot == SGXFIVE_TRI_SLOT_EOT && g->n < EOT_MIN_WORDS ? -EINVAL : 0;
}

static uint32_t temps(unsigned int slot, const struct sgxfive_tri_prog *g)
{
	return g->temps > slot_place[slot].temps ? g->temps : slot_place[slot].temps;
}

static uint64_t get_insn(const uint32_t *p, uint32_t i)
{
	return p[2 * i] | (uint64_t)p[2 * i + 1] << 32;
}

static void set_insn(uint32_t *p, uint32_t i, uint64_t v)
{
	p[2 * i] = (uint32_t)v;
	p[2 * i + 1] = (uint32_t)(v >> 32);
}

/*
 * The PDS words at area + off, keeping the dwords keep[] says from what is there, and with
 * every data dword SGXFIVE_TRI_PROBE_SCRATCH_IMM | k pointing at scratch + k.
 */
struct imm_base {
	uint32_t scratch, target;	/* 0: that kind of immediate is not patched */
};

/* imm, or the address its 0x5CAF or 0x5CB0 prefix and low 16 bits name */
static uint32_t imm_patch(uint32_t imm, const struct imm_base *b)
{
	if (b->scratch && (imm & ~0xffffu) == SGXFIVE_TRI_PROBE_SCRATCH_IMM)
		return b->scratch + (imm & 0xffff);
	if (b->target && (imm & ~0xffffu) == SGXFIVE_TRI_PROBE_TARGET_IMM)
		return b->target + (imm & 0xffff);
	return imm;
}

static void put_pds(uint32_t *area, uint32_t off, const struct sgxfive_tri_prog *g,
		    const uint32_t *keep, unsigned int nkeep, const struct imm_base *ib)
{
	uint32_t saved[16], *w = area + off / 4;

	for (unsigned int k = 0; k < nkeep; k++)
		saved[k] = w[keep[k]];
	for (uint32_t i = 0; i < g->n; i++) {
		w[i] = (uint32_t)g->words[i];
		if (i < g->data)
			w[i] = imm_patch(w[i], ib);
	}
	for (unsigned int k = 0; k < nkeep; k++)
		w[keep[k]] = saved[k];
}

/* The USSE words at area + off with their scratch immediates patched. */
static uint32_t *put_usse(uint32_t *area, uint32_t off, const struct sgxfive_tri_prog *g,
			  const struct imm_base *ib)
{
	uint32_t *w = area + off / 4;

	for (uint32_t i = 0; i < g->n; i++) {
		uint64_t v = g->words[i];
		const uint32_t imm = sgxfive_limm_get(v);

		if ((v & LIMM_MASK) == LIMM_VAL && imm_patch(imm, ib) != imm)
			v = sgxfive_limm_set(v, imm_patch(imm, ib));
		set_insn(w, i, v);
	}
	return w;
}

/* Clip space as render.c's ndc(): px / (W / 2) - 1, px in 1/16 pixel. */
static uint32_t ndc(int32_t px16, uint32_t size)
{
	return sgxfive_f32((float)px16 / (8.0f * (float)size) - 1.0f);
}

/*
 * n vertices: the triangle's three, then copies of it, copy c moved c/16 pixel right and
 * down; the index list 0 to n - 1 (16-bit pairs, or with idx32 32-bit words and the header's
 * SGXFIVE_TRI_PROBE_VDM_INDEX32), its count in the VDM's index-list word. More than the
 * scene's vertex buffer holds go to the page's spare room, the vertex PDS's buffer and the
 * VDM's index-list address pointing there.
 */
/*
 * blk_add: rebuild the state block with pr's presence bits and words in bit order, pad it to
 * whole rows of four and grow the state copy to match: the doutd word, the VDM state's
 * attribute rows and use_mtest18's second move (repeat16: 32 dwords, the room's whole).
 */
static int add_words(const struct sgxfive_tri_cpu *c, const struct sgxfive_tri_probe *pr)
{
	static const uint8_t words[16] = { 1, 1, 1, 1, 1, 1, 3, 2, 6, 1, 1, 1, 1, 1, 1, 1 };
	uint32_t *blk = c->pdsv + SGXFIVE_TRI_PV_BLOCK / 4;
	uint32_t out[BLOCK_MAX_WORDS] = { 0 }, presence = blk[0], n = 1, i = 1;
	uint32_t *move = c->usev + (SGXFIVE_TRI_UV_MTE18 + MTE18_MOVE2 * 8) / 4;

	if (pr->add_mask & ~ADD_ALLOWED || pr->add_mask & presence)
		return -1;
	out[0] = presence | pr->add_mask;
	for (unsigned int b = 0; b < 16; b++) {
		if (!(out[0] >> b & 1))
			continue;
		if (n + words[b] > BLOCK_MAX_WORDS)
			return -1;
		for (unsigned int k = 0; k < words[b]; k++)
			out[n++] = presence >> b & 1 ? blk[i++] : pr->add_val[b][k];
	}
	n = (n + 3) & ~3u;
	memcpy(blk, out, n * 4);
	c->pdsv[SGXFIVE_TRI_PV_MTE / 4 + 1] = sgxfive_tri_doutd(n);
	c->gen[SGXFIVE_TRI_G_VDM / 4 + 1] = (c->gen[SGXFIVE_TRI_G_VDM / 4 + 1] & ~VDM_ATTR_ROWS) |
					    n / 4;
	move[1] |= 0xfu << (REPEAT_SHIFT - 32);
	return 0;
}

static void put_copies(const struct sgxfive_tri_cpu *c, const struct sgxfive_tri_layout *l,
		       const struct sgxfive_tri_params *p, uint32_t n, bool depth, bool idx32)
{
	const bool big = n * 16 > SGXFIVE_TRI_G_IDX - SGXFIVE_TRI_G_VTX;
	const bool wide = n > SGXFIVE_TRI_PROBE_MAX_VERTICES;
	const uint32_t vat = wide ? SGXFIVE_TRI_PROBE_W_VTX :
			     big ? SGXFIVE_TRI_PROBE_G_VTX : SGXFIVE_TRI_G_VTX;
	const uint32_t iat = wide ? SGXFIVE_TRI_PROBE_W_IDX :
			     big ? SGXFIVE_TRI_PROBE_G_IDX : SGXFIVE_TRI_G_IDX;
	uint32_t *v = c->gen + vat / 4, *idx = c->gen + iat / 4;
	uint32_t *vdm = c->gen + SGXFIVE_TRI_G_VDM / 4;

	if (big) {
		memcpy(v, c->gen + SGXFIVE_TRI_G_VTX / 4, 3 * 16);
		c->pdsv[SGXFIVE_TRI_PV_VTX / 4] = l->gen + vat;
		vdm[3] = l->gen + iat;
	}
	for (uint32_t i = 3; i < n; i++) {
		const int32_t d = (int32_t)(i / 3);

		v[4 * i] = ndc(p->v[i % 3][0] + d, p->width);
		v[4 * i + 1] = ndc(p->v[i % 3][1] + d, p->height);
		v[4 * i + 2] = depth ? sgxfive_f32((float)d / 16.0f) : 0;
		v[4 * i + 3] = sgxfive_f32(1.0f);
	}
	if (idx32) {
		for (uint32_t i = 0; i < n; i++)
			idx[i] = i;
		vdm[2] |= SGXFIVE_TRI_PROBE_VDM_INDEX32;
	} else {
		for (uint32_t i = 0; i < n; i += 2)
			idx[i / 2] = i | (i + 1 < n ? (i + 1) << 16 : 0);
	}
	vdm[2] = (vdm[2] & ~VDM_INDEX_COUNT) | n;
}

/*
 * The coordsize word for n coordinate dwords: one 3-bit field per set from bit 0 (1 x, 2 xy,
 * 3 xyz, 4 xyw, 5 xyzw), as sets of four and then the rest.
 */
static uint32_t coordsize(uint32_t n)
{
	uint32_t w = 0;

	for (unsigned int shift = 0; n; shift += 3, n -= n > 4 ? 4 : n)
		w |= (n >= 4 ? 5u : n) << shift;
	return w;
}

/*
 * obj2: the copies from pr->obj2_first on as a second object. Its state block is the first's
 * as built (the rows the VDM state copies), with obj2's words set and the primary pixel
 * pointer its own pds_prim's, which starts obj2_pixel (or the default fill); its pds_mte copies
 * that block; the VDM stream gets its state and an index list of the rest of the vertices
 * after the first object's, which keeps the first obj2_first.
 */
static int put_obj2(const struct sgxfive_tri_cpu *c, const struct sgxfive_tri_layout *l,
		    const struct sgxfive_tri_probe *pr)
{
	const struct sgxfive_tri_prog *g = &pr->obj2_pixel;
	const struct sgxfive_tri_prog *pp2 = &pr->obj2_pixpds;
	const struct imm_base ib = { pr->scratch, l->fb };
	const uint32_t first = pr->obj2_first, n = pr->vertices;
	uint32_t *vdm = c->gen + SGXFIVE_TRI_G_VDM / 4;
	const uint32_t words = (vdm[1] & VDM_ATTR_ROWS) * 4;
	const uint32_t *blk = c->pdsv + SGXFIVE_TRI_PV_BLOCK / 4;
	uint32_t *blk2 = c->gen + SGXFIVE_TRI_PROBE_G_BLK2 / 4;
	uint32_t *mte2 = c->pdsv + SGXFIVE_TRI_PROBE_PV_MTE2 / 4;
	uint32_t *prim2 = c->pdsp + SGXFIVE_TRI_PROBE_PP_PRIM2 / 4;
	uint16_t *idx2 = (uint16_t *)(c->gen + SGXFIVE_TRI_PROBE_G_IDX2 / 4);
	const struct sgxfive_tri_prog *pp = &pr->slot[SGXFIVE_TRI_SLOT_PIXPDS];
	/* object 1's primary pointer: the default's, or the pixpds slot's */
	const uint32_t pri = pp->n ? sgxfive_tri_pix_ptr(l, l->pdsp + SGXFIVE_TRI_PROBE_PP_PIXPDS,
							 pp->data)
				   : sgxfive_tri_pix_ptr(l, l->pdsp + SGXFIVE_TRI_PP_PRIM, PRIM_DATA);
	uint32_t tail[3];

	if (first % 3 || first < 3 || first >= n || words > SGXFIVE_TRI_PROBE_BLK2_WORDS || pr->obj2_blk_mask >> words ||
	    (uint64_t)pr->slot[SGXFIVE_TRI_SLOT_PIXEL].n * 8 >
		    SGXFIVE_TRI_PROBE_UP_PIXEL2 - SGXFIVE_TRI_PROBE_UP_PIXEL ||
	    (uint64_t)g->n * 8 > SGXFIVE_TRI_PROBE_UP_PIXTASK - SGXFIVE_TRI_PROBE_UP_PIXEL2 ||
	    (g->n && g->temps > USE_MAX_TEMPS) ||
	    (pp2->n && ((uint64_t)pp2->n * 4 > SGXFIVE_TRI_PROBE_PP_PIXPDS - SGXFIVE_TRI_PROBE_PP_PRIM2 ||
			pp2->data % 4 || pp2->data < 4 || pp2->data > PDS_MAX_DATA || pp2->n <= pp2->data)))
		return -EINVAL;

	/* the block: the first's, the caller's words, its own primary */
	for (uint32_t i = 0; i < words; i++) {
		blk2[i] = pr->obj2_blk_mask >> i & 1 ? pr->obj2_blk_val[i] : blk[i];
		if (!(pr->obj2_blk_mask >> i & 1) && blk2[i] == pri)
			blk2[i] = sgxfive_tri_pix_ptr(l, l->pdsp + SGXFIVE_TRI_PROBE_PP_PRIM2,
						      pp2->n ? pp2->data : PRIM_DATA);
	}
	if (pp2->n && !(pr->obj2_blk_mask >> 4 & 1))
		blk2[4] = SGXFIVE_TRI_PROBE_PIX_ROWS | 3u << 16;
	memcpy(mte2, c->pdsv + SGXFIVE_TRI_PV_MTE / 4, SGXFIVE_TRI_PV_EOS - SGXFIVE_TRI_PV_MTE);
	mte2[0] = l->gen + SGXFIVE_TRI_PROBE_G_BLK2;

	/* the primary and the pixel shader */
	memcpy(prim2, c->pdsp + SGXFIVE_TRI_PP_PRIM / 4, SGXFIVE_TRI_PP_BGPRIM - SGXFIVE_TRI_PP_PRIM);
	if (g->n) {
		const uint32_t at = l->usep + SGXFIVE_TRI_PROBE_UP_PIXEL2;
		uint32_t *pw = put_usse(c->usep, SGXFIVE_TRI_PROBE_UP_PIXEL2, g, &ib);
		const uint64_t i0 = get_insn(pw, 0);

		if ((i0 & PHAS_MASK) == PHAS_VAL && (i0 & PHAS_NEXT))
			set_insn(pw, 0, i0 + (at - l->usep_base) / 8);
		prim2[0] = sgxfive_tri_doutu(at, l->usep_base, 0, temps(SGXFIVE_TRI_SLOT_PIXEL, g));
	} else {
		prim2[0] = sgxfive_tri_doutu(l->usep + SGXFIVE_TRI_UP_FILL, l->usep_base, 0, 0);
	}

	if (pp2->n) {
		/* the caller's primary: its U0 and U1 the shader's, as the default's */
		const uint32_t u0 = prim2[0], u1 = prim2[1];

		put_pds(c->pdsp, SGXFIVE_TRI_PROBE_PP_PRIM2, pp2, NULL, 0, &ib);
		prim2[0] = u0;
		prim2[1] = u1;
	}

	/* the index list and the VDM stream: object 1, object 2, end of scene, terminate */
	for (uint32_t i = first; i < n; i++)
		idx2[i - first] = (uint16_t)i;
	memcpy(tail, vdm + 8, sizeof(tail));
	vdm[2] = (vdm[2] & ~VDM_INDEX_COUNT) | first;
	vdm[8] = (vdm[0] & 0xf0000000u) | (((l->pdsv + SGXFIVE_TRI_PROBE_PV_MTE2) >> 4) & 0x0fffffff);
	vdm[9] = vdm[1];
	memcpy(vdm + 10, vdm + 2, 6 * 4);
	vdm[10] = (vdm[2] & ~VDM_INDEX_COUNT) | (n - first);
	vdm[11] = l->gen + SGXFIVE_TRI_PROBE_G_IDX2;
	memcpy(vdm + 16, tail, sizeof(tail));
	return 0;
}

int sgxfive_tri_probe_apply(const struct sgxfive_tri_cpu *c, const struct sgxfive_tri_layout *l,
			    const struct sgxfive_tri_params *p, const struct sgxfive_tri_probe *pr,
			    struct drm_sgxfive_render_cmd *cmd)
{
	static const uint32_t pixev_keep[] = { 0, 1, 2, 3, 4, 5, 12, SGXFIVE_TRI_PROBE_PIXTASK_U0 };
	static const uint32_t vtxpds_keep[] = { 0, 1, 2, 4 };
	const struct sgxfive_tri_prog *s = pr->slot;
	const struct imm_base ib = { pr->scratch, l->fb };
	uint32_t *pixev = c->pdsp + SGXFIVE_TRI_PP_PIXEV / 4;
	uint32_t *vtxpds = c->pdsv + SGXFIVE_TRI_PV_VTX / 4;
	uint32_t *vdm = c->gen + SGXFIVE_TRI_G_VDM / 4;
	uint32_t *w;

	for (unsigned int i = 0; i < SGXFIVE_TRI_SLOT_COUNT; i++)
		if (check(i, &s[i]))
			return -EINVAL;
	if (pr->obj2_pixpds.n && !pr->obj2_first)
		return -EINVAL;
	if (pr->vertices % 3 || pr->vertices > SGXFIVE_TRI_PROBE_WIDE_VERTICES ||
	    (pr->vertices > SGXFIVE_TRI_PROBE_MAX_VERTICES &&
	     (pr->obj2_first || c->gen_size < SGXFIVE_TRI_PROBE_GEN_PAGES * SGXFIVE_PAGE_SIZE)))
		return -EINVAL;
	if (pr->coords > OUTSEL_VTX_SIZE_MAX - 4 ||
	    (pr->blk_mask | pr->blk_xor_mask) >> SGXFIVE_TRI_BLOCK_WORDS ||
	    (pr->cmd_mask | pr->cmd_xor_mask) >> SGXFIVE_TRI_PROBE_CMD_WORDS ||
	    (pr->vdm_mask | pr->vdm_xor_mask) >> (pr->obj2_first ? SGXFIVE_TRI_PROBE_VDM2_WORDS :
						  SGXFIVE_TRI_VDM_WORDS))
		return -EINVAL;
	if (pr->coords) {
		uint32_t *blk = c->pdsv + SGXFIVE_TRI_PV_BLOCK / 4;

		blk[BLK_OUTSEL] = (blk[BLK_OUTSEL] & ~OUTSEL_VTX_SIZE) | (4 + pr->coords) << 16;
		blk[BLK_COORDSIZE] = coordsize(pr->coords);
		/* the vertex task's output size, in rows of four dwords */
		vdm[7] = (vdm[7] & ~VDM_OUTPUT_SIZE) | (4 + pr->coords + 3) / 4 << 24;
	}

	if ((pr->index_width && pr->index_width != 16 && pr->index_width != 32) ||
	    (pr->index_width == 32 &&
	     (pr->obj2_first || pr->vertices > SGXFIVE_TRI_PROBE_MAX_VERTICES)))
		return -EINVAL;
	if (pr->vertices > 3 || pr->index_width == 32)
		put_copies(c, l, p, pr->vertices > 3 ? pr->vertices : 3, pr->copy_depth,
			   pr->index_width == 32);

	if (s[SGXFIVE_TRI_SLOT_EOT].n) {
		const struct sgxfive_tri_prog *g = &s[SGXFIVE_TRI_SLOT_EOT];
		const struct sgxfive_rect r = { 0, 0, p->width, p->height };
		uint32_t pbe[SGXFIVE_PBE_WORDS];

		/* as render.c's put_eot */
		sgxfive_pbe(pbe, &r, 4 * p->width, l->fb);
		w = put_usse(c->usep, SGXFIVE_TRI_PROBE_UP_EOT, g, &ib);
		for (unsigned int i = 0; i < 4; i++)
			set_insn(w, 1 + i, sgxfive_limm_set(get_insn(w, 1 + i) + ((uint64_t)i << 21),
							    pbe[i]));
		set_insn(w, g->n - 1, sgxfive_emitpix_sb_set(get_insn(w, g->n - 1),
							       pr->sideband_set ? pr->sideband : pbe[4]));
		pixev[3] = sgxfive_tri_doutu(l->usep + SGXFIVE_TRI_PROBE_UP_EOT, l->usep_base, 0,
					     temps(SGXFIVE_TRI_SLOT_EOT, g));
	}
	if (pr->pbe_mask) {
		/* the end-of-tile task's four PBE words are the immediates of its instructions 1-4 */
		uint32_t *w = c->usep + (s[SGXFIVE_TRI_SLOT_EOT].n ? SGXFIVE_TRI_PROBE_UP_EOT :
					 SGXFIVE_TRI_UP_EOT) / 4;

		for (unsigned int i = 0; i < 4; i++)
			if (pr->pbe_mask >> i & 1)
				set_insn(w, 1 + i, sgxfive_limm_set(get_insn(w, 1 + i), pr->pbe_val[i]));
	}
	if (s[SGXFIVE_TRI_SLOT_BGPIXEL].n || s[SGXFIVE_TRI_SLOT_BGPDS].n) {
		const struct sgxfive_tri_prog *u = &s[SGXFIVE_TRI_SLOT_BGPIXEL];
		const struct sgxfive_tri_prog *g = &s[SGXFIVE_TRI_SLOT_BGPDS];
		uint32_t *prim = c->pdsp + SGXFIVE_TRI_PP_BGPRIM / 4;

		if (u->n) {
			const uint32_t at = l->usep + SGXFIVE_TRI_PROBE_UP_BGPIXEL;
			uint32_t *pw = put_usse(c->usep, SGXFIVE_TRI_PROBE_UP_BGPIXEL, u, &ib);
			const uint64_t i0 = get_insn(pw, 0);

			if ((i0 & PHAS_MASK) == PHAS_VAL && (i0 & PHAS_NEXT))
				set_insn(pw, 0, i0 + (at - l->usep_base) / 8);
			prim[0] = sgxfive_tri_doutu(at, l->usep_base, 0,
						    temps(SGXFIVE_TRI_SLOT_BGPIXEL, u));
		}
		if (g->n) {
			const uint32_t at = SGXFIVE_TRI_PROBE_PP_BGPDS;
			uint32_t *dst = c->pdsp + at / 4;

			/* the shader's U0 and U1, as the default background primary has them */
			put_pds(c->pdsp, at, g, NULL, 0, &ib);
			dst[0] = prim[0];
			dst[1] = prim[1];
			cmd->bgobj_words[1] = SGXFIVE_TRI_PROBE_PIX_ROWS | 3u << 16;
			cmd->bgobj_words[2] = sgxfive_tri_pix_ptr(l, l->pdsp + at, g->data);
		}
	}
	if (s[SGXFIVE_TRI_SLOT_PIXTASK].n) {
		const struct sgxfive_tri_prog *g = &s[SGXFIVE_TRI_SLOT_PIXTASK];

		w = put_usse(c->usep, SGXFIVE_TRI_PROBE_UP_PIXTASK, g, &ib);
		/*
		 * A plain task the pixel-event program starts hung on hardware at any
		 * place but the PTOFF program's: that program becomes its phas and a br
		 * to the pixtask, past the pixtask's own phas.
		 */
		{
			const uint32_t from = SGXFIVE_TRI_UP_PTOFF + 8;
			uint32_t to = SGXFIVE_TRI_PROBE_UP_PIXTASK;

			if ((get_insn(w, 0) & PHAS_MASK) == PHAS_VAL)
				to += 8;
			set_insn(c->usep + SGXFIVE_TRI_UP_PTOFF / 4, 1,
				 BR_VAL | ((to - from) / 8 & BR_OFFSET));
		}
		pixev[0] = sgxfive_tri_doutu(l->usep + SGXFIVE_TRI_UP_PTOFF, l->usep_base, 0,
					     temps(SGXFIVE_TRI_SLOT_PIXTASK, g));
		pixev[SGXFIVE_TRI_PROBE_PIXTASK_U0] =
			sgxfive_tri_doutu(l->usep + SGXFIVE_TRI_PROBE_UP_PIXTASK, l->usep_base, 0,
					  temps(SGXFIVE_TRI_SLOT_PIXTASK, g));
	}
	if (s[SGXFIVE_TRI_SLOT_PIXEV].n) {
		const struct sgxfive_tri_prog *g = &s[SGXFIVE_TRI_SLOT_PIXEV];

		/* dword 11 stays the caller's unless the pixtask slot put its U0 there */
		put_pds(c->pdsp, SGXFIVE_TRI_PP_PIXEV, g, pixev_keep,
			s[SGXFIVE_TRI_SLOT_PIXTASK].n ? 8 : 7, &ib);
		cmd->event_pixel_pds_data = g->data / 4;
		/*
		 * 0 [HW]: with any of bits 5:0 set douta does not reach the task's
		 * sa0-sa127, which hold its 16 x 8 block's colours; with them clear
		 * it writes there.
		 */
		cmd->event_pixel_pds_info = 0;
	}
	if (s[SGXFIVE_TRI_SLOT_VTXUSE].n) {
		const struct sgxfive_tri_prog *g = &s[SGXFIVE_TRI_SLOT_VTXUSE];
		const uint32_t at = l->usev + SGXFIVE_TRI_PROBE_UV_VTX;
		uint64_t i0;

		w = put_usse(c->usev, SGXFIVE_TRI_PROBE_UV_VTX, g, &ib);
		/* as render.c's put_vertex_programs, for a two-phase program */
		i0 = get_insn(w, 0);
		if ((i0 & PHAS_MASK) == PHAS_VAL && (i0 & PHAS_NEXT))
			set_insn(w, 0, i0 + (at - l->usev_base) / 8);
		vtxpds[4] = sgxfive_tri_doutu(at, l->usev_base, SGXFIVE_TRI_USEV_CBASE,
					      temps(SGXFIVE_TRI_SLOT_VTXUSE, g));
	}
	if (s[SGXFIVE_TRI_SLOT_STATE].n) {
		const struct sgxfive_tri_prog *g = &s[SGXFIVE_TRI_SLOT_STATE];

		put_usse(c->usev, SGXFIVE_TRI_UV_MTE18, g, &ib);
		c->pdsv[SGXFIVE_TRI_PV_MTE / 4 + 4] =
			sgxfive_tri_doutu(l->usev + SGXFIVE_TRI_UV_MTE18, l->usev_base,
					  SGXFIVE_TRI_USEV_CBASE, temps(SGXFIVE_TRI_SLOT_STATE, g));
	}
	if (s[SGXFIVE_TRI_SLOT_VTXPDS].n) {
		const struct sgxfive_tri_prog *g = &s[SGXFIVE_TRI_SLOT_VTXPDS];
		const uint32_t at = l->pdsv + SGXFIVE_TRI_PROBE_PV_VTX;
		uint32_t *dst = c->pdsv + SGXFIVE_TRI_PROBE_PV_VTX / 4;

		for (unsigned int k = 0; k < 4; k++)
			dst[vtxpds_keep[k]] = vtxpds[vtxpds_keep[k]];
		put_pds(c->pdsv, SGXFIVE_TRI_PROBE_PV_VTX, g, vtxpds_keep, 4, &ib);
		vdm[6] = (vdm[6] & 0xf0000000u) | ((at >> 4) & 0x0fffffff);
		vdm[7] = (vdm[7] & ~VDM_DATA_ROWS) | g->data / 4;
	}
	if (s[SGXFIVE_TRI_SLOT_PIXEL].n) {
		const struct sgxfive_tri_prog *g = &s[SGXFIVE_TRI_SLOT_PIXEL];

		const uint32_t at = l->usep + SGXFIVE_TRI_PROBE_UP_PIXEL;
		uint32_t *pw = put_usse(c->usep, SGXFIVE_TRI_PROBE_UP_PIXEL, g, &ib);
		const uint64_t i0 = get_insn(pw, 0);

		/* a two-phase shader, as the vtxuse slot's: its next phase from the code base */
		if ((i0 & PHAS_MASK) == PHAS_VAL && (i0 & PHAS_NEXT))
			set_insn(pw, 0, i0 + (at - l->usep_base) / 8);
		c->pdsp[SGXFIVE_TRI_PP_PRIM / 4] =
			sgxfive_tri_doutu(l->usep + SGXFIVE_TRI_PROBE_UP_PIXEL, l->usep_base, 0,
					  temps(SGXFIVE_TRI_SLOT_PIXEL, g));
	}
	if (s[SGXFIVE_TRI_SLOT_PIXPDS].n) {
		const struct sgxfive_tri_prog *g = &s[SGXFIVE_TRI_SLOT_PIXPDS];
		const uint32_t at = SGXFIVE_TRI_PROBE_PP_PIXPDS;
		uint32_t *blk = c->pdsv + SGXFIVE_TRI_PV_BLOCK / 4;

		/* the pixel shader's U0 and U1, as the default primary has them */
		put_pds(c->pdsp, at, g, NULL, 0, &ib);
		c->pdsp[at / 4] = c->pdsp[SGXFIVE_TRI_PP_PRIM / 4];
		c->pdsp[at / 4 + 1] = c->pdsp[SGXFIVE_TRI_PP_PRIM / 4 + 1];
		blk[4] = SGXFIVE_TRI_PROBE_PIX_ROWS | 3u << 16;
		blk[5] = sgxfive_tri_pix_ptr(l, l->pdsp + at, g->data);
	}
	if (pr->isp2_set) {
		uint32_t *blk = c->pdsv + SGXFIVE_TRI_PV_BLOCK / 4;

		/* the wrap word (12) makes room: words 3-11 move on by one */
		memmove(blk + BLK_ISP2 + 1, blk + BLK_ISP2, (BLK_WRAP - BLK_ISP2) * 4);
		blk[BLK_ISP2] = pr->isp2;
		blk[0] = (blk[0] & ~PRESENT_WRAP) | PRESENT_ISP2;
		blk[1] |= ISP0_ISP2_PRESENT;
	}
	if (pr->add_mask && (s[SGXFIVE_TRI_SLOT_STATE].n || add_words(c, pr)))
		return -EINVAL;
	if (pr->blk_mask) {
		uint32_t *blk = c->pdsv + SGXFIVE_TRI_PV_BLOCK / 4;

		/* last, after coords and pixpds: the caller's words win */
		for (unsigned int i = 0; i < SGXFIVE_TRI_BLOCK_WORDS; i++)
			if (pr->blk_mask >> i & 1)
				blk[i] = pr->blk_val[i];
	}
	if (pr->blk_xor_mask) {
		uint32_t *blk = c->pdsv + SGXFIVE_TRI_PV_BLOCK / 4;

		for (unsigned int i = 0; i < SGXFIVE_TRI_BLOCK_WORDS; i++)
			if (pr->blk_xor_mask >> i & 1)
				blk[i] ^= pr->blk_xor_val[i];
	}
	for (unsigned int i = 0; i < SGXFIVE_TRI_PROBE_CMD_WORDS; i++) {
		if (pr->cmd_mask >> i & 1)
			((uint32_t *)cmd)[i] = pr->cmd_val[i];
		if (pr->cmd_xor_mask >> i & 1)
			((uint32_t *)cmd)[i] ^= pr->cmd_xor_val[i];
	}
	/* the second object copies the first's state and stream words: the stream is set after it */
	if (pr->obj2_first && put_obj2(c, l, pr))
		return -EINVAL;
	for (unsigned int i = 0; i < SGXFIVE_TRI_PROBE_VDM2_WORDS; i++) {
		if (pr->vdm_mask >> i & 1)
			vdm[i] = pr->vdm_val[i];
		if (pr->vdm_xor_mask >> i & 1)
			vdm[i] ^= pr->vdm_xor_val[i];
	}
	return 0;
}

/* ---- The probe engine ----------------------------------------------------------------- */

enum { PG_PDSV, PG_USEV, PG_PDSP, PG_USEP, PG_GEN, PG_COUNT };

static const uint32_t page_heap[PG_COUNT] = {
	DRM_SGXFIVE_HEAP_PDS_VERTEX, DRM_SGXFIVE_HEAP_USSE_VERTEX, DRM_SGXFIVE_HEAP_PDS_PIXEL,
	DRM_SGXFIVE_HEAP_USSE_PIXEL, DRM_SGXFIVE_HEAP_GENERAL,
};

int sgxfive_tri_rig_create(struct sgxfive_vm *vm, uint32_t ctx, uint32_t max_w, uint32_t max_h,
			   struct sgxfive_tri_rig **out)
{
	struct sgxfive_dev *dev = sgxfive_vm_dev(vm);
	const struct sgxfive_info *info = sgxfive_dev_info(dev);
	struct sgxfive_tri_rig *g;
	uint64_t addr[PG_COUNT] = { 0 };
	void *map = NULL, *fb = NULL;
	int ret;

	if (!max_w || !max_h || max_w > SGXFIVE_TRI_MAX_W || max_h > SGXFIVE_TRI_MAX_H)
		return -EINVAL;
	g = calloc(1, sizeof(*g));
	if (!g)
		return -ENOMEM;
	g->vm = vm;
	g->dev = dev;
	g->ctx = ctx;
	/* the target and a guard page after it, whole pages */
	g->fb_size = ((uint64_t)max_w * max_h * 4 + 2 * SGXFIVE_PAGE_SIZE - 1) &
		     ~(uint64_t)(SGXFIVE_PAGE_SIZE - 1);
	ret = sgxfive_bo_create(dev, (PG_COUNT - 1 + SGXFIVE_TRI_PROBE_GEN_PAGES) * SGXFIVE_PAGE_SIZE,
				DRM_SGXFIVE_BO_ALLOW_CPU_ACCESS, &g->bo);
	if (!ret)
		ret = sgxfive_bo_mmap(g->bo, &map);
	for (int i = 0; !ret && i < PG_COUNT; i++) {
		/* the gen region, the last, has the extra pages of a wide scene after its page */
		const uint64_t size = (i == PG_GEN ? SGXFIVE_TRI_PROBE_GEN_PAGES : 1) *
				      SGXFIVE_PAGE_SIZE;

		ret = sgxfive_vm_alloc(vm, page_heap[i], size, SGXFIVE_PAGE_SIZE, &addr[i]);
		if (!ret)
			ret = sgxfive_vm_map(vm, addr[i], g->bo, (uint64_t)i * SGXFIVE_PAGE_SIZE,
					     size, 0);
		if (ret)
			addr[i] = 0;
	}
	if (!ret)
		ret = sgxfive_bo_create(dev, g->fb_size, DRM_SGXFIVE_BO_ALLOW_CPU_ACCESS,
					&g->fb_bo);
	if (!ret)
		ret = sgxfive_bo_mmap(g->fb_bo, &fb);
	if (!ret)
		ret = sgxfive_vm_alloc(vm, DRM_SGXFIVE_HEAP_GENERAL, g->fb_size, SGXFIVE_PAGE_SIZE,
				       &g->fb_addr);
	if (!ret)
		ret = sgxfive_vm_map(vm, g->fb_addr, g->fb_bo, 0, g->fb_size, 0);
	if (ret)
		g->fb_addr = 0;
	if (!ret)
		ret = sgxfive_syncobj_create(dev, false, &g->done);
	if (map) {
		uint32_t *m = map;

		g->cpu = (struct sgxfive_tri_cpu){
			m, m + SGXFIVE_PAGE_SIZE / 4, m + 2 * SGXFIVE_PAGE_SIZE / 4,
			m + 3 * SGXFIVE_PAGE_SIZE / 4, m + 4 * SGXFIVE_PAGE_SIZE / 4,
			SGXFIVE_TRI_PROBE_GEN_PAGES * SGXFIVE_PAGE_SIZE,
		};
	}
	g->fb = fb;
	g->layout = (struct sgxfive_tri_layout){
		.pdsv = (uint32_t)addr[PG_PDSV], .usev = (uint32_t)addr[PG_USEV],
		.pdsp = (uint32_t)addr[PG_PDSP], .usep = (uint32_t)addr[PG_USEP],
		.gen = (uint32_t)addr[PG_GEN], .fb = (uint32_t)g->fb_addr,
		.pds_exec_base = (uint32_t)info->heaps[DRM_SGXFIVE_HEAP_PDS_PIXEL].base,
		.usep_base = (uint32_t)info->heaps[DRM_SGXFIVE_HEAP_USSE_PIXEL].base,
		.usev_base = (uint32_t)info->heaps[DRM_SGXFIVE_HEAP_USSE_VERTEX].base,
	};
	if (ret) {
		sgxfive_tri_rig_destroy(g);
		return ret;
	}
	*out = g;
	return 0;
}

void sgxfive_tri_rig_destroy(struct sgxfive_tri_rig *g)
{
	const uint32_t pages[PG_COUNT] = {
		g ? g->layout.pdsv : 0, g ? g->layout.usev : 0, g ? g->layout.pdsp : 0,
		g ? g->layout.usep : 0, g ? g->layout.gen : 0,
	};

	if (!g)
		return;
	if (g->pending)
		sgxfive_tri_rig_wait(g, 10LL * 1000000000LL);
	for (int i = 0; i < PG_COUNT; i++)
		if (pages[i])
			sgxfive_vm_unmap(g->vm, pages[i], i == PG_GEN ?
					 SGXFIVE_TRI_PROBE_GEN_PAGES * SGXFIVE_PAGE_SIZE :
					 SGXFIVE_PAGE_SIZE);
	if (g->fb_addr)
		sgxfive_vm_unmap(g->vm, g->fb_addr, g->fb_size);
	if (g->done)
		sgxfive_syncobj_destroy(g->dev, g->done);
	sgxfive_bo_destroy(g->fb_bo);
	sgxfive_bo_destroy(g->bo);
	free(g);
}

int sgxfive_tri_rig_build(struct sgxfive_tri_rig *g, const struct sgxfive_tri_params *p,
			  const struct sgxfive_tri_probe *pr)
{
	int ret;

	if (g->pending)
		return -EBUSY;
	if ((uint64_t)p->width * p->height * 4 + SGXFIVE_PAGE_SIZE > g->fb_size)
		return -EINVAL;
	ret = sgxfive_tri_scene(&g->cpu, &g->layout, p, &g->cmd);
	if (!ret && pr)
		ret = sgxfive_tri_probe_apply(&g->cpu, &g->layout, p, pr, &g->cmd);
	if (ret)
		return ret;
	g->params = *p;
	for (uint64_t i = 0; i < g->fb_size / 4; i++)
		g->fb[i] = SGXFIVE_TRI_SENTINEL;
	return 0;
}

int sgxfive_tri_rig_submit(struct sgxfive_tri_rig *g)
{
	int ret;

	if (g->pending)
		return -EBUSY;
	ret = sgxfive_submit_render(g->dev, g->ctx, &g->cmd, 0, g->done);
	if (!ret)
		g->pending = true;
	return ret;
}

int sgxfive_tri_rig_wait(struct sgxfive_tri_rig *g, int64_t timeout_ns)
{
	int ret, job_error;

	if (!g->pending)
		return 0;
	ret = sgxfive_syncobj_wait_job(g->dev, g->done, 0, timeout_ns, &job_error);
	if (!ret)
		g->pending = false;
	return ret ? ret : job_error;
}
