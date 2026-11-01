// SPDX-License-Identifier: MIT
/*
 * Probe programs in the first triangle's render (sgxfive_tri_probe.h): the
 * slot names, each replacement placed and patched as its default is, the
 * scene unchanged without replacements, the sizes refused, and the probe
 * engine rendering on the mock, which faults a render whose tasks are not
 * mapped.
 */
#include <errno.h>
#include <stdlib.h>
#include <string.h>

#include "sgxfive_mock.h"
#include "sgxfive_tri_probe.h"
#include "tap.h"

#define PAGE		SGXFIVE_PAGE_SIZE
#define NSEC		1000000000LL

/* Pages and layout of a scene at made-up addresses (the default heap bases). */
struct scene {
	uint32_t *mem;
	struct sgxfive_tri_cpu c;
	struct sgxfive_tri_layout l;
	struct sgxfive_tri_params p;
	struct drm_sgxfive_render_cmd cmd;
};

static void scene_init(struct scene *s, uint32_t w, uint32_t h)
{
	s->mem = calloc(5, PAGE);
	s->c = (struct sgxfive_tri_cpu){ s->mem, s->mem + PAGE / 4, s->mem + 2 * PAGE / 4,
					 s->mem + 3 * PAGE / 4, s->mem + 4 * PAGE / 4 };
	s->l = (struct sgxfive_tri_layout){
		.pdsv = 0x30400000, .usev = 0x3c000000, .pdsp = 0x2e000000, .usep = 0x37000000,
		.gen = 0x3e000000, .fb = 0x3e001000, .pds_exec_base = 0x2e000000,
		.usep_base = 0x37000000, .usev_base = 0x3c000000,
	};
	sgxfive_tri_default(&s->p, w, h);
	CHECK_EQ(sgxfive_tri_scene(&s->c, &s->l, &s->p, &s->cmd), 0);
}

static uint64_t insn(const uint32_t *page, uint32_t off)
{
	return page[off / 4] | (uint64_t)page[off / 4 + 1] << 32;
}

static void slot_names(void)
{
	static const char *const names[] = { "pixev", "eot", "vtxpds", "vtxuse", "pixel", "pixtask",
					      "pixpds", "state" };

	for (int i = 0; i < SGXFIVE_TRI_SLOT_COUNT; i++) {
		CHECK_EQ(sgxfive_tri_slot_find(names[i]), i);
		CHECK(!strcmp(sgxfive_tri_slot_name(i), names[i]));
	}
	CHECK_EQ(sgxfive_tri_slot_find("bogus"), -1);
	CHECK_EQ(sgxfive_tri_slot_find(""), -1);
	CHECK(sgxfive_tri_slot_is_pds(SGXFIVE_TRI_SLOT_PIXEV));
	CHECK(sgxfive_tri_slot_is_pds(SGXFIVE_TRI_SLOT_VTXPDS));
	CHECK(!sgxfive_tri_slot_is_pds(SGXFIVE_TRI_SLOT_EOT));
	CHECK(!sgxfive_tri_slot_is_pds(SGXFIVE_TRI_SLOT_VTXUSE));
	CHECK(!sgxfive_tri_slot_is_pds(SGXFIVE_TRI_SLOT_PIXEL));
	CHECK(!sgxfive_tri_slot_is_pds(SGXFIVE_TRI_SLOT_PIXTASK));
	CHECK(sgxfive_tri_slot_is_pds(SGXFIVE_TRI_SLOT_PIXPDS));
	CHECK(!sgxfive_tri_slot_is_pds(SGXFIVE_TRI_SLOT_STATE));
}

/*
 * pixtask: a plain USE task for the pixel-event program to kick (no PBE), at
 * SGXFIVE_TRI_PROBE_UP_PIXTASK with its scratch immediates; its U0 goes to the
 * pixel-event program's data dword 11, replaced or not.
 */
static void pixtask_slot(void)
{
	struct scene s;
	struct sgxfive_tri_probe pr = { .scratch = 0x3e100000 };
	const uint32_t at = SGXFIVE_TRI_PROBE_UP_PIXTASK;
	uint64_t w[2] = { 0xfa44070000000000ull, 0 };
	uint64_t pix[20];

	scene_init(&s, 64, 64);
	w[1] = sgxfive_limm_set(insn(s.c.usep, SGXFIVE_TRI_UP_FILL + 8),
				SGXFIVE_TRI_PROBE_SCRATCH_IMM | 0x20);
	pr.slot[SGXFIVE_TRI_SLOT_PIXTASK] = (struct sgxfive_tri_prog){ w, 2, 0, 8 };
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	CHECK_EQ(insn(s.c.usep, at), w[0]);
	CHECK_EQ(sgxfive_limm_get(insn(s.c.usep, at + 8)), 0x3e100020);
	CHECK_EQ(s.c.pdsp[SGXFIVE_TRI_PP_PIXEV / 4 + 11],
		 sgxfive_tri_doutu(s.l.usep + at, s.l.usep_base, 0, 8));
	/* a replaced pixel-event program gets it too, over its own dword 11 */
	for (unsigned int i = 0; i < 20; i++)
		pix[i] = 0xdead0000u | i;
	pr.slot[SGXFIVE_TRI_SLOT_PIXEV] = (struct sgxfive_tri_prog){ pix, 20, 16, 0 };
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	CHECK_EQ(s.c.pdsp[SGXFIVE_TRI_PP_PIXEV / 4 + 11],
		 sgxfive_tri_doutu(s.l.usep + at, s.l.usep_base, 0, 8));
	CHECK_EQ(s.c.pdsp[SGXFIVE_TRI_PP_PIXEV / 4 + 10], 0xdead000au);
	/*
	 * a plain task the pixel-event program starts runs only at the PTOFF
	 * program's place: the PTOFF program becomes its phas and a br to the
	 * pixtask's second instruction (past its own phas)
	 */
	CHECK_EQ(insn(s.c.usep, SGXFIVE_TRI_UP_PTOFF), 0xfa44070000000000ull);
	CHECK_EQ(insn(s.c.usep, SGXFIVE_TRI_UP_PTOFF + 8),
		 0xF800004000000000ull | (at + 8 - (SGXFIVE_TRI_UP_PTOFF + 8)) / 8);
	/* and the PTOFF task, now the pixtask, gets the pixtask's temporaries */
	CHECK_EQ(s.c.pdsp[SGXFIVE_TRI_PP_PIXEV / 4],
		 sgxfive_tri_doutu(s.l.usep + SGXFIVE_TRI_UP_PTOFF, s.l.usep_base, 0, 8));
	/* the pixel slot ends where pixtask starts */
	CHECK(SGXFIVE_TRI_PROBE_UP_PIXEL < at && at < SGXFIVE_TRI_PROBE_UP_EOT);
	free(s.mem);
}

/* No replacement: the scene stays the default's, byte for byte. */
static void no_replacement(void)
{
	struct scene a, b;
	const struct sgxfive_tri_probe pr = { .scratch = 0x3e100000 };

	scene_init(&a, 64, 64);
	scene_init(&b, 64, 64);
	CHECK_EQ(sgxfive_tri_probe_apply(&b.c, &b.l, &b.p, &pr, &b.cmd), 0);
	CHECK(!memcmp(a.mem, b.mem, 5 * PAGE));
	CHECK(!memcmp(&a.cmd, &b.cmd, sizeof(a.cmd)));
	free(a.mem);
	free(b.mem);
}

