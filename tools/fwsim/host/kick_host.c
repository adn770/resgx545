// SPDX-License-Identifier: GPL-2.0-only OR MIT
/*
 * Host harness for the kernel's render-job builders (drivers/gpu/drm/gma500/sgxfive/sgx_render.c
 * and sgx_xfer.c of the linux fork, at the commit a kept session ran), built with the shim headers
 * of host/shim and tools/fwtask/host/shim in place of the kernel's, and with "sgxfive_ctx_gen.h",
 * the context-memory offsets that tools/fwsim/kick.py copies out of the same commit's
 * sgxfive_ctx.h. It mirrors the kernel's glue around the builders at that commit (sgxfive_cmd.c
 * sgxfive_render_addrs() and sgxfive_render_build(), sgxfive_render.c sgxfive_render_init_mem()
 * and sgxfive_render_write()); it reads and prints our kernel's structures only, never a firmware
 * byte.
 *
 *   kick_host < INPUT
 *       INPUT: "key=value" lines (mem, pd_phys, slot, max_w, max_h, aa4, arrays, tail_room,
 *       pb_pages, seqno, first, last; numbers in C notation) and "cmd:N=value" lines, the user's
 *       struct drm_sgxfive_render_cmd. Prints "addr NAME=0x..." for each structure's device
 *       address, "size=0x..." (the TA command's size in the TA CCB), then the words of the
 *       context's memory as the kernel leaves them after the context's creation ("init SPACE:N=")
 *       and after the job's run writes, before its kick ("job SPACE:N="). Spaces: ctx (the HW
 *       render context), ctl (the TA CCB control), rtds, pb (descriptor), pbblk, kw (access,
 *       pending, render target status, background update list), rd (render details), ta (the TA
 *       command at the CCB's offset 0), bg (the background object); after the creation also
 *       "init pt:N=" for each nonzero entry of the PB's page table.
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <linux/types.h>

#include "sgx_render.h"
#include "sgx_xfer.h"
#include "sgxfive_ctx_gen.h"

/* sgxfive_drv.c sgxfive_rev1_heaps: the PARAMETERS and TA_DATA heaps' bases (REV1). */
#define HEAP_PARAMETERS_BASE	0x10000000u
#define HEAP_TA_DATA_BASE	0x20000000u
#define CTX_MEM_BYTES		(SGXFIVE_CTX_PAGE_OFF + 0x1000)
#define BG_WORDS		23

struct input {
	u32 mem, pd_phys, slot, max_w, max_h, aa4, arrays, tail_room, pb_pages, seqno, first, last;
	struct drm_sgxfive_render_cmd c;
};

static int parse(FILE *f, struct input *in)
{
	char line[256];
	u32 *cw = (u32 *)&in->c;

	while (fgets(line, sizeof(line), f)) {
		char *eq = strchr(line, '=');
		unsigned long v;
		unsigned int n;

		if (!eq || line[0] == '#')
			continue;
		*eq = 0;
		v = strtoul(eq + 1, NULL, 0);
		if (sscanf(line, "cmd:%u", &n) == 1) {
			if (n >= sizeof(in->c) / 4)
				return -1;
			cw[n] = v;
			continue;
		}
#define KEY(k) if (!strcmp(line, #k)) { in->k = v; continue; }
		KEY(mem) KEY(pd_phys) KEY(slot) KEY(max_w) KEY(max_h) KEY(aa4) KEY(arrays)
		KEY(tail_room) KEY(pb_pages) KEY(seqno) KEY(first) KEY(last)
#undef KEY
		fprintf(stderr, "kick_host: unknown key %s\n", line);
		return -1;
	}
	return 0;
}

