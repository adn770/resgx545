/* SPDX-License-Identifier: MIT */
/*
 * Probe programs inside the first triangle's render (sgxfive-test probe --tri):
 * the scene of sgxfive_tri_scene() with some of its
 * programs replaced by the caller's, patched the way the defaults are, so that
 * a probe sees a vertex task, a triangle and the pixel events of every tile.
 *
 * The slots, and what the host patches in a replacement (everything else is
 * the caller's words, verbatim, except the scratch immediates below):
 *
 *   pixev   the pixel-event PDS program (asm/transfer/pds_pixevent.s), at the
 *           default's place. Data dwords 0-5 and 12 as the default's: 0 the
 *           PTOFF task's U0, 1 and 2 zero, 3 the end-of-tile task's U0 (the
 *           eot slot's program), 4 and 5 the end-of-render task's U0 and U1,
 *           12 the end-of-tile U1 base (PBENABLE). So a replacement keeps the
 *           default's data layout and dispatch. EVENT_PIXEL_PDS_DATA becomes
 *           its data rows and EVENT_PIXEL_PDS_INFO 0, so it may douta into
 *           attributes 0-SGXFIVE_TRI_PROBE_ATTRS - 1 of the end-of-tile task,
 *           which are its tile buffer (bits 5:0 of the info set, douta does
 *           not reach them).
 *   eot     the end-of-tile USE program (asm/transfer/use_eot.s), at
 *           SGXFIVE_TRI_PROBE_UP_EOT. As use_eot.s: instructions 1-4 are four
 *           "mov.skipinv r0, #imm" that get PBE words 0-3 and registers r0-r3,
 *           and the last instruction is the emitpix2 that gets the sideband.
 *   vtxpds  the vertex PDS program (asm/tri/pds_vtx.s), at
 *           SGXFIVE_TRI_PROBE_PV_VTX. Data dwords 0, 1, 2 and 4 as the
 *           default's: the vertex buffer, the doutd word, the stride and the
 *           vertex shader's U0 (the vtxuse slot's program); the VDM's vertex
 *           task points at it with its data rows.
 *   vtxuse  the vertex USE program (asm/tri/use_vtx.s), at
 *           SGXFIVE_TRI_PROBE_UV_VTX. As use_vtx.s: when its first
 *           instruction is a phas with a next phase #N (N > 0), N counts from
 *           the program's start and the host adds the program's index from
 *           the code base.
 *   pixel   the triangle's pixel shader (asm/transfer/use_fill.s), at
 *           SGXFIVE_TRI_PROBE_UP_PIXEL; its primary's U0 points at it. The
 *           colour is not patched in (the background keeps its own shader). A
 *           first phas with a next phase #N (N > 0) is renumbered as vtxuse's,
 *           from the pixel code base (a punch-through shader's pt phase).
 *   pixtask a plain USE task for the pixel-event program to start itself (no PBE
 *           flags), at SGXFIVE_TRI_PROBE_UP_PIXTASK: its U0 goes to the pixel-event
 *           program's data dword 11 (unused by the default), replaced or not. The
 *           end-of-tile task's secondary attributes hold the tile's colours, so a
 *           pixel-event probe passes its results on with douta to this task instead
 *           (kicking it before the end-of-tile task). Such a task hung at any place
 *           but the PTOFF program's, so the host also turns the PTOFF program into
 *           its phas and a br to the pixtask: kick it with the PTOFF task's U0
 *           (data dword 0) and U1 (dword 1, 0).
 *   pixpds  the triangle's primary pixel PDS program (asm/transfer/pds_prim.s), at
 *           SGXFIVE_TRI_PROBE_PP_PIXPDS in the pixel PDS page. Data dwords 0 and 1
 *           as the default's: the pixel shader's U0 (the pixel slot's program, or
 *           the default fill) and U1. The triangle's state block points at it
 *           with its data rows and SGXFIVE_TRI_PROBE_PIX_ROWS rows of primary
 *           attributes, so it may douti, doutt or doutd into pa0-pa15 before
 *           its doutu; the background keeps its own.
 *   bgpds   the background object's primary pixel PDS program, in place of pds_prim's
 *           background copy (asm/transfer/pds_prim.s), at SGXFIVE_TRI_PROBE_PP_BGPDS in
 *           the pixel PDS page. As pixpds: data dwords 0 and 1 the bgpixel slot's (or
 *           the default background's) pixel shader U0 and U1; the render command's
 *           background object words point at it with its data rows and
 *           SGXFIVE_TRI_PROBE_PIX_ROWS rows of primary attributes, so it may douti, doutt
 *           or doutd into pa0-pa15 before its doutu.
 *   bgpixel the background object's pixel shader (asm/transfer/use_fill.s's background
 *           copy), at SGXFIVE_TRI_PROBE_UP_BGPIXEL; the background's primary (the
 *           default's, or the bgpds slot's data dword 0) starts it. Patched as the
 *           pixel slot, a first phas with a next phase renumbered from the pixel code
 *           base.
 *   state   the triangle's state task (asm/tri/use_mtest18.s), in its own place,
 *           SGXFIVE_TRI_UV_MTE18 (up to SGXFIVE_TRI_UV_MTE2); the MTE PDS
 *           program's U0 gets the slot's temporaries. Not with blk_add, which
 *           patches use_mtest18's second move.
 *
 * Replacement USE programs run with the temporaries their slot gives (at
 * least the default's), and every limm "mov d, #imm" in them whose immediate
 * is SGXFIVE_TRI_PROBE_SCRATCH_IMM | k (k < 0x10000) loads scratch + k
 * instead, as the fill probes' (sgxfive-test probe), and every one with
 * SGXFIVE_TRI_PROBE_TARGET_IMM | k the render target's address + k; so does every data dword
 * of a replacement PDS program with that value (a texture's address, say).
 */