static void pixev(void)
{
	struct scene d, s;
	struct sgxfive_tri_probe pr = { 0 };
	uint64_t w[40];
	const uint32_t *got;

	for (int i = 0; i < 40; i++)
		w[i] = 0xa0000000u | i;
	scene_init(&d, 64, 64);
	scene_init(&s, 64, 64);
	pr.slot[SGXFIVE_TRI_SLOT_PIXEV] = (struct sgxfive_tri_prog){ w, 40, 24, 0 };
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	got = s.c.pdsp + SGXFIVE_TRI_PP_PIXEV / 4;
	for (int i = 0; i < 40; i++) {
		const bool patched = i <= 5 || i == 12;
		const uint32_t want = patched ? d.c.pdsp[SGXFIVE_TRI_PP_PIXEV / 4 + i] :
					      (uint32_t)w[i];

		if (!CHECK_EQ(got[i], want))
			printf("#   dword %d\n", i);
	}
	CHECK_EQ(s.cmd.event_pixel_pds_exec, d.cmd.event_pixel_pds_exec);
	CHECK_EQ(s.cmd.event_pixel_pds_data, 6);
	CHECK_EQ(s.cmd.event_pixel_pds_info, 0);		/* douta reaches the task */
	/* the rest of the command is the default's */
	s.cmd.event_pixel_pds_data = d.cmd.event_pixel_pds_data;
	s.cmd.event_pixel_pds_info = d.cmd.event_pixel_pds_info;
	CHECK(!memcmp(&s.cmd, &d.cmd, sizeof(d.cmd)));
	free(d.mem);
	free(s.mem);
}

static void eot(void)
{
	struct scene d, s;
	struct sgxfive_tri_probe pr = { .scratch = 0x3e100000 };
	const uint32_t at = SGXFIVE_TRI_PROBE_UP_EOT;
	uint64_t w[8];

	scene_init(&d, 64, 64);
	scene_init(&s, 64, 64);
	/* use_eot.s with a scratch store address between: the defaults' words */
	for (int i = 0; i < 5; i++)
		w[i] = insn(d.c.usep, SGXFIVE_TRI_UP_EOT + 8 * i);
	w[5] = sgxfive_limm_set(w[1], SGXFIVE_TRI_PROBE_SCRATCH_IMM | 0x40);
	w[6] = insn(d.c.usep, SGXFIVE_TRI_UP_EOT + 8 * 5);	/* emitpix1 */
	w[7] = insn(d.c.usep, SGXFIVE_TRI_UP_EOT + 8 * 6);	/* emitpix2 */
	for (int i = 1; i <= 4; i++)		/* back to the template's r0, #0 */
		w[i] = sgxfive_limm_set(w[i] - ((uint64_t)(i - 1) << 21), 0);
	w[7] = sgxfive_emitpix_sb_set(w[7], 0);
	pr.slot[SGXFIVE_TRI_SLOT_EOT] = (struct sgxfive_tri_prog){ w, 8, 0, 8 };
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	for (int i = 0; i < 5; i++)
		CHECK_EQ(insn(s.c.usep, at + 8 * i), insn(d.c.usep, SGXFIVE_TRI_UP_EOT + 8 * i));
	CHECK_EQ(sgxfive_limm_get(insn(s.c.usep, at + 40)), 0x3e100040);
	CHECK_EQ(insn(s.c.usep, at + 48), insn(d.c.usep, SGXFIVE_TRI_UP_EOT + 40));
	CHECK_EQ(insn(s.c.usep, at + 56), insn(d.c.usep, SGXFIVE_TRI_UP_EOT + 48));
	/* the pixel-event program starts it, with its temporaries */
	CHECK_EQ(s.c.pdsp[SGXFIVE_TRI_PP_PIXEV / 4 + 3],
		 sgxfive_tri_doutu(s.l.usep + at, s.l.usep_base, 0, 8));
	CHECK_EQ(s.cmd.event_pixel_pds_info, 1);		/* the default pixev's */
	/* fewer temporaries than the default's four: the default's */
	pr.slot[SGXFIVE_TRI_SLOT_EOT].temps = 1;
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	CHECK_EQ(s.c.pdsp[SGXFIVE_TRI_PP_PIXEV / 4 + 3],
		 sgxfive_tri_doutu(s.l.usep + at, s.l.usep_base, 0, 4));
	free(d.mem);
	free(s.mem);
}

static void vtxpds(void)
{
	struct scene d, s;
	struct sgxfive_tri_probe pr = { 0 };
	const uint32_t at = SGXFIVE_TRI_PROBE_PV_VTX;
	uint64_t w[20];
	const uint32_t *vdm;

	for (int i = 0; i < 20; i++)
		w[i] = 0xb0000000u | i;
	scene_init(&d, 64, 64);
	scene_init(&s, 64, 64);
	pr.slot[SGXFIVE_TRI_SLOT_VTXPDS] = (struct sgxfive_tri_prog){ w, 20, 12, 0 };
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	for (int i = 0; i < 20; i++) {
		const bool patched = i <= 2 || i == 4;
		const uint32_t want = patched ? d.c.pdsv[SGXFIVE_TRI_PV_VTX / 4 + i] :
					      (uint32_t)w[i];

		if (!CHECK_EQ(s.c.pdsv[at / 4 + i], want))
			printf("#   dword %d\n", i);
	}
	vdm = s.c.gen + SGXFIVE_TRI_G_VDM / 4;
	CHECK_EQ(vdm[6], 15u << 28 | (s.l.pdsv + at) >> 4);
	CHECK_EQ(vdm[7] & 0x7f, 3);				/* data rows */
	CHECK_EQ(vdm[7] & ~0x7fu, d.c.gen[SGXFIVE_TRI_G_VDM / 4 + 7] & ~0x7fu);
	free(d.mem);
	free(s.mem);
}

static void vtxuse(void)
{
	struct scene d, s;
	struct sgxfive_tri_probe pr = { 0 };
	const uint32_t at = SGXFIVE_TRI_PROBE_UV_VTX;
	uint64_t w[9];

	scene_init(&d, 64, 64);
	scene_init(&s, 64, 64);
	/* use_vtx.s as assembled: phas #7 counted from the program's start */
	w[0] = 0xfa44020000000007ull;
	for (int i = 1; i < 9; i++)
		w[i] = 0xf800094000000000ull;
	pr.slot[SGXFIVE_TRI_SLOT_VTXUSE] = (struct sgxfive_tri_prog){ w, 9, 0, 12 };
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	CHECK_EQ(insn(s.c.usev, at), w[0] + (s.l.usev + at - s.l.usev_base) / 8);
	CHECK_EQ(insn(s.c.usev, at + 8), w[1]);
	CHECK_EQ(s.c.pdsv[SGXFIVE_TRI_PV_VTX / 4 + 4],
		 sgxfive_tri_doutu(s.l.usev + at, s.l.usev_base, SGXFIVE_TRI_USEV_CBASE, 12));
	/* a single-phase program (phas #0) is not renumbered */
	w[0] = 0xfa44070000000000ull;
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	CHECK_EQ(insn(s.c.usev, at), w[0]);
	/* with vtxpds replaced too, the replacement starts it */
	{
		uint64_t p[12] = { 0 };

		p[8] = 0xaf000000;
		pr.slot[SGXFIVE_TRI_SLOT_VTXPDS] = (struct sgxfive_tri_prog){ p, 9, 8, 0 };
		CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
		CHECK_EQ(s.c.pdsv[SGXFIVE_TRI_PROBE_PV_VTX / 4 + 4],
			 sgxfive_tri_doutu(s.l.usev + at, s.l.usev_base, SGXFIVE_TRI_USEV_CBASE,
					   12));
	}
	free(d.mem);
	free(s.mem);
}

/*
 * state: the triangle's state task (use_mtest18.s) replaced in its own place,
 * SGXFIVE_TRI_UV_MTE18, its DOUTU in the MTE PDS program given the slot's temporaries.
 */