/* sgxfive_cmd.c sgxfive_render_addrs() */
static void addrs(struct sgx_render_addrs *a, const struct input *in, const struct sgx_render_tadata *td)
{
	u32 mem = in->mem;

	memset(a, 0, sizeof(*a));
	a->pd_phys = in->pd_phys;
	a->param_base = HEAP_PARAMETERS_BASE + in->slot * SGXFIVE_RENDER_PARAM_SLOT;
	a->tadata = HEAP_TA_DATA_BASE + in->slot * SGXFIVE_RENDER_TD_SLOT;
	a->td = *td;
	a->ctx = mem + SGXFIVE_CTX_HW_OFF;
	a->ccb = mem + SGXFIVE_CTX_CCB_OFF;
	a->ccb_ctl = mem + SGXFIVE_CTX_CTL_OFF;
	a->rtds = mem + SGXFIVE_RCTX_RTDS_OFF;
	a->pbdesc = mem + SGXFIVE_RCTX_PBDESC_OFF;
	a->pbblock = mem + SGXFIVE_RCTX_PBBLOCK_OFF;
	a->rd = mem + SGXFIVE_RCTX_RD_OFF;
	a->ta_status = mem + SGXFIVE_CTX_TA_OFF;
	a->td_status = mem + SGXFIVE_CTX_FENCE_OFF;
	a->access = mem + SGXFIVE_RCTX_ACCESS_OFF;
	a->pending = mem + SGXFIVE_RCTX_PENDING_OFF;
	a->rt_status = mem + SGXFIVE_RCTX_RTSTATUS_OFF;
	a->bgpri = mem + SGXFIVE_RCTX_BGPRI_OFF;
}

static u32 *w(u8 *mem, u32 off)
{
	return (u32 *)(mem + off);
}

static void dump(const char *phase, const char *space, const u32 *p, unsigned int n)
{
	for (unsigned int i = 0; i < n; i++)
		printf("%s %s:%u=0x%08x\n", phase, space, i, p[i]);
}

/* The PB's page table: its nonzero entries only (one per page of the slot's heap). */
static void dump_pt(const char *phase, const u32 *pt)
{
	for (unsigned int i = 0; i < SGX_RENDER_PT_BYTES / 4; i++)
		if (pt[i])
			printf("%s pt:%u=0x%08x\n", phase, i, pt[i]);
}

static void dump_all(const char *phase, u8 *mem, const u32 *bg)
{
	dump(phase, "ctx", w(mem, SGXFIVE_CTX_HW_OFF), SGX_RENDER_CTX_SIZE / 4);
	dump(phase, "ctl", w(mem, SGXFIVE_CTX_CTL_OFF), 2);
	dump(phase, "rtds", w(mem, SGXFIVE_RCTX_RTDS_OFF), SGX_RENDER_RTDS_SIZE / 4);
	dump(phase, "pb", w(mem, SGXFIVE_RCTX_PBDESC_OFF), SGX_RENDER_PBDESC_SIZE / 4);
	dump(phase, "pbblk", w(mem, SGXFIVE_RCTX_PBBLOCK_OFF), SGX_RENDER_PBBLOCK_SIZE / 4);
	dump(phase, "kw", w(mem, SGXFIVE_RCTX_ACCESS_OFF), 4);
	dump(phase, "rd", w(mem, SGXFIVE_RCTX_RD_OFF), SGX_RENDER_RD_SIZE / 4);
	dump(phase, "ta", w(mem, SGXFIVE_CTX_CCB_OFF), SGX_RENDER_CMD_SIZE / 4);
	dump(phase, "bg", bg, BG_WORDS);
}

