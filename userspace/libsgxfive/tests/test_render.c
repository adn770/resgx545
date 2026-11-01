// SPDX-License-Identifier: MIT
/*
 * The render builders (src/render.c) against the first triangle of the
 * kernel's debugfs test: at the same addresses they must produce the same
 * words as the kernel's triangle test (sgx_tri.c, which the linux fork gains
 * with the 3D unit; its KUnit tests pin those values),
 * and other sizes must move exactly the size-dependent words.
 */
#include <errno.h>
#include <stdlib.h>
#include <string.h>

#include "sgxfive_render.h"
#include "tap.h"

/*
 * The tiling words of a target, each field written out from the layout rule
 * of include/uapi/sgxfive_drm.h (struct drm_sgxfive_render_cmd): tx x ty tiles
 * of 32 x 16 pixels; n = 4 macrotiles across and down from 640 x 480 pixels
 * on, else 2; a macrotile of mx x my tiles, the tiles over n rounded up to a
 * multiple of 4. TE_MTILE1/2 hold m / 4 in 31:24 and two boundaries in tiles
 * in 19:12 and 11:0: 2m and 3m when n = 4, else m and m; TE_MTILE1 bit 31 when
 * n = 4. TE_MTILE is 16 per 4 x 4-tile block of a macrotile.
 */
#define MT2(m)	((m) / 4 << 24 | (m) << 12 | (m))
#define MT4(m)	((m) / 4 << 24 | 2 * (m) << 12 | 3 * (m))

static const struct sgxfive_tri_layout L = {
	.pdsv = 0x30401000, .usev = 0x3c001000, .pdsp = 0x2e001000, .usep = 0x37001000,
	.gen = 0x3e001000, .fb = 0x3e010000, .pds_exec_base = 0x2e000000,
	.usep_base = 0x37000000, .usev_base = 0x3c000000,
};

static uint64_t qw(const uint32_t *p, unsigned int insn)
{
	return p[2 * insn] | (uint64_t)p[2 * insn + 1] << 32;
}

static void test_words(void)
{
	CHECK_EQ(sgxfive_tri_doutu(0xfc008d80, 0xfc000000, 10, 0), 0x11b0a);
	CHECK_EQ(sgxfive_tri_doutu(0xf4000020, 0xf4000000, 0, 4), 0x01000040);
	CHECK_EQ(sgxfive_tri_pix_ptr(&L, 0x2e001040, 4), 0x04000104);
	CHECK_EQ(sgxfive_tri_doutd(12), 0x02c0000b);
	CHECK_EQ(sgxfive_tri_doutd(18), 0x02000018);
	CHECK_EQ(sgxfive_tri_doutd(2), 0x00400001);
	CHECK_EQ(sgxfive_f32(-0.75f), 0xbf400000);
	CHECK_EQ(sgxfive_f32(32.0f), 0x42000000);
}

static void test_default(void)
{
	struct sgxfive_tri_params p;

	sgxfive_tri_default(&p, 64, 64);
	CHECK_EQ(p.width, 64);
	CHECK_EQ(p.v[0][0], 8 * 16);
	CHECK_EQ(p.v[1][0], 56 * 16);
	CHECK_EQ(p.v[1][1], 20 * 16);
	CHECK_EQ(p.v[2][1], 56 * 16);
	sgxfive_tri_default(&p, 256, 128);
	CHECK_EQ(p.v[1][0], 56 * 4 * 16);
	CHECK_EQ(p.v[1][1], 20 * 2 * 16);
}

/* The kernel test's state block; and the presence word's count. */
static void test_block(void)
{
	static const uint32_t want[SGXFIVE_TRI_BLOCK_WORDS] = {
		0xdf43, 0x01d00200, 0x10f0, 0x04000104, 0x00030001, 0x04000100,
		0x42000000, 0x42000000, 0x42000000, 0x42000000, 0x3f000000,
		0x3f000000, 0, 0x43000, 0x3727c5ac, 0x01555620, 0, 0,
	};
	uint32_t blk[SGXFIVE_TRI_BLOCK_WORDS], eos[SGXFIVE_TRI_EOS_WORDS];
	struct sgxfive_tri_params p;

	sgxfive_tri_default(&p, 64, 64);
	sgxfive_tri_block(blk, &L, &p);
	for (unsigned int i = 0; i < SGXFIVE_TRI_BLOCK_WORDS; i++)
		CHECK_EQ(blk[i], want[i]);
	sgxfive_tri_eos(eos, &p);
	CHECK_EQ(eos[0], 0x2000);
	CHECK_EQ(eos[1], 0x00010001);
	/* 256 x 128: the viewport and the last 32 x 32 block move. */
	sgxfive_tri_default(&p, 256, 128);
	sgxfive_tri_block(blk, &L, &p);
	CHECK_EQ(blk[6], 0x43000000);		/* 128.0 */
	CHECK_EQ(blk[8], 0x42800000);		/* 64.0 */
	sgxfive_tri_eos(eos, &p);
	CHECK_EQ(eos[1], 0x00070003);
}