static void state(void)
{
	struct scene s;
	struct sgxfive_tri_probe pr = { 0 };
	const uint32_t at = SGXFIVE_TRI_UV_MTE18;
	uint64_t w[3] = { 0xfa44070000000000ull, 0xf800014000000000ull, 0xf804014000000000ull };

	scene_init(&s, 64, 64);
	pr.slot[SGXFIVE_TRI_SLOT_STATE] = (struct sgxfive_tri_prog){ w, 3, 0, 8 };
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	for (int i = 0; i < 3; i++)
		CHECK_EQ(insn(s.c.usev, at + 8 * i), w[i]);
	CHECK_EQ(s.c.pdsv[SGXFIVE_TRI_PV_MTE / 4 + 4],
		 sgxfive_tri_doutu(s.l.usev + at, s.l.usev_base, SGXFIVE_TRI_USEV_CBASE, 8));
	/* blk_add patches use_mtest18's second move: not with the program replaced */
	pr.add_mask = 1u << 3;
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), -EINVAL);
	free(s.mem);
}

static void pixel(void)
{
	struct scene d, s;
	struct sgxfive_tri_probe pr = { .scratch = 0x3e100000 };
	const uint32_t at = SGXFIVE_TRI_PROBE_UP_PIXEL;
	uint64_t w[2] = { 0xfa44070000000000ull, 0 };

	scene_init(&d, 64, 64);
	scene_init(&s, 64, 64);
	w[1] = sgxfive_limm_set(insn(d.c.usep, SGXFIVE_TRI_UP_FILL + 8),
				SGXFIVE_TRI_PROBE_SCRATCH_IMM | 0x10);
	pr.slot[SGXFIVE_TRI_SLOT_PIXEL] = (struct sgxfive_tri_prog){ w, 2, 0, 16 };
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	CHECK_EQ(insn(s.c.usep, at), w[0]);
	CHECK_EQ(sgxfive_limm_get(insn(s.c.usep, at + 8)), 0x3e100010);
	CHECK_EQ(s.c.pdsp[SGXFIVE_TRI_PP_PRIM / 4],
		 sgxfive_tri_doutu(s.l.usep + at, s.l.usep_base, 0, 16));
	/* the background keeps its own */
	CHECK_EQ(s.c.pdsp[SGXFIVE_TRI_PP_BGPRIM / 4], d.c.pdsp[SGXFIVE_TRI_PP_BGPRIM / 4]);
	/* without a scratch address the immediate stays */
	pr.scratch = 0;
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	CHECK_EQ(sgxfive_limm_get(insn(s.c.usep, at + 8)), SGXFIVE_TRI_PROBE_SCRATCH_IMM | 0x10);
	/* a two-phase shader (phas #N, N > 0, from the program's start) is renumbered from the
	 * pixel code base, as the vtxuse slot's (a punch-through shader's pt phase, say) */
	w[0] = 0xfa44010000000003ull;
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	CHECK_EQ(insn(s.c.usep, at), w[0] + (s.l.usep + at - s.l.usep_base) / 8);
	free(d.mem);
	free(s.mem);
}

/*
 * pixpds: the triangle's primary pixel PDS program at SGXFIVE_TRI_PROBE_PP_PIXPDS, data
 * dwords 0 and 1 the pixel shader's U0 and U1 (the pixel slot's, or the default fill's), the
 * state block's primary pointer and size word repointed at it with
 * SGXFIVE_TRI_PROBE_PIX_ROWS rows of primary attributes; the background keeps its own.
 */
static void pixpds(void)
{
	struct scene d, s;
	struct sgxfive_tri_probe pr = { 0 };
	const uint32_t at = SGXFIVE_TRI_PROBE_PP_PIXPDS;
	uint64_t w[12], pix[2] = { 0xfa44070000000000ull, 0xf804014000000000ull };
	const uint32_t *blk;

	for (int i = 0; i < 12; i++)
		w[i] = 0xc0000000u | i;
	scene_init(&d, 64, 64);
	scene_init(&s, 64, 64);
	pr.slot[SGXFIVE_TRI_SLOT_PIXPDS] = (struct sgxfive_tri_prog){ w, 12, 8, 0 };
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	CHECK_EQ(s.c.pdsp[at / 4], d.c.pdsp[SGXFIVE_TRI_PP_PRIM / 4]);	/* the fill's U0 */
	CHECK_EQ(s.c.pdsp[at / 4 + 1], 4);
	for (int i = 2; i < 12; i++)
		if (!CHECK_EQ(s.c.pdsp[at / 4 + i], (uint32_t)w[i]))
			printf("#   dword %d\n", i);
	blk = s.c.pdsv + SGXFIVE_TRI_PV_BLOCK / 4;
	CHECK_EQ(blk[5], sgxfive_tri_pix_ptr(&s.l, s.l.pdsp + at, 8));
	CHECK_EQ(blk[4], SGXFIVE_TRI_PROBE_PIX_ROWS | 3u << 16);
	CHECK_EQ(s.cmd.bgobj_words[2], d.cmd.bgobj_words[2]);
	/* a data dword SGXFIVE_TRI_PROBE_SCRATCH_IMM | k loads scratch + k, as the USSE
	 * immediates do (a texture's address, say); code dwords and other data stay */
	w[6] = SGXFIVE_TRI_PROBE_SCRATCH_IMM | 0x40;
	w[9] = SGXFIVE_TRI_PROBE_SCRATCH_IMM | 0x80;	/* code: not patched */
	pr.scratch = 0x3e100000;
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	CHECK_EQ(s.c.pdsp[at / 4 + 6], 0x3e100040);
	CHECK_EQ(s.c.pdsp[at / 4 + 9], SGXFIVE_TRI_PROBE_SCRATCH_IMM | 0x80);
	CHECK_EQ(s.c.pdsp[at / 4 + 7], (uint32_t)w[7]);
	/* with the pixel slot replaced too, its U0 */
	pr.slot[SGXFIVE_TRI_SLOT_PIXEL] = (struct sgxfive_tri_prog){ pix, 2, 0, 0 };
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	CHECK_EQ(s.c.pdsp[at / 4], sgxfive_tri_doutu(s.l.usep + SGXFIVE_TRI_PROBE_UP_PIXEL,
						     s.l.usep_base, 0, 0));
	free(d.mem);
	free(s.mem);
}

/*
 * coords: N more output dwords per vertex after the position, texture coordinate sets: the
 * state block's OUTSEL vertex size (bits 19:16) 4 + N, its coordsize word one 3-bit field per
 * set (sets of four components, 5, then the rest: 1 x, 2 xy, 3 xyz), and the vertex task's
 * output size (VDM word 7, bits 31:24) in rows of four dwords.
 */
static void coords(void)
{
	struct scene d, s;
	struct sgxfive_tri_probe pr = { .coords = 2 };
	const uint32_t *blk, *dblk;

	scene_init(&d, 64, 64);
	scene_init(&s, 64, 64);
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	blk = s.c.pdsv + SGXFIVE_TRI_PV_BLOCK / 4;
	dblk = d.c.pdsv + SGXFIVE_TRI_PV_BLOCK / 4;
	CHECK_EQ((dblk[13] >> 16) & 0xf, 4);
	CHECK_EQ(blk[13], (dblk[13] & ~0xf0000u) | (4 + 2) << 16);
	CHECK_EQ(blk[16], 2);				/* one set, xy */
	CHECK_EQ(s.c.gen[SGXFIVE_TRI_G_VDM / 4 + 7] >> 24, (4 + 2 + 3) / 4);
	CHECK_EQ(s.c.gen[SGXFIVE_TRI_G_VDM / 4 + 7] & 0xffffffu,
		 d.c.gen[SGXFIVE_TRI_G_VDM / 4 + 7] & 0xffffffu);
	CHECK_EQ(d.c.gen[SGXFIVE_TRI_G_VDM / 4 + 7] >> 24, 1);
	for (int i = 0; i < SGXFIVE_TRI_BLOCK_WORDS; i++)
		if (i != 13 && i != 16 && !CHECK_EQ(blk[i], dblk[i]))
			printf("#   block word %d\n", i);
	/* sets of four (5) and the rest, one 3-bit field each from bit 0 */
	for (unsigned int i = 0; i < 4; i++) {
		static const uint32_t n[] = { 3, 4, 6, 11 },
			want[] = { 3, 5, 5 | 2 << 3, 5 | 5 << 3 | 3 << 6 };

		pr.coords = n[i];
		CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
		if (!CHECK_EQ(blk[16], want[i]))
			printf("#   %u coordinates\n", n[i]);
	}
	pr.coords = 13;		/* the vertex size field holds 15 at most */
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), -EINVAL);
	free(d.mem);
	free(s.mem);
}