#ifndef SGXFIVE_TRI_PROBE_H
#define SGXFIVE_TRI_PROBE_H

#include <stdbool.h>

#include "sgxfive_render.h"

enum sgxfive_tri_slot {
	SGXFIVE_TRI_SLOT_PIXEV,
	SGXFIVE_TRI_SLOT_EOT,
	SGXFIVE_TRI_SLOT_VTXPDS,
	SGXFIVE_TRI_SLOT_VTXUSE,
	SGXFIVE_TRI_SLOT_PIXEL,
	SGXFIVE_TRI_SLOT_PIXTASK,
	SGXFIVE_TRI_SLOT_PIXPDS,
	SGXFIVE_TRI_SLOT_STATE,
	SGXFIVE_TRI_SLOT_BGPDS,
	SGXFIVE_TRI_SLOT_BGPIXEL,
	SGXFIVE_TRI_SLOT_COUNT,
};

#define SGXFIVE_TRI_PROBE_SCRATCH_IMM	0x5CAF0000u
/* the same with the render target's address (the layout's fb): a program that reads its target */
#define SGXFIVE_TRI_PROBE_TARGET_IMM	0x5CB00000u
#define SGXFIVE_TRI_PROBE_ATTRS		16	/* a replaced pixev's douta range */

/* Where replacements go, inside the scene's pages (after the defaults). */
#define SGXFIVE_TRI_PROBE_PV_VTX	0x200	/* vtxpds, to the page's end */
#define SGXFIVE_TRI_PROBE_UV_VTX	0x200	/* vtxuse, to the page's end */
#define SGXFIVE_TRI_PROBE_UP_PIXEL	0x100	/* pixel, up to the pixtask slot */
#define SGXFIVE_TRI_PROBE_UP_PIXTASK	0x600	/* pixtask, up to the eot slot */
#define SGXFIVE_TRI_PROBE_PIXTASK_U0	11	/* the pixev data dword with its U0 */
#define SGXFIVE_TRI_PROBE_UP_EOT	0x800	/* eot, up to the bgpixel slot */
#define SGXFIVE_TRI_PROBE_UP_BGPIXEL	0xc00	/* bgpixel, to the page's end */
#define SGXFIVE_TRI_PROBE_PP_PIXPDS	0x800	/* pixpds, up to the bgpds slot (pixev up to it) */
#define SGXFIVE_TRI_PROBE_PP_BGPDS	0xc00	/* bgpds, to the page's end */
#define SGXFIVE_TRI_PROBE_PIX_ROWS	4	/* primary attribute rows with pixpds */
/* A second object (obj2_first): its pds_mte, block, index list, primary and pixel shader. */
#define SGXFIVE_TRI_PROBE_PV_MTE2	0x0c0	/* pds_mte, the second block's */
#define SGXFIVE_TRI_PROBE_G_BLK2	0xd00	/* its state block, up to 32 dwords */
#define SGXFIVE_TRI_PROBE_G_IDX2	0xe00	/* its 16-bit indices */
#define SGXFIVE_TRI_PROBE_PP_PRIM2	0x700	/* pds_prim, starting its pixel shader */
#define SGXFIVE_TRI_PROBE_UP_PIXEL2	0x400	/* its pixel shader (the pixel slot up to it) */
#define SGXFIVE_TRI_PROBE_BLK2_WORDS	32

/* One replacement: n words (USSE instructions, or one PDS word per element). */
struct sgxfive_tri_prog {
	const uint64_t *words;
	uint32_t n;		/* 0: keep the default */
	uint32_t data;		/* PDS: its data dwords (whole rows of four) */
	uint32_t temps;		/* USE: at least this many temporaries */
};