/* The vertices' clip z (a depth ramp across the triangle): 0 is the default depth 0.5. */
static void test_vertex_z(void)
{
	struct sgxfive_tri_cpu c = {
		calloc(1, 4096), calloc(1, 4096), calloc(1, 4096), calloc(1, 4096),
		calloc(1, 4096), 0,
	};
	struct drm_sgxfive_render_cmd cmd;
	struct sgxfive_tri_params p;
	const uint32_t *v = c.gen + SGXFIVE_TRI_G_VTX / 4;

	sgxfive_tri_default(&p, 64, 64);
	CHECK_EQ(p.zndc[0] == 0.0f && p.zndc[1] == 0.0f && p.zndc[2] == 0.0f, 1);
	p.zndc[0] = -0.5f;
	p.zndc[1] = 0.5f;
	p.zndc[2] = 1.0f;
	CHECK_EQ(sgxfive_tri_scene(&c, &L, &p, &cmd), 0);
	CHECK_EQ(v[2], 0xbf000000);
	CHECK_EQ(v[6], 0x3f000000);
	CHECK_EQ(v[10], 0x3f800000);
	CHECK_EQ(v[3], 0x3f800000);	/* w stays 1.0 */
}

/* --tri-v: vertices in 1/256 pixel reach the vertex buffer as exact clip coordinates. */
static void test_fine_vertices(void)
{
	struct sgxfive_tri_cpu c = {
		calloc(1, 4096), calloc(1, 4096), calloc(1, 4096), calloc(1, 4096),
		calloc(1, 4096), 0,
	};
	struct drm_sgxfive_render_cmd cmd;
	struct sgxfive_tri_params p;
	const uint32_t *v = c.gen + SGXFIVE_TRI_G_VTX / 4;
	/* 64 x 64: ndc = px256 / 8192 - 1 */
	const int32_t f[3][2] = { { 0, 8192 }, { 8193, 16384 }, { 40, 4095 } };

	sgxfive_tri_default(&p, 64, 64);
	CHECK_EQ(p.fine, 0);
	sgxfive_tri_fine(&p, f);
	CHECK_EQ(p.fine, 1);
	/* the reference's 1/16 vertices are the nearest ones (half up) */
	CHECK_EQ(p.v[0][0], 0);
	CHECK_EQ(p.v[0][1], 512);
	CHECK_EQ(p.v[1][0], 512);	/* 8193 / 16 = 512.06 */
	CHECK_EQ(p.v[2][0], 3);		/* 40 / 16 = 2.5 */
	CHECK_EQ(p.v[2][1], 256);	/* 4095 / 16 = 255.94 */
	CHECK_EQ(sgxfive_tri_scene(&c, &L, &p, &cmd), 0);
	CHECK_EQ(v[0], 0xbf800000);	/* -1.0 */
	CHECK_EQ(v[1], 0);		/* 8192 / 8192 - 1 = 0 */
	CHECK_EQ(v[4], 0x39000000);	/* 2^-13 */
	CHECK_EQ(v[5], 0x3f800000);	/* 16384 / 8192 - 1 = 1.0 */
	CHECK_EQ(v[8], 0xbf7ec000);	/* 40 / 8192 - 1 = -0.9951171875 */
	CHECK_EQ(v[9], 0xbf000800);	/* 4095 / 8192 - 1 = -0.5001220703125 */
	/* 128 wide: ndc = px256 / 16384 - 1 */
	sgxfive_tri_default(&p, 128, 128);
	sgxfive_tri_fine(&p, f);
	CHECK_EQ(sgxfive_tri_scene(&c, &L, &p, &cmd), 0);
	CHECK_EQ(v[4], 0xbefff800);	/* 8193 / 16384 - 1 = -0.49993896484375 */
}