/*
 * isp2: the state block carries ISP word 2 (stencil) in place of the wrap word, keeping its 18
 * words: presence bit 2 set and bit 9 clear, ISP0 bit 8 (ISP word 2 present), the word at 3
 * and the pixel programs and viewport one word on; OUTSEL and
 * the words after it stay. --blk words index the new layout.
 */
static void isp2(void)
{
	struct scene d, s;
	struct sgxfive_tri_probe pr = { .isp2_set = true, .isp2 = 0x0e0200ff };
	const uint32_t *blk, *dblk;

	scene_init(&d, 64, 64);
	scene_init(&s, 64, 64);
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	blk = s.c.pdsv + SGXFIVE_TRI_PV_BLOCK / 4;
	dblk = d.c.pdsv + SGXFIVE_TRI_PV_BLOCK / 4;
	CHECK_EQ(dblk[0], 0xdf43);
	CHECK_EQ(blk[0], 0xdd47);
	CHECK_EQ(blk[1], dblk[1] | 0x100);
	CHECK_EQ(blk[2], dblk[2]);
	CHECK_EQ(blk[3], 0x0e0200ff);
	CHECK_EQ(dblk[12], 0);			/* the wrap word it replaces */
	for (int i = 4; i <= 12; i++)
		if (!CHECK_EQ(blk[i], dblk[i - 1]))
			printf("#   block word %d\n", i);
	for (int i = 13; i < SGXFIVE_TRI_BLOCK_WORDS; i++)
		if (!CHECK_EQ(blk[i], dblk[i]))
			printf("#   block word %d\n", i);
	/* the caller's words index the new layout */
	pr.blk_mask = 1u << 3;
	pr.blk_val[3] = 0x12345678;
	free(s.mem);
	scene_init(&s, 64, 64);
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	blk = s.c.pdsv + SGXFIVE_TRI_PV_BLOCK / 4;
	CHECK_EQ(blk[3], 0x12345678);
	free(d.mem);
	free(s.mem);
}

/*
 * blk_add: presence bits the default block lacks (2-5 one word each, 7 two), their words
 * inserted in bit order; the block padded with zeros to whole rows of four and the state copy
 * grown with it: the doutd word, the VDM state's attribute rows and use_mtest18's second
 * move (repeat16, 32 dwords). --blk words index the grown layout. A bit already present, one
 * outside 2-5 and 7, refused.
 */
static void blk_add(void)
{
	struct scene d, s;
	struct sgxfive_tri_probe pr = { .add_mask = 1u << 3 | 1u << 5 };
	const uint32_t *blk, *dblk;

	scene_init(&d, 64, 64);
	scene_init(&s, 64, 64);
	pr.add_val[3][0] = 0x33333333;
	pr.add_val[5][0] = 0x55555555;
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	blk = s.c.pdsv + SGXFIVE_TRI_PV_BLOCK / 4;
	dblk = d.c.pdsv + SGXFIVE_TRI_PV_BLOCK / 4;
	CHECK_EQ(blk[0], 0xdf6b);
	CHECK_EQ(blk[1], dblk[1]);
	CHECK_EQ(blk[2], dblk[2]);
	CHECK_EQ(blk[3], 0x33333333);
	CHECK_EQ(blk[4], 0x55555555);
	for (int i = 3; i < SGXFIVE_TRI_BLOCK_WORDS; i++)
		if (!CHECK_EQ(blk[i + 2], dblk[i]))
			printf("#   block word %d\n", i + 2);
	CHECK_EQ(s.c.pdsv[SGXFIVE_TRI_PV_MTE / 4 + 1], sgxfive_tri_doutd(20));
	CHECK_EQ(s.c.gen[SGXFIVE_TRI_G_VDM / 4 + 1] & 0xff, 5);
	CHECK_EQ(d.c.gen[SGXFIVE_TRI_G_VDM / 4 + 1] & 0xff, 5);	/* 18 dwords: 5 rows too */
	CHECK_EQ(insn(d.c.usev, SGXFIVE_TRI_UV_MTE18 + 6 * 8), 0x28a11001a2000800ull);
	CHECK_EQ(insn(s.c.usev, SGXFIVE_TRI_UV_MTE18 + 6 * 8), 0x28a1f001a2000800ull);
	free(s.mem);

	/* bits 3 and 7 (two words): 21 dwords, padded to 24 */
	pr = (struct sgxfive_tri_probe){ .add_mask = 1u << 3 | 1u << 7, .add_val[3] = { 3 },
					 .add_val[7] = { 7, 8 } };
	scene_init(&s, 64, 64);
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	blk = s.c.pdsv + SGXFIVE_TRI_PV_BLOCK / 4;
	CHECK_EQ(blk[0], 0xdfcb);
	CHECK_EQ(blk[3], 3);
	CHECK_EQ(blk[4], dblk[3]);
	CHECK_EQ(blk[7], 7);
	CHECK_EQ(blk[8], 8);
	CHECK_EQ(blk[9], dblk[6]);
	CHECK_EQ(blk[20], dblk[17]);
	CHECK_EQ(blk[21], 0);
	CHECK_EQ(blk[23], 0);
	CHECK_EQ(s.c.pdsv[SGXFIVE_TRI_PV_MTE / 4 + 1], sgxfive_tri_doutd(24));
	CHECK_EQ(s.c.gen[SGXFIVE_TRI_G_VDM / 4 + 1] & 0xff, 6);
	free(s.mem);

	/* with isp2 (bit 2 in place of the wrap word) and a --blk word of the grown layout */
	pr = (struct sgxfive_tri_probe){ .isp2_set = true, .isp2 = 0x0e0200ff,
					 .add_mask = 1u << 3, .add_val[3] = { 0x33333333 },
					 .blk_mask = 1u << 4, .blk_val[4] = 0x44444444 };
	scene_init(&s, 64, 64);
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	blk = s.c.pdsv + SGXFIVE_TRI_PV_BLOCK / 4;
	CHECK_EQ(blk[0], 0xdd4f);
	CHECK_EQ(blk[3], 0x0e0200ff);
	CHECK_EQ(blk[4], 0x44444444);
	CHECK_EQ(blk[5], dblk[3]);
	free(s.mem);

	for (unsigned int bit = 0; bit < 16; bit++) {
		if ((bit >= 2 && bit <= 5) || bit == 7)
			continue;
		pr = (struct sgxfive_tri_probe){ .add_mask = 1u << bit };
		scene_init(&s, 64, 64);
		if (!CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), -EINVAL))
			printf("#   presence bit %u\n", bit);
		free(s.mem);
	}
	pr = (struct sgxfive_tri_probe){ .isp2_set = true, .add_mask = 1u << 2 };
	scene_init(&s, 64, 64);
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), -EINVAL);
	free(s.mem);
	free(d.mem);
}