/*
 * Up to 15 vertices fit the scene's own vertex buffer (SGXFIVE_TRI_G_VTX up to _G_IDX);
 * more move it and the index list to the scene page's spare room, here: 126 vertices of
 * 16 bytes at 0x400, their 16-bit indices at 0xc00.
 */
#define SGXFIVE_TRI_PROBE_MAX_VERTICES	126
/*
 * More than that, up to SGXFIVE_TRI_PROBE_WIDE_VERTICES, need the rig's gen region of
 * SGXFIVE_TRI_PROBE_GEN_PAGES pages (the cpu view's gen_size): the vertices at W_VTX, their
 * 16-bit indices at W_IDX.
 */
#define SGXFIVE_TRI_PROBE_WIDE_VERTICES	1500
#define SGXFIVE_TRI_PROBE_GEN_PAGES	9
#define SGXFIVE_TRI_PROBE_W_VTX		0x1000
#define SGXFIVE_TRI_PROBE_W_IDX		0x8000
/* The render command's words a probe may set (version 1, 0x68 bytes). */
#define SGXFIVE_TRI_PROBE_CMD_WORDS	26
/* The two-object VDM stream's words (with obj2_first); the one-object stream's are 11. */
#define SGXFIVE_TRI_PROBE_VDM2_WORDS	19
#define SGXFIVE_TRI_PROBE_G_VTX		0x400
#define SGXFIVE_TRI_PROBE_G_IDX		0xc00

struct sgxfive_tri_probe {
	struct sgxfive_tri_prog slot[SGXFIVE_TRI_SLOT_COUNT];
	uint32_t scratch;	/* where scratch immediates point; 0: not patched */
	/*
	 * 0 or 3: the one triangle; up to SGXFIVE_TRI_PROBE_MAX_VERTICES: copies of it
	 * after it, copy c (vertices 3c to 3c + 2) moved c/16 pixel right and down, so that
	 * the vertex programs run for more vertices than one task's.
	 */
	uint32_t vertices;
	/*
	 * 0: the position alone; N: N more output dwords per vertex, texture coordinate
	 * sets of four components and then the rest (the state block's OUTSEL vertex size
	 * 4 + N, its coordsize word a 3-bit field per set), for a vtxuse program that
	 * writes o4 on.
	 */
	uint32_t coords;
	/* the copies at clip-space z = c / 16 (copy c), not all at 0 */
	bool copy_depth;
	/*
	 * with isp2_set: the state block carries ISP word 2 (stencil) isp2 in place of the wrap
	 * word, at word 3, the pixel programs and viewport one word on (presence 0xdd47, ISP0
	 * bit 8); blk_val then indexes that layout
	 */
	bool isp2_set;
	uint32_t isp2;
	/*
	 * presence bits the block lacks, each with its words, inserted in bit order after isp2:
	 * bits 2-5 one word each (ISP word 2 and, by inference, the back-face ISP words), bit 7
	 * two (region clip); the block is padded with zeros to whole rows of four, at most 32
	 * dwords, and the state copy grows with it (doutd, the VDM state's attribute rows, a
	 * 32-dword copy); blk_val then indexes the grown layout
	 */
	uint32_t add_mask;
	uint32_t add_val[16][2];
	/* state block words set as given: bit i of blk_mask, word i is blk_val[i] */
	uint32_t blk_mask;
	uint32_t blk_val[SGXFIVE_TRI_BLOCK_WORDS];
	/* state block words flipped after those: bit i of blk_xor_mask, word i ^= blk_xor_val[i] */
	uint32_t blk_xor_mask;
	uint32_t blk_xor_val[SGXFIVE_TRI_BLOCK_WORDS];
	/* render command words set as given: bit i of cmd_mask, word i is cmd_val[i] */
	uint32_t cmd_mask;
	uint32_t cmd_val[SGXFIVE_TRI_PROBE_CMD_WORDS];
	/* render command words flipped after those: bit i of cmd_xor_mask, word i ^= cmd_xor_val[i] */
	uint32_t cmd_xor_mask;
	uint32_t cmd_xor_val[SGXFIVE_TRI_PROBE_CMD_WORDS];
	/*
	 * VDM stream words set as given, after coords: bit i of vdm_mask, word i is vdm_val[i].
	 * Words 0 to SGXFIVE_TRI_VDM_WORDS - 1 are the one-object stream's; with obj2_first the
	 * stream is the two-object one (SGXFIVE_TRI_PROBE_VDM2_WORDS words: the first state block
	 * 0-1, its index list and vertex task 2-7, the second state block 8-9, its index list and
	 * vertex task 10-15, the end of scene 16-17, terminate 18), set and flipped as built, so
	 * word 9 changes the second state block alone.
	 */
	uint32_t vdm_mask;
	uint32_t vdm_val[SGXFIVE_TRI_PROBE_VDM2_WORDS];
	/* VDM stream words flipped after those: bit i of vdm_xor_mask, word i ^= vdm_xor_val[i] */
	uint32_t vdm_xor_mask;
	uint32_t vdm_xor_val[SGXFIVE_TRI_PROBE_VDM2_WORDS];
	/*
	 * PBE words 0 to 3 of the end-of-tile task (the default's or the eot slot's) set as
	 * given: bit i of pbe_mask, word i is pbe_val[i]; word 4, the sideband, is sideband_set's.
	 */
	uint32_t pbe_mask;
	uint32_t pbe_val[4];
	/* with an end-of-tile slot: its emitpix2's sideband, the default's 0x200 unless set */
	bool sideband_set;
	uint32_t sideband;
	/*
	 * 0, or a second object: the copies from vertex obj2_first on (a multiple of 3 below
	 * vertices) drawn after the first with their own state block, the first's as built here
	 * with obj2_blk_val[i] for bit i of obj2_blk_mask and its primary pixel program its own,
	 * which starts obj2_pixel (patched as the pixel slot; n 0: the default fill) with its one
	 * primary attribute row; the pixel slot then ends before SGXFIVE_TRI_PROBE_UP_PIXEL2.
	 */
	uint32_t obj2_first;
	uint32_t obj2_blk_mask;
	uint32_t obj2_blk_val[SGXFIVE_TRI_PROBE_BLK2_WORDS];
	struct sgxfive_tri_prog obj2_pixel;
	/*
	 * the second object's primary pixel PDS program, a caller's as the pixpds slot is the
	 * first's (n 0: the default's, as pds_prim): at SGXFIVE_TRI_PROBE_PP_PRIM2, up to the
	 * pixpds slot; its data dwords 0 and 1 are the second object's pixel shader's U0 and U1,
	 * scratch immediates in its data patched; the second block points at it with
	 * SGXFIVE_TRI_PROBE_PIX_ROWS rows of primary attributes (obj2_blk_val words win), so it
	 * may douta constants into the shader's secondary attributes with a block of room for them.
	 */
	struct sgxfive_tri_prog obj2_pixpds;
};