/* a finer unit: vertices in 1/4096 pixel (shift 12) are still exact clip coordinates on a 64 wide target */
static void test_fine_unit(void)
{
	struct sgxfive_tri_cpu c = {
		calloc(1, 4096), calloc(1, 4096), calloc(1, 4096), calloc(1, 4096),
		calloc(1, 4096), 0,
	};
	struct drm_sgxfive_render_cmd cmd;
	struct sgxfive_tri_params p;
	const uint32_t *v = c.gen + SGXFIVE_TRI_G_VTX / 4;
	/* 64 x 64 at shift 12: ndc = px / 131072 - 1 */
	const int32_t f[3][2] = { { 0, 131072 }, { 131073, 262144 }, { 700, 65535 } };

	sgxfive_tri_default(&p, 64, 64);
	sgxfive_tri_fine_unit(&p, f, 12);
	CHECK_EQ(p.fine, 1);
	CHECK_EQ(p.fine_shift, 12);
	CHECK_EQ(p.v[1][0], 512);	/* 131073 / 256 = 512.004: nearest 1/16 */
	CHECK_EQ(p.v[2][0], 3);		/* 700 / 256 = 2.73 */
	CHECK_EQ(p.v[2][1], 256);	/* 65535 / 256 = 255.996 */
	CHECK_EQ(sgxfive_tri_scene(&c, &L, &p, &cmd), 0);
	CHECK_EQ(v[0], 0xbf800000);
	CHECK_EQ(v[1], 0);
	CHECK_EQ(v[4], 0x37000000);	/* 131073 / 131072 - 1 = 2^-17 */
	CHECK_EQ(v[5], 0x3f800000);
	CHECK_EQ(v[8], 0xbf7ea200);	/* 700 / 131072 - 1 = -0.99465942... */
	/* the old call is the shift 8 */
	sgxfive_tri_default(&p, 64, 64);
	sgxfive_tri_fine(&p, f);
	CHECK_EQ(p.fine_shift, 8);
}

static void test_vdm(void)
{
	static const uint32_t want[SGXFIVE_TRI_VDM_WORDS] = {
		0x43040104, 0x0a022405, 0x80c00003, 0x3e001200, 0xf0000000, 0x003fffff,
		0xf3040100, 0x01c00082, 0x63040108, 0x0a022401, 0xc0000000,
	};
	uint32_t vdm[SGXFIVE_TRI_VDM_WORDS];

	sgxfive_tri_vdm(vdm, &L);
	for (unsigned int i = 0; i < SGXFIVE_TRI_VDM_WORDS; i++)
		CHECK_EQ(vdm[i], want[i]);
}