static void refused(void)
{
	static uint64_t w[1024];
	static const struct { unsigned int slot; uint32_t n, data, temps; } bad[] = {
		{ SGXFIVE_TRI_SLOT_PIXEV, 30, 12, 0 },	/* data too short for dword 12 */
		{ SGXFIVE_TRI_SLOT_PIXEV, 30, 18, 0 },	/* not whole rows */
		{ SGXFIVE_TRI_SLOT_PIXEV, 20, 20, 0 },	/* no code */
		{ SGXFIVE_TRI_SLOT_PIXEV, 200, 132, 0 },	/* more than 128 data dwords */
		{ SGXFIVE_TRI_SLOT_PIXEV,
		  (SGXFIVE_TRI_PROBE_PP_PIXPDS - SGXFIVE_TRI_PP_PIXEV) / 4 + 1, 20, 0 },
		{ SGXFIVE_TRI_SLOT_PIXPDS, 6, 0, 0 },	/* no data for U0 and U1 */
		{ SGXFIVE_TRI_SLOT_PIXPDS, (PAGE - SGXFIVE_TRI_PROBE_PP_PIXPDS) / 4 + 1, 4, 0 },
		{ SGXFIVE_TRI_SLOT_VTXPDS, 10, 4, 0 },	/* data too short for dword 4 */
		{ SGXFIVE_TRI_SLOT_VTXPDS, (PAGE - SGXFIVE_TRI_PROBE_PV_VTX) / 4 + 1, 8, 0 },
		{ SGXFIVE_TRI_SLOT_EOT, 4, 0, 8 },	/* no emitpix after the PBE words */
		{ SGXFIVE_TRI_SLOT_EOT, (PAGE - SGXFIVE_TRI_PROBE_UP_EOT) / 8 + 1, 0, 8 },
		{ SGXFIVE_TRI_SLOT_PIXEL,
		  (SGXFIVE_TRI_PROBE_UP_PIXTASK - SGXFIVE_TRI_PROBE_UP_PIXEL) / 8 + 1, 0, 8 },
		{ SGXFIVE_TRI_SLOT_PIXTASK,
		  (SGXFIVE_TRI_PROBE_UP_EOT - SGXFIVE_TRI_PROBE_UP_PIXTASK) / 8 + 1, 0, 8 },
		{ SGXFIVE_TRI_SLOT_VTXUSE, (PAGE - SGXFIVE_TRI_PROBE_UV_VTX) / 8 + 1, 0, 8 },
		{ SGXFIVE_TRI_SLOT_VTXUSE, 4, 0, 129 },	/* too many temporaries */
		{ SGXFIVE_TRI_SLOT_STATE,
		  (SGXFIVE_TRI_UV_MTE2 - SGXFIVE_TRI_UV_MTE18) / 8 + 1, 0, 8 },
	};
	struct scene s;

	scene_init(&s, 64, 64);
	for (size_t i = 0; i < sizeof(bad) / sizeof(bad[0]); i++) {
		struct sgxfive_tri_probe pr = { 0 };

		pr.slot[bad[i].slot] = (struct sgxfive_tri_prog){ w, bad[i].n, bad[i].data,
								   bad[i].temps };
		if (!CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), -EINVAL))
			printf("#   case %zu\n", i);
	}
	/* the largest that fit */
	{
		struct sgxfive_tri_probe pr = { 0 };

		pr.slot[SGXFIVE_TRI_SLOT_PIXEV] = (struct sgxfive_tri_prog){
			w, (SGXFIVE_TRI_PROBE_PP_PIXPDS - SGXFIVE_TRI_PP_PIXEV) / 4, 128, 0 };
		pr.slot[SGXFIVE_TRI_SLOT_PIXPDS] = (struct sgxfive_tri_prog){
			w, (PAGE - SGXFIVE_TRI_PROBE_PP_PIXPDS) / 4, 128, 0 };
		pr.slot[SGXFIVE_TRI_SLOT_PIXEL] = (struct sgxfive_tri_prog){
			w, (SGXFIVE_TRI_PROBE_UP_PIXTASK - SGXFIVE_TRI_PROBE_UP_PIXEL) / 8, 0, 128 };
		pr.slot[SGXFIVE_TRI_SLOT_PIXTASK] = (struct sgxfive_tri_prog){
			w, (SGXFIVE_TRI_PROBE_UP_EOT - SGXFIVE_TRI_PROBE_UP_PIXTASK) / 8, 0, 128 };
		CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	}
	free(s.mem);
}

/* ---- The probe engine on the mock --------------------------------------------------- */

struct env {
	struct sgxfive_mock *mock;
	struct sgxfive_dev *dev;
	struct sgxfive_vm *vm;
	uint32_t ctx;
	struct sgxfive_tri_rig *g;
};

static void env_init(struct env *e, uint32_t w, uint32_t h)
{
	const struct sgxfive_mock_config cfg = { .layout = SGXFIVE_MOCK_LAYOUT_REV1 };

	memset(e, 0, sizeof(*e));
	e->mock = sgxfive_mock_create(&cfg);
	CHECK_EQ(sgxfive_dev_open(sgxfive_mock_backend(e->mock), NULL, &e->dev), 0);
	CHECK_EQ(sgxfive_vm_create(e->dev, &e->vm), 0);
	CHECK_EQ(sgxfive_render_ctx_create(e->vm, w, h, &e->ctx), 0);
	CHECK_EQ(sgxfive_tri_rig_create(e->vm, e->ctx, w, h, &e->g), 0);
}

static void env_fini(struct env *e)
{
	sgxfive_tri_rig_destroy(e->g);
	sgxfive_ctx_destroy(e->dev, e->ctx);
	sgxfive_vm_destroy(e->vm);
	sgxfive_dev_close(e->dev);
	sgxfive_mock_destroy(e->mock);
}

/* The default scene through the probe engine draws the first triangle. */
static void rig_default(void)
{
	static const uint32_t sizes[][2] = { { 64, 64 }, { 32, 16 }, { 32, 4096 } };

	for (size_t k = 0; k < sizeof(sizes) / sizeof(sizes[0]); k++) {
		struct sgxfive_tri_counts n;
		struct sgxfive_tri_params p;
		struct env e;

		env_init(&e, sizes[k][0], sizes[k][1]);
		sgxfive_tri_default(&p, sizes[k][0], sizes[k][1]);
		CHECK_EQ(sgxfive_tri_rig_build(e.g, &p, NULL), 0);
		CHECK_EQ(e.g->fb[0], SGXFIVE_TRI_SENTINEL);
		CHECK_EQ(sgxfive_tri_rig_submit(e.g), 0);
		CHECK_EQ(sgxfive_tri_rig_submit(e.g), -EBUSY);
		CHECK_EQ(sgxfive_tri_rig_wait(e.g, 5 * NSEC), 0);
		CHECK_EQ(sgxfive_tri_check(&p, e.g->fb, &n), 0);
		CHECK_EQ(e.g->fb[(uint64_t)p.width * p.height], SGXFIVE_TRI_SENTINEL);
		env_fini(&e);
	}
	{
		struct sgxfive_tri_params p;
		struct env e;

		env_init(&e, 64, 64);
		sgxfive_tri_default(&p, 128, 64);		/* beyond the rig's buffer */
		CHECK_EQ(sgxfive_tri_rig_build(e.g, &p, NULL), -EINVAL);
		env_fini(&e);
	}
}