int main(void)
{
	static u8 mem[CTX_MEM_BYTES], img[SGX_XFER_CMD_SIZE];
	static u32 pt[SGX_RENDER_PT_BYTES / 4], bg[BG_WORDS];
	struct input in = { .pb_pages = SGX_RENDER_PB_PAGES, .seqno = 1, .first = 1, .last = 1 };
	struct sgx_render_tadata td;
	struct sgx_render_addrs a;
	struct sgx_render_kick k;
	u32 size, tag;
	int ret;

	if (parse(stdin, &in))
		return 2;
	ret = sgx_render_tadata_layout(&td, in.max_w, in.max_h,
				       sgx_render_rgn_arrays(in.arrays, in.aa4),
				       sgx_render_tail_room(in.max_w, in.max_h, in.aa4, in.tail_room));
	if (ret) {
		fprintf(stderr, "kick_host: tadata layout %d\n", ret);
		return 1;
	}
	addrs(&a, &in, &td);
	printf("addr ctx=0x%08x\naddr ccb=0x%08x\naddr ccb_ctl=0x%08x\naddr rtds=0x%08x\n"
	       "addr pbdesc=0x%08x\naddr pbblock=0x%08x\naddr rd=0x%08x\naddr access=0x%08x\n"
	       "addr param_base=0x%08x\naddr tadata=0x%08x\naddr td_size=0x%08x\n"
	       "addr fence=0x%08x\naddr ta_status=0x%08x\n",
	       a.ctx, a.ccb, a.ccb_ctl, a.rtds, a.pbdesc, a.pbblock, a.rd, a.access, a.param_base,
	       a.tadata, td.size, a.td_status, a.ta_status);

	/* sgxfive_render.c sgxfive_render_init_mem(): the context as created (PB without a final) */
	sgx_render_ctx(w(mem, SGXFIVE_CTX_HW_OFF), &a);
	w(mem, SGXFIVE_CTX_CTL_OFF)[0] = 0;
	w(mem, SGXFIVE_CTX_CTL_OFF)[1] = 0;
	sgx_render_rtds(w(mem, SGXFIVE_RCTX_RTDS_OFF), &a, 0);
	sgx_render_pb(w(mem, SGXFIVE_RCTX_PBDESC_OFF), w(mem, SGXFIVE_RCTX_PBBLOCK_OFF), pt, &a,
		      in.pb_pages);
	*w(mem, SGXFIVE_RCTX_ACCESS_OFF) = 0;
	*w(mem, SGXFIVE_RCTX_PENDING_OFF) = 0;
	*w(mem, SGXFIVE_RCTX_RTSTATUS_OFF) = 0;
	*w(mem, SGXFIVE_CTX_TA_OFF) = *w(mem, SGXFIVE_CTX_FENCE_OFF);
	dump_all("init", mem, bg);
	dump_pt("init", pt);

	/* sgxfive_cmd.c sgxfive_render_build() */
	memset(img, 0, sizeof(img));
	sgx_render_scene_kick(&k, in.seqno, in.seqno, in.first, in.last);
	size = sgx_render_cmd(img, &a, &in.c, &k);
	sgx_render_rd((u32 *)(img + SGXFIVE_RENDER_IMG_RD), &a, &in.c);
	printf("size=0x%x\n", size);

	/* sgxfive_render.c sgxfive_render_write(), the context's first job (CCB offset 0) */
	memcpy(w(mem, SGXFIVE_RCTX_RD_OFF), img + SGXFIVE_RENDER_IMG_RD, SGX_RENDER_RD_SIZE);
	memcpy(&tag, img + SGXFIVE_RENDER_IMG_RD + SGX_RENDER_RD_BGTAG, 4);
	sgx_render_bgobj(bg, &in.c, sgx_render_bgtag_layers(tag));
	*w(mem, SGXFIVE_RCTX_BGPRI_OFF) = in.c.bgobj_words[2];
	sgx_render_rtds_resize(w(mem, SGXFIVE_RCTX_RTDS_OFF), in.c.mte_screen);
	sgx_render_rtds_job(w(mem, SGXFIVE_RCTX_RTDS_OFF));
	*w(mem, SGXFIVE_RCTX_PENDING_OFF) += sgx_render_executed(img);
	memcpy(mem + SGXFIVE_CTX_CCB_OFF, img, SGX_RENDER_CMD_STRIDE);
	w(mem, SGXFIVE_CTX_CTL_OFF)[0] = size & (SGX_RENDER_CCB_SIZE - 1);
	dump_all("job", mem, bg);
	return 0;
}