/* The programs in place with their patched fields, as sgx_tri_test_scene. */
static void test_scene(void)
{
	struct sgxfive_tri_cpu c = {
		calloc(1, 4096), calloc(1, 4096), calloc(1, 4096), calloc(1, 4096),
		calloc(1, 4096), 0,
	};
	struct drm_sgxfive_render_cmd cmd;
	struct sgxfive_tri_params p;
	const uint32_t *pv, *pp, *g;

	sgxfive_tri_default(&p, 64, 64);
	p.colour = 0xff00ff00;
	p.bg_colour = 0xff203040;
	memset(&cmd, 0xa5, sizeof(cmd));
	CHECK_EQ(sgxfive_tri_scene(&c, &L, &p, &cmd), 0);

	pv = c.pdsv + SGXFIVE_TRI_PV_VTX / 4;
	CHECK_EQ(pv[0], 0x3e001100);
	CHECK_EQ(pv[1], 3);
	CHECK_EQ(pv[2], 16);
	CHECK_EQ(pv[4], 0x200a);
	CHECK_EQ(pv[8], 0x67800072);
	pv = c.pdsv + SGXFIVE_TRI_PV_MTE / 4;
	CHECK_EQ(pv[0], 0x30401100);
	CHECK_EQ(pv[1], 0x02000018);
	CHECK_EQ(pv[4], 0x210a);
	pv = c.pdsv + SGXFIVE_TRI_PV_EOS / 4;
	CHECK_EQ(pv[0], 0x30401180);
	CHECK_EQ(pv[1], 0x00400001);
	CHECK_EQ(pv[4], 0x220a);
	CHECK_EQ(c.pdsv[SGXFIVE_TRI_PV_BLOCK / 4], 0xdf43);
	CHECK_EQ(c.pdsv[SGXFIVE_TRI_PV_EOSBLOCK / 4], 0x2000);
	CHECK_EQ(qw(c.usev, 0), 0xfa44020000000207ull);
	CHECK_EQ(qw(c.usev + SGXFIVE_TRI_UV_MTE18 / 4, 9), 0xfb2f4000a0200000ull);

	pp = c.pdsp;
	CHECK_EQ(pp[SGXFIVE_TRI_PP_PRIM / 4], 0x2000);
	CHECK_EQ(pp[SGXFIVE_TRI_PP_PRIM / 4 + 1], 4);
	CHECK_EQ(pp[SGXFIVE_TRI_PP_BGPRIM / 4], 0x2020);
	CHECK_EQ(pp[SGXFIVE_TRI_PP_SEC / 4], 0x2040);
	pp = c.pdsp + SGXFIVE_TRI_PP_PIXEV / 4;
	CHECK_EQ(pp[0], 0x2060);
	CHECK_EQ(pp[3], 0x01002080);
	CHECK_EQ(pp[4], 0x01002100);
	CHECK_EQ(pp[5], 0x00c00000);
	CHECK_EQ(pp[12], 0x00800000);
	CHECK_EQ(pp[6], 8);

	CHECK_EQ(sgxfive_limm_get(qw(c.usep + SGXFIVE_TRI_UP_FILL / 4, 1)), 0xff00ff00);
	CHECK_EQ(sgxfive_limm_get(qw(c.usep + SGXFIVE_TRI_UP_BGFILL / 4, 1)), 0xff203040);
	CHECK_EQ(qw(c.usep + SGXFIVE_TRI_UP_EOT / 4, 1), 0xfca0000000000000ull);
	CHECK_EQ(sgxfive_limm_get(qw(c.usep + SGXFIVE_TRI_UP_EOT / 4, 2)), 0x003f003f);
	CHECK_EQ(sgxfive_limm_get(qw(c.usep + SGXFIVE_TRI_UP_EOT / 4, 3)), 0x001f8000);
	CHECK_EQ(sgxfive_limm_get(qw(c.usep + SGXFIVE_TRI_UP_EOT / 4, 4)), 0x3e010000);
	CHECK_EQ((qw(c.usep + SGXFIVE_TRI_UP_EOT / 4, 4) >> 21) & 0x7f, 3);
	CHECK_EQ(qw(c.usep + SGXFIVE_TRI_UP_EOT / 4, 6),
		 sgxfive_emitpix_sb_set(0xfb24000000208180ull, 0x200));

	g = c.gen;
	CHECK_EQ(g[SGXFIVE_TRI_G_VTX / 4 + 0], 0xbf400000);
	CHECK_EQ(g[SGXFIVE_TRI_G_VTX / 4 + 3], 0x3f800000);
	CHECK_EQ(g[SGXFIVE_TRI_G_VTX / 4 + 4], 0x3f400000);
	CHECK_EQ(g[SGXFIVE_TRI_G_VTX / 4 + 5], 0xbec00000);
	CHECK_EQ(g[SGXFIVE_TRI_G_VTX / 4 + 9], 0x3f400000);
	CHECK_EQ(g[SGXFIVE_TRI_G_VTX / 4 + 2], 0);	/* clip z 0: depth 0.5 */
	CHECK_EQ(g[SGXFIVE_TRI_G_VTX / 4 + 6], 0);
	CHECK_EQ(g[SGXFIVE_TRI_G_IDX / 4], 0x00010000);
	CHECK_EQ(g[SGXFIVE_TRI_G_IDX / 4 + 1] & 0xffff, 2);
	CHECK_EQ(g[SGXFIVE_TRI_G_VDM / 4 + 10], 0xc0000000);

	/* The register words: sgx_tri_render_cmd's for 64 x 64. */
	CHECK_EQ(cmd.vdm_ctrl_stream_base, 0x3e001000);
	CHECK_EQ(cmd.te_aa, 0x20000000);
	CHECK_EQ(cmd.te_mtile1, MT2(4));
	CHECK_EQ(cmd.te_mtile2, MT2(4));
	CHECK_EQ(cmd.te_screen, (4 - 1) << 12 | (2 - 1));
	CHECK_EQ(cmd.te_mtile_stride, 16 * 1 * 1);
	CHECK_EQ(cmd.mte_ctrl, 0xa2);
	CHECK_EQ(cmd.mte_wcompare, 0x358637bd);
	CHECK_EQ(cmd.mte_wclamp, 0x358637bd);
	CHECK_EQ(cmd.mte_screen, 0x003f003f);
	CHECK_EQ(cmd.mte_multisamplectl, 0x88);
	CHECK_EQ(cmd.pixelbe, 0x80);
	/*
	 * 15 in bits 19:16, as the triangle's hardware runs set it, and bit 8,
	 * process empty regions, which targets above 64 x 64 need [HW].
	 */
	CHECK_EQ(cmd.isp_ipfmisc, 0x000f0100);
	CHECK_EQ(cmd.aa_mode_3d, 0x80000000);
	CHECK_EQ(cmd.isp_bgobjdepth, 0x3f800000);
	CHECK_EQ(cmd.isp_bgobj, 0x300);
	CHECK_EQ(cmd.isp_multisamplectl, 0x88);
	CHECK_EQ(cmd.tsp_config, 0x30);
	CHECK_EQ(cmd.event_pixel_pds_exec, 0x2e001080);
	CHECK_EQ(cmd.event_pixel_pds_data, 5);
	CHECK_EQ(cmd.event_pixel_pds_info, 1);
	CHECK_EQ(cmd.isp_fpuctrl, 1);
	CHECK_EQ(cmd.isp_depthsort, 0x100);
	CHECK_EQ(cmd.bgobj_words[0], 0x04000104);
	CHECK_EQ(cmd.bgobj_words[1], 0x00030000);
	CHECK_EQ(cmd.bgobj_words[2], 0x04000102);

	/* 256 x 128: the screen words and the PBE state follow the size. */
	sgxfive_tri_default(&p, 256, 128);
	CHECK_EQ(sgxfive_tri_scene(&c, &L, &p, &cmd), 0);
	CHECK_EQ(cmd.te_screen, 7 | 7 << 12);
	CHECK_EQ(cmd.mte_screen, 255 | 127 << 16);
	CHECK_EQ(sgxfive_limm_get(qw(c.usep + SGXFIVE_TRI_UP_EOT / 4, 2)), 0x007f00ff);
	CHECK_EQ(sgxfive_limm_get(qw(c.usep + SGXFIVE_TRI_UP_EOT / 4, 3)), 0x007f8000);
	CHECK_EQ(cmd.te_mtile1, MT2(4));
	CHECK_EQ(cmd.te_mtile2, MT2(4));
	CHECK_EQ(cmd.te_mtile_stride, 16 * 1 * 1);
	/* 1024 x 768: four macrotiles across and down (sgxfive_tiling, test_tiling's rule). */
	sgxfive_tri_default(&p, 1024, 768);
	CHECK_EQ(sgxfive_tri_scene(&c, &L, &p, &cmd), 0);
	CHECK_EQ(cmd.te_screen, (48 - 1) << 12 | (32 - 1));
	CHECK_EQ(cmd.te_mtile1, MT4(8) | 1u << 31);
	CHECK_EQ(cmd.te_mtile2, MT4(12));
	CHECK_EQ(cmd.te_mtile_stride, 16 * 2 * 3);
	CHECK_EQ(cmd.mte_screen, 1023 | 767 << 16);
	/* The device's largest; sizes beyond it, odd sizes. */
	sgxfive_tri_default(&p, 4096, 4096);
	CHECK_EQ(sgxfive_tri_scene(&c, &L, &p, &cmd), 0);
	sgxfive_tri_default(&p, 64, 4098);
	CHECK_EQ(sgxfive_tri_scene(&c, &L, &p, &cmd), -EINVAL);
	sgxfive_tri_default(&p, 4098, 64);
	CHECK_EQ(sgxfive_tri_scene(&c, &L, &p, &cmd), -EINVAL);
	sgxfive_tri_default(&p, 63, 64);
	CHECK_EQ(sgxfive_tri_scene(&c, &L, &p, &cmd), -EINVAL);
	free(c.pdsv);
	free(c.usev);
	free(c.pdsp);
	free(c.usep);
	free(c.gen);
}