/* Every slot replaced by a copy of its default: the same image. */
static void rig_every_slot(void)
{
	struct scene d;
	struct sgxfive_tri_probe pr = { 0 };
	struct sgxfive_tri_counts n;
	uint64_t pixev[64], vtxpds[16], eot[7], vtxuse[9], pix[2], pixpds[6];
	struct env e;

	scene_init(&d, 64, 64);
	for (int i = 0; i < 64; i++)
		pixev[i] = d.c.pdsp[SGXFIVE_TRI_PP_PIXEV / 4 + i];
	for (int i = 0; i < 16; i++)
		vtxpds[i] = d.c.pdsv[SGXFIVE_TRI_PV_VTX / 4 + i];
	for (int i = 0; i < 7; i++)
		eot[i] = insn(d.c.usep, SGXFIVE_TRI_UP_EOT + 8 * i);
	for (int i = 1; i <= 4; i++)
		eot[i] = sgxfive_limm_set(eot[i] - ((uint64_t)(i - 1) << 21), 0);
	for (int i = 0; i < 9; i++)
		vtxuse[i] = insn(d.c.usev, SGXFIVE_TRI_UV_VTX + 8 * i);
	vtxuse[0] = 0xfa44020000000007ull;			/* as assembled */
	for (int i = 0; i < 2; i++)
		pix[i] = insn(d.c.usep, SGXFIVE_TRI_UP_FILL + 8 * i);
	for (int i = 0; i < 6; i++)
		pixpds[i] = d.c.pdsp[SGXFIVE_TRI_PP_PRIM / 4 + i];
	pr.slot[SGXFIVE_TRI_SLOT_PIXPDS] = (struct sgxfive_tri_prog){ pixpds, 6, 4, 0 };
	pr.slot[SGXFIVE_TRI_SLOT_PIXEV] = (struct sgxfive_tri_prog){ pixev, 52, 20, 0 };
	pr.slot[SGXFIVE_TRI_SLOT_VTXPDS] = (struct sgxfive_tri_prog){ vtxpds, 12, 8, 0 };
	pr.slot[SGXFIVE_TRI_SLOT_EOT] = (struct sgxfive_tri_prog){ eot, 7, 0, 4 };
	pr.slot[SGXFIVE_TRI_SLOT_VTXUSE] = (struct sgxfive_tri_prog){ vtxuse, 9, 0, 0 };
	pr.slot[SGXFIVE_TRI_SLOT_PIXEL] = (struct sgxfive_tri_prog){ pix, 2, 0, 0 };
	env_init(&e, 64, 64);
	CHECK_EQ(sgxfive_tri_rig_build(e.g, &d.p, &pr), 0);
	CHECK_EQ(sgxfive_tri_rig_submit(e.g), 0);
	CHECK_EQ(sgxfive_tri_rig_wait(e.g, 5 * NSEC), 0);
	CHECK_EQ(sgxfive_tri_check(&d.p, e.g->fb, &n), 0);
	CHECK_EQ(n.tri + n.bg, 64 * 64);
	env_fini(&e);
	free(d.mem);
}

/*
 * The mock faults a render whose vertex shader, PTOFF or end-of-render task
 * is not mapped (a wrong DOUTU word in a probe's scene), as it does one whose
 * end-of-tile program or pixel shaders are not.
 */
static void rig_unmapped_tasks(void)
{
	static const struct { int page; uint32_t dword; } words[] = {
		{ 0, SGXFIVE_TRI_PV_VTX / 4 + 4 },	/* the vertex shader's U0 */
		{ 2, SGXFIVE_TRI_PP_PIXEV / 4 + 0 },	/* the PTOFF task's U0 */
		{ 2, SGXFIVE_TRI_PP_PIXEV / 4 + 4 },	/* the end-of-render task's U0 */
		{ 2, SGXFIVE_TRI_PP_PIXEV / 4 + 3 },	/* the end-of-tile task's U0 */
	};

	for (size_t i = 0; i < sizeof(words) / sizeof(words[0]); i++) {
		struct sgxfive_tri_params p;
		struct env e;
		uint32_t *page;

		env_init(&e, 64, 64);
		sgxfive_tri_default(&p, 64, 64);
		CHECK_EQ(sgxfive_tri_rig_build(e.g, &p, NULL), 0);
		page = words[i].page == 0 ? e.g->cpu.pdsv : e.g->cpu.pdsp;
		/* instruction 0x8000 of its code base: 256 KiB on, nothing mapped there */
		page[words[i].dword] = (page[words[i].dword] & 0xff00000fu) | 0x8000u << 4;
		CHECK_EQ(sgxfive_tri_rig_submit(e.g), 0);
		if (!CHECK_EQ(sgxfive_tri_rig_wait(e.g, 5 * NSEC), -EIO))
			printf("#   word %zu\n", i);
		env_fini(&e);
	}
}

/*
 * vertices: copies of the triangle after it, so that the vertex programs run for more
 * vertices than one task's; copy c (vertices 3c-3c+2) is the first moved c/16 pixel
 * right and down, its vertices told apart by their x, the index list 0 to N-1.
 */
static void vertices(void)
{
	struct scene d, s;
	struct sgxfive_tri_probe pr = { .vertices = 9 };
	const uint32_t *v, *vdm;

	scene_init(&d, 64, 64);
	scene_init(&s, 64, 64);
	v = s.c.gen + SGXFIVE_TRI_G_VTX / 4;
	vdm = s.c.gen + SGXFIVE_TRI_G_VDM / 4;
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	CHECK_EQ(vdm[2], (d.c.gen[SGXFIVE_TRI_G_VDM / 4 + 2] & ~0x3fffffu) | 9);
	for (unsigned int i = 0; i < 9; i++) {
		const int32_t c = i / 3;

		CHECK_EQ(v[4 * i], sgxfive_f32((float)(s.p.v[i % 3][0] + c) / 512.0f - 1.0f));
		CHECK_EQ(v[4 * i + 1], sgxfive_f32((float)(s.p.v[i % 3][1] + c) / 512.0f - 1.0f));
		CHECK_EQ(v[4 * i + 2], 0);
		CHECK_EQ(v[4 * i + 3], sgxfive_f32(1.0f));
	}
	for (unsigned int i = 0; i < 9; i += 2)
		CHECK_EQ(s.c.gen[SGXFIVE_TRI_G_IDX / 4 + i / 2] & 0xffff, i);
	for (unsigned int i = 1; i < 9; i += 2)
		CHECK_EQ(s.c.gen[SGXFIVE_TRI_G_IDX / 4 + i / 2] >> 16, i);
	free(s.mem);
	/* 0 and 3: the one triangle, the scene unchanged */
	for (uint32_t n = 0; n <= 3; n += 3) {
		pr.vertices = n;
		scene_init(&s, 64, 64);
		CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
		CHECK(!memcmp(s.c.gen, d.c.gen, PAGE));
		free(s.mem);
	}
	/* not whole triangles, or more than the vertex buffer holds */
	for (uint32_t n = 1; n <= 18; n++) {
		if (n % 3 == 0 && n <= SGXFIVE_TRI_PROBE_MAX_VERTICES)
			continue;
		pr.vertices = n;
		scene_init(&s, 64, 64);
		if (!CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), -EINVAL))
			printf("#   %u vertices\n", n);
		free(s.mem);
	}
	pr.vertices = SGXFIVE_TRI_PROBE_MAX_VERTICES + 3;
	scene_init(&s, 64, 64);
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), -EINVAL);
	free(s.mem);
	CHECK_EQ(SGXFIVE_TRI_PROBE_MAX_VERTICES, 126);
	free(d.mem);
}

/*
 * copy_depth: copy c of the triangle (vertices 3c to 3c + 2) at clip-space z = c / 16, the
 * triangle itself at 0, so that the copies overlap at different depths.
 */
static void copy_depth(void)
{
	struct scene s;
	struct sgxfive_tri_probe pr = { .vertices = 12, .copy_depth = true };
	const uint32_t *v;

	scene_init(&s, 64, 64);
	v = s.c.gen + SGXFIVE_TRI_G_VTX / 4;
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	for (unsigned int i = 0; i < 12; i++)
		if (!CHECK_EQ(v[4 * i + 2], sgxfive_f32((float)(i / 3) / 16.0f)))
			printf("#   vertex %u\n", i);
	free(s.mem);
}

/*
 * More than 15 vertices: the vertex buffer and index list move to the scene page's spare
 * room (SGXFIVE_TRI_PROBE_G_VTX, _G_IDX), the vertex PDS and the VDM's index-list address
 * pointing there; the triangle's three vertices first, then the copies as with fewer.
 */