/* The slot called name ("pixev", "eot", ...), or -1. */
int sgxfive_tri_slot_find(const char *name);
const char *sgxfive_tri_slot_name(unsigned int slot);
bool sgxfive_tri_slot_is_pds(unsigned int slot);

/*
 * Put pr's replacements into a scene sgxfive_tri_scene() built in c (layout
 * l, params p, command cmd). -EINVAL if one does not fit its place, has a
 * data segment that is not whole rows, too short for the dwords patched
 * (pixev 16, vtxpds 8), longer than 128 dwords or not followed by code, or
 * asks for more than 128 temporaries, or if pr's vertices are not whole
 * triangles or more than the vertex buffer holds.
 */
int sgxfive_tri_probe_apply(const struct sgxfive_tri_cpu *c, const struct sgxfive_tri_layout *l,
			    const struct sgxfive_tri_params *p, const struct sgxfive_tri_probe *pr,
			    struct drm_sgxfive_render_cmd *cmd);

/* ---- A render engine whose scene the caller may change before it is submitted ------- */

struct sgxfive_tri_rig {
	struct sgxfive_vm *vm;
	struct sgxfive_dev *dev;
	uint32_t ctx;
	struct sgxfive_bo *bo, *fb_bo;
	struct sgxfive_tri_cpu cpu;		/* the five pages */
	struct sgxfive_tri_layout layout;
	struct sgxfive_tri_params params;	/* of the last build */
	uint32_t *fb;				/* W x H, then a guard page */
	uint64_t fb_addr, fb_size;
	uint32_t done;				/* syncobj of the last submit */
	bool pending;
	struct drm_sgxfive_render_cmd cmd __attribute__((aligned(8)));
};

/*
 * The five pages (as sgxfive_render_create's) and a colour buffer for targets
 * up to max_w x max_h in vm, for the render context ctx.
 */
int sgxfive_tri_rig_create(struct sgxfive_vm *vm, uint32_t ctx, uint32_t max_w, uint32_t max_h,
			   struct sgxfive_tri_rig **out);
void sgxfive_tri_rig_destroy(struct sgxfive_tri_rig *g);
/* The scene of p with pr's replacements (pr may be NULL), the target set to the sentinel. */
int sgxfive_tri_rig_build(struct sgxfive_tri_rig *g, const struct sgxfive_tri_params *p,
			  const struct sgxfive_tri_probe *pr);
int sgxfive_tri_rig_submit(struct sgxfive_tri_rig *g);
/* As sgxfive_render_wait: 0, the wait's error, or the job's (-EIO, -ENOSPC, ...). */
int sgxfive_tri_rig_wait(struct sgxfive_tri_rig *g, int64_t timeout_ns);

#endif