/* Targets of every kind against the rule above. */
static void test_tiling(void)
{
	/* width, height, TE_SCREEN = (ty - 1) << 12 | (tx - 1), TE_MTILE1, TE_MTILE2, TE_MTILE */
	static const uint32_t rule[][6] = {
		{ 64, 64, (4 - 1) << 12 | (2 - 1), MT2(4), MT2(4), 16 * 1 * 1 },
		{ 1, 1, (1 - 1) << 12 | (1 - 1), MT2(4), MT2(4), 16 * 1 * 1 },
		{ 100, 60, (4 - 1) << 12 | (4 - 1), MT2(4), MT2(4), 16 * 1 * 1 },
		{ 256, 128, (8 - 1) << 12 | (8 - 1), MT2(4), MT2(4), 16 * 1 * 1 },
		{ 128, 192, (12 - 1) << 12 | (4 - 1), MT2(4), MT2(8), 16 * 1 * 2 },
		{ 256, 256, (16 - 1) << 12 | (8 - 1), MT2(4), MT2(8), 16 * 1 * 2 },
		{ 512, 16, (1 - 1) << 12 | (16 - 1), MT2(8), MT2(4), 16 * 2 * 1 },
		/* one row short of 640 x 480: still two macrotiles */
		{ 640, 475, (30 - 1) << 12 | (20 - 1), MT2(12), MT2(16), 16 * 3 * 4 },
		{ 640, 480, (30 - 1) << 12 | (20 - 1), MT4(8) | 1u << 31, MT4(8), 16 * 2 * 2 },
		{ 333, 777, (49 - 1) << 12 | (11 - 1), MT2(8), MT2(28), 16 * 2 * 7 },
		{ 1366, 768, (48 - 1) << 12 | (43 - 1), MT4(12) | 1u << 31, MT4(12), 16 * 3 * 3 },
		{ 2049, 2049, (129 - 1) << 12 | (65 - 1), MT4(20) | 1u << 31, MT4(36), 16 * 5 * 9 },
		/* the area decides n: 4096 x 74 is below 640 x 480, 4096 x 75 is not */
		{ 4096, 74, (5 - 1) << 12 | (128 - 1), MT2(64), MT2(4), 16 * 16 * 1 },
		{ 4096, 75, (5 - 1) << 12 | (128 - 1), MT4(32) | 1u << 31, MT4(4), 16 * 8 * 1 },
		{ 4096, 4096, (256 - 1) << 12 | (128 - 1), MT4(32) | 1u << 31, MT4(64),
		  16 * 8 * 16 },
	};
	struct sgxfive_tiling t;

	for (unsigned int i = 0; i < sizeof(rule) / sizeof(rule[0]); i++) {
		memset(&t, 0xa5, sizeof(t));
		sgxfive_tiling(&t, rule[i][0], rule[i][1]);
		CHECK_EQ(t.te_screen, rule[i][2]);
		CHECK_EQ(t.te_mtile1, rule[i][3]);
		CHECK_EQ(t.te_mtile2, rule[i][4]);
		CHECK_EQ(t.te_mtile_stride, rule[i][5]);
	}
}