static void many_vertices(void)
{
	struct scene s;
	const uint32_t n = SGXFIVE_TRI_PROBE_MAX_VERTICES;
	struct sgxfive_tri_probe pr = { .vertices = n };
	const uint32_t *v, *idx, *vdm;

	scene_init(&s, 64, 64);
	v = s.c.gen + SGXFIVE_TRI_PROBE_G_VTX / 4;
	idx = s.c.gen + SGXFIVE_TRI_PROBE_G_IDX / 4;
	vdm = s.c.gen + SGXFIVE_TRI_G_VDM / 4;
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	CHECK_EQ(s.c.pdsv[SGXFIVE_TRI_PV_VTX / 4], s.l.gen + SGXFIVE_TRI_PROBE_G_VTX);
	CHECK_EQ(vdm[3], s.l.gen + SGXFIVE_TRI_PROBE_G_IDX);
	CHECK_EQ(vdm[2] & 0x3fffffu, n);
	for (unsigned int i = 0; i < n; i++) {
		const int32_t c = i / 3;

		if (!CHECK_EQ(v[4 * i], sgxfive_f32((float)(s.p.v[i % 3][0] + c) / 512.0f - 1.0f)) ||
		    !CHECK_EQ(v[4 * i + 3], sgxfive_f32(1.0f)) ||
		    !CHECK_EQ(idx[i / 2] >> (i % 2 * 16) & 0xffff, i))
			printf("#   vertex %u\n", i);
	}
	CHECK(SGXFIVE_TRI_PROBE_G_VTX + 16 * n <= SGXFIVE_TRI_PROBE_G_IDX);
	CHECK(SGXFIVE_TRI_PROBE_G_IDX + 2 * n <= PAGE);
	free(s.mem);
}

/*
 * cmd: words of the render command set as given (cmd_mask bit i: word i is cmd_val[i]),
 * after the other options; the rest as the default's.
 */
static void cmd_words(void)
{
	struct scene d, s;
	struct sgxfive_tri_probe pr = { .cmd_mask = 1u << 13 | 1u << 16 };
	const uint32_t *w = (const uint32_t *)&s.cmd, *dw = (const uint32_t *)&d.cmd;

	pr.cmd_val[13] = 0x80000002;
	pr.cmd_val[16] = 0xeaa26e26;
	scene_init(&d, 64, 64);
	scene_init(&s, 64, 64);
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	for (unsigned int i = 0; i < SGXFIVE_TRI_PROBE_CMD_WORDS; i++) {
		const uint32_t want = i == 13 ? 0x80000002 : i == 16 ? 0xeaa26e26 : dw[i];

		if (!CHECK_EQ(w[i], want))
			printf("#   command word %u\n", i);
	}
	CHECK_EQ(SGXFIVE_TRI_PROBE_CMD_WORDS * 4, DRM_SGXFIVE_RENDER_CMD_SIZE_V1);
	pr.cmd_mask = 1u << SGXFIVE_TRI_PROBE_CMD_WORDS;	/* past the command */
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), -EINVAL);
	free(d.mem);
	free(s.mem);
}

/*
 * blk: words of the triangle's state block set as given (blk_mask bit i: word i is
 * blk_val[i]), after the other options; the rest as the default's.
 */
static void blk_words(void)
{
	struct scene d, s;
	struct sgxfive_tri_probe pr = { .blk_mask = 1u << 1 | 1u << 10 };
	const uint32_t *blk, *dblk;

	pr.blk_val[1] = 0x00400200;
	pr.blk_val[10] = 0x3e99999a;
	scene_init(&d, 64, 64);
	scene_init(&s, 64, 64);
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	blk = s.c.pdsv + SGXFIVE_TRI_PV_BLOCK / 4;
	dblk = d.c.pdsv + SGXFIVE_TRI_PV_BLOCK / 4;
	for (int i = 0; i < SGXFIVE_TRI_BLOCK_WORDS; i++) {
		const uint32_t want = i == 1 ? 0x00400200 : i == 10 ? 0x3e99999a : dblk[i];

		if (!CHECK_EQ(blk[i], want))
			printf("#   block word %d\n", i);
	}
	pr.blk_mask = 1u << SGXFIVE_TRI_BLOCK_WORDS;	/* past the block */
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), -EINVAL);
	free(d.mem);
	free(s.mem);
}

/*
 * vdm: words of the triangle's VDM stream set as given (vdm_mask bit i: word i is
 * vdm_val[i]), after the other options (coords sets word 7); the rest as the default's.
 */
static void vdm_words(void)
{
	struct scene d, s;
	struct sgxfive_tri_probe pr = { .coords = 2, .vdm_mask = 1u << 4 | 1u << 7 };
	const uint32_t *vdm, *dvdm;

	pr.vdm_val[4] = 0xf4000000;
	pr.vdm_val[7] = 0x01c00083;
	scene_init(&d, 64, 64);
	scene_init(&s, 64, 64);
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	vdm = s.c.gen + SGXFIVE_TRI_G_VDM / 4;
	dvdm = d.c.gen + SGXFIVE_TRI_G_VDM / 4;
	for (int i = 0; i < SGXFIVE_TRI_VDM_WORDS; i++) {
		const uint32_t want = i == 4 ? 0xf4000000 : i == 7 ? 0x01c00083 : dvdm[i];

		if (!CHECK_EQ(vdm[i], want))
			printf("#   VDM word %d\n", i);
	}
	pr.vdm_mask = 1u << SGXFIVE_TRI_VDM_WORDS;	/* past the stream */
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), -EINVAL);
	free(d.mem);
	free(s.mem);
}

/*
 * vdm_xor: words of the VDM stream flipped by the given bits after the other options and the
 * set words (vdm_xor_mask bit i: word i ^= vdm_xor_val[i]).
 */
static void vdm_xor_words(void)
{
	struct scene d, s;
	struct sgxfive_tri_probe pr = { .vdm_xor_mask = 1u << 1 | 1u << 6 };
	const uint32_t *vdm, *dvdm;

	pr.vdm_xor_val[1] = 0x100;
	pr.vdm_xor_val[6] = 0x80000000;
	scene_init(&d, 64, 64);
	scene_init(&s, 64, 64);
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	vdm = s.c.gen + SGXFIVE_TRI_G_VDM / 4;
	dvdm = d.c.gen + SGXFIVE_TRI_G_VDM / 4;
	for (int i = 0; i < SGXFIVE_TRI_VDM_WORDS; i++) {
		const uint32_t want = dvdm[i] ^ (i == 1 ? 0x100 : i == 6 ? 0x80000000 : 0);

		if (!CHECK_EQ(vdm[i], want))
			printf("#   VDM word %d\n", i);
	}
	pr.vdm_xor_mask = 1u << SGXFIVE_TRI_VDM_WORDS;	/* past the stream */
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), -EINVAL);
	free(d.mem);
	free(s.mem);
}

/*
 * sideband: with sideband_set, the end-of-tile program's emitpix2 gets the given sideband
 * instead of the default's (0x200); without, the default's.
 */
static void eot_sideband(void)
{
	struct scene d, s;
	struct sgxfive_tri_probe pr = { .sideband_set = true, .sideband = 0x2240 };
	const uint32_t at = SGXFIVE_TRI_PROBE_UP_EOT;
	uint64_t w[7];

	scene_init(&d, 64, 64);
	scene_init(&s, 64, 64);
	for (int i = 0; i < 7; i++)
		w[i] = insn(d.c.usep, SGXFIVE_TRI_UP_EOT + 8 * i);
	pr.slot[SGXFIVE_TRI_SLOT_EOT] = (struct sgxfive_tri_prog){ w, 7, 0, 4 };
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	CHECK_EQ(insn(s.c.usep, at + 48), sgxfive_emitpix_sb_set(w[6], 0x2240));
	pr.sideband_set = false;
	free(s.mem);
	scene_init(&s, 64, 64);
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	CHECK_EQ(insn(s.c.usep, at + 48), sgxfive_emitpix_sb_set(w[6], 0x200));
	free(d.mem);
	free(s.mem);
}

/* The rig renders the copies (the mock draws every triangle of the index list). */
static void rig_vertices(void)
{
	struct sgxfive_tri_probe pr = { .vertices = SGXFIVE_TRI_PROBE_MAX_VERTICES };
	struct sgxfive_tri_params p;
	struct sgxfive_tri_counts n;
	struct env e;

	env_init(&e, 64, 64);
	sgxfive_tri_default(&p, 64, 64);
	CHECK_EQ(sgxfive_tri_rig_build(e.g, &p, &pr), 0);
	CHECK_EQ(sgxfive_tri_rig_submit(e.g), 0);
	CHECK_EQ(sgxfive_tri_rig_wait(e.g, 5 * NSEC), 0);
	sgxfive_tri_check(&p, e.g->fb, &n);
	CHECK_EQ(n.tri + n.bg, 64 * 64);
	CHECK(n.tri > 0);
	env_fini(&e);
}