/* The kernel test's reference points, and a reference image checks clean. */
static void test_expect(void)
{
	struct sgxfive_tri_params p;
	struct sgxfive_tri_counts n;
	uint32_t *fb = calloc(64 * 64, 4), in = 0, edge = 0;

	sgxfive_tri_default(&p, 64, 64);
	p.colour = 0xff00ff00;
	p.bg_colour = 0xff203040;
	CHECK_EQ(sgxfive_tri_expect(&p, 28, 28), 1);
	CHECK_EQ(sgxfive_tri_expect(&p, 2, 2), 0);
	CHECK_EQ(sgxfive_tri_expect(&p, 60, 60), 0);
	CHECK_EQ(sgxfive_tri_expect(&p, 37, 38), (uint64_t)-1);
	CHECK_EQ(sgxfive_tri_expect(&p, 30, 13), (uint64_t)-1);
	CHECK_EQ(sgxfive_tri_expect(&p, 50, 22), 1);
	CHECK_EQ(sgxfive_tri_expect(&p, 50, 41), 0);
	for (uint32_t y = 0; y < 64; y++)
		for (uint32_t x = 0; x < 64; x++) {
			int e = sgxfive_tri_expect(&p, x, y);

			in += e == 1;
			edge += e == -1;
			fb[y * 64 + x] = e == 1 ? p.colour : p.bg_colour;
		}
	CHECK(in < 1080 && in + edge > 1080 && in > 800);
	CHECK_EQ(sgxfive_tri_check(&p, fb, &n), 0);
	CHECK_EQ(n.wrong_in + n.wrong_out + n.wrong_edge, 0);
	CHECK_EQ(n.tri, in);
	CHECK(n.flipped > 0);
	fb[28 * 64 + 28] = 0x12345678;			/* one wrong pixel inside */
	CHECK_EQ(sgxfive_tri_check(&p, fb, &n), -EIO);
	CHECK_EQ(n.wrong_in, 1);
	CHECK_EQ(n.other, 1);
	free(fb);
}

int main(void)
{
	test_words();
	test_default();
	test_block();
	test_vdm();
	test_scene();
	test_vertex_z();
	test_fine_vertices();
	test_fine_unit();
	test_tiling();
	test_expect();
	return tap_done();
}