/*
 * A second object: copies from vertex obj2_first on drawn with their own state block (the
 * first's as built, with obj2's words set and its primary pointing at its own pds_prim) and
 * pixel shader, after the first object in the VDM stream.
 */
static void obj2(void)
{
	struct scene d, s;
	struct sgxfive_tri_probe pr = { .vertices = 12, .obj2_first = 6 };
	uint64_t w[2] = { 0xfa44070000000000ull, 0 };
	const uint32_t *vdm, *b1, *b2, *mte2, *prim2;
	const uint16_t *idx2;

	scene_init(&d, 64, 64);
	scene_init(&s, 64, 64);
	w[1] = insn(d.c.usep, SGXFIVE_TRI_UP_FILL + 8);
	pr.obj2_blk_mask = 1u << 1;
	pr.obj2_blk_val[1] = 0x00400200;
	pr.obj2_pixel = (struct sgxfive_tri_prog){ w, 2, 0, 8 };
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	vdm = s.c.gen + SGXFIVE_TRI_G_VDM / 4;
	/* object 1: its state and the first six indices */
	CHECK_EQ(vdm[0], d.c.gen[SGXFIVE_TRI_G_VDM / 4]);
	CHECK_EQ(vdm[2] & 0xffff, 6);
	/* object 2: its state (pds_mte2), an index list of the other six at G_IDX2 */
	CHECK_EQ(vdm[8], 1u << 30 | ((s.l.pdsv + SGXFIVE_TRI_PROBE_PV_MTE2) >> 4));
	CHECK_EQ(vdm[9], vdm[1]);
	CHECK_EQ(vdm[10], (vdm[2] & ~0xffffu) | 6);
	CHECK_EQ(vdm[11], s.l.gen + SGXFIVE_TRI_PROBE_G_IDX2);
	for (int i = 12; i < 16; i++)
		CHECK_EQ(vdm[i], vdm[i - 8]);
	/* then the end of scene and terminate, moved on */
	CHECK_EQ(vdm[16], d.c.gen[SGXFIVE_TRI_G_VDM / 4 + 8]);
	CHECK_EQ(vdm[17], d.c.gen[SGXFIVE_TRI_G_VDM / 4 + 9]);
	CHECK_EQ(vdm[18], 3u << 30);
	idx2 = (const uint16_t *)(s.c.gen + SGXFIVE_TRI_PROBE_G_IDX2 / 4);
	for (int i = 0; i < 6; i++)
		CHECK_EQ(idx2[i], 6 + i);
	/* pds_mte2: pds_mte with the second block's address */
	mte2 = s.c.pdsv + SGXFIVE_TRI_PROBE_PV_MTE2 / 4;
	CHECK_EQ(mte2[0], s.l.gen + SGXFIVE_TRI_PROBE_G_BLK2);
	for (int i = 1; i < 16; i++)
		CHECK_EQ(mte2[i], s.c.pdsv[SGXFIVE_TRI_PV_MTE / 4 + i]);
	/* the second block: the first's, its ISP word 0 set, its primary its own */
	b1 = s.c.pdsv + SGXFIVE_TRI_PV_BLOCK / 4;
	b2 = s.c.gen + SGXFIVE_TRI_PROBE_G_BLK2 / 4;
	for (int i = 0; i < 20; i++)
		if (i != 1 && i != 5 && !CHECK_EQ(b2[i], b1[i]))
			printf("#   block word %d\n", i);
	CHECK_EQ(b2[1], 0x00400200);
	CHECK_EQ(b2[5], sgxfive_tri_pix_ptr(&s.l, s.l.pdsp + SGXFIVE_TRI_PROBE_PP_PRIM2, 4));
	CHECK_EQ(b1[5], d.c.pdsv[SGXFIVE_TRI_PV_BLOCK / 4 + 5]);
	/* its primary starts the obj2 pixel shader */
	prim2 = s.c.pdsp + SGXFIVE_TRI_PROBE_PP_PRIM2 / 4;
	CHECK_EQ(prim2[0], sgxfive_tri_doutu(s.l.usep + SGXFIVE_TRI_PROBE_UP_PIXEL2,
					     s.l.usep_base, 0, 8));
	CHECK_EQ(prim2[1], 4);
	CHECK_EQ(insn(s.c.usep, SGXFIVE_TRI_PROBE_UP_PIXEL2), w[0]);
	free(s.mem);

	/* without obj2_pixel, object 2 runs the default fill */
	pr.obj2_pixel.n = 0;
	scene_init(&s, 64, 64);
	CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
	CHECK_EQ(s.c.pdsp[SGXFIVE_TRI_PROBE_PP_PRIM2 / 4], d.c.pdsp[SGXFIVE_TRI_PP_PRIM / 4]);
	free(s.mem);

	/* with the pixpds slot, object 1's primary is that program: object 2 gets its own all
	 * the same (a punch-through scene feeds its pixels through pixpds) */
	{
		uint32_t pds[8] = { 0, 0, 0, 0, 0x07000000, 0, 0, 0 };
		uint64_t pdsw[8];

		for (int i = 0; i < 8; i++)
			pdsw[i] = pds[i];
		pr.slot[SGXFIVE_TRI_SLOT_PIXPDS] = (struct sgxfive_tri_prog){ pdsw, 8, 4, 0 };
		scene_init(&s, 64, 64);
		CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &pr, &s.cmd), 0);
		b1 = s.c.pdsv + SGXFIVE_TRI_PV_BLOCK / 4;
		b2 = s.c.gen + SGXFIVE_TRI_PROBE_G_BLK2 / 4;
		CHECK_EQ(b1[5], sgxfive_tri_pix_ptr(&s.l, s.l.pdsp + SGXFIVE_TRI_PROBE_PP_PIXPDS, 4));
		CHECK_EQ(b2[5], sgxfive_tri_pix_ptr(&s.l, s.l.pdsp + SGXFIVE_TRI_PROBE_PP_PRIM2, 4));
		free(s.mem);
		pr.slot[SGXFIVE_TRI_SLOT_PIXPDS].n = 0;
	}

	/* refused: not whole triangles, past the copies, a block word past the block, a pixel
	 * slot reaching UP_PIXEL2 */
	for (int k = 0; k < 5; k++) {
		struct sgxfive_tri_probe q = pr;
		uint64_t big[97] = { 0 };

		if (k == 0)
			q.obj2_first = 4;
		if (k == 1)
			q.obj2_first = 12;
		if (k == 2)
			q.obj2_first = 3 * 42;
		if (k == 3)
			q.obj2_blk_mask = 1u << 20;
		if (k == 4)
			q.slot[SGXFIVE_TRI_SLOT_PIXEL] = (struct sgxfive_tri_prog){ big, 97, 0, 0 };
		scene_init(&s, 64, 64);
		if (!CHECK_EQ(sgxfive_tri_probe_apply(&s.c, &s.l, &s.p, &q, &s.cmd), -EINVAL))
			printf("#   case %d\n", k);
		free(s.mem);
	}
	free(d.mem);
}

int main(void)
{
	slot_names();
	pixtask_slot();
	no_replacement();
	pixev();
	eot();
	vtxpds();
	vtxuse();
	state();
	pixel();
	pixpds();
	coords();
	isp2();
	blk_add();
	refused();
	rig_default();
	rig_every_slot();
	rig_unmapped_tasks();
	vertices();
	copy_depth();
	eot_sideband();
	many_vertices();
	cmd_words();
	blk_words();
	vdm_words();
	vdm_xor_words();
	rig_vertices();
	obj2();
	return tap_done();
}
