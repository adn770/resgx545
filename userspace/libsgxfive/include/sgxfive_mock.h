/* SPDX-License-Identifier: MIT */
/*
 * An in-process mock of the sgxfive render node, behind struct
 * sgxfive_backend: render-node discovery, DEV_QUERY, GEM BOs with mmap, VM
 * contexts with per-mapping permissions, transfer and render contexts, DRM
 * syncobjs and SUBMIT_JOBS with the kernel's validation rules (those
 * include/uapi/sgxfive_drm.h states). Render jobs run on a small interpreter of our triangle scenes (VDM
 * state and index lists, vertex PDS, fill colours, the EOT's PBE state). Transfers run
 * synchronously on a tiny interpreter that follows the job's own pointers
 * through its VM (pixel-event PDS -> EOT -> PBE state, background object ->
 * PDS primary -> shader and texture words) and writes the pixels, so a job
 * that placed something wrong produces wrong pixels or a GPU fault. A fault
 * writes nothing and loses the context, as on hardware with recovery. A
 * render whose scene overflows its context's parameter buffer (a model of
 * the pages it needs, see mock.c) fails with -ENOSPC and keeps its context.
 */
#ifndef SGXFIVE_MOCK_H
#define SGXFIVE_MOCK_H

#include "sgxfive.h"

enum sgxfive_mock_layout {
	SGXFIVE_MOCK_LAYOUT_REV1 = 0,	/* our silicon: host bridge rev 3 */
	SGXFIVE_MOCK_LAYOUT_HARNESS,	/* the kernel's debugfs test addresses */
};

struct sgxfive_mock_config {
	enum sgxfive_mock_layout layout;
	const char *other_driver;	/* if set, renderD128 is this driver, sgxfive 129 */
	bool no_sgxfive;		/* no sgxfive node at all */
	const char *sgxfive_name;	/* driver name of the sgxfive node; NULL: "sgxfive" */
	uint32_t render_pb_pages;	/* render contexts' PB, 0x23-0x422; 0: 0x422 */
	/*
	 * the kernel's debugfs render_final_pb_pages: taken once by the next render context, whose
	 * render that closes a scene a geometry job opened has a PB of these pages (0x23-0x422,
	 * the context's own: 0 or any other value)
	 */
	uint32_t render_final_pb_pages;
	/*
	 * the kernel's debugfs render_bg_layer and render_bg_src: with the layer on, a render's
	 * background object is the one-layer form and its source must be set and mapped in the
	 * render's VM (else -EINVAL at submit); the background pixels are then the source's
	 * texels the layer's coordinates name
	 */
	bool bg_layer;
	uint32_t bg_src;
	/*
	 * The park race of E1085: the kernel parks a closed render context when its last
	 * reference goes, which can be after the close ioctl returns, and debugfs render_kept
	 * reads 0 bytes until then. With both set, a render context's close leaves
	 * debugfs_dir/render_kept empty for kept_park_ms, then puts its bytes back (a child
	 * process sleeps and renames render_kept.parking back); 0 or NULL: no park.
	 */
	const char *debugfs_dir;
	uint32_t kept_park_ms;
	/*
	 * the kernel's debugfs vm_pde_addr, vm_pde_size and vm_pde_layout (Q109): a VM_MAP at
	 * vm_pde_addr (0: off) must be exactly 4 MiB with a size code and layout the kernel makes a
	 * region for (codes 1-4 any layout, 0 and 5 dense or pt4k, 6 and 7 dense), else -EINVAL;
	 * the mock then maps the buffer as ever (the large page is not modelled)
	 */
	uint32_t vm_pde_addr, vm_pde_size, vm_pde_layout;
};

struct sgxfive_mock_stats {
	uint32_t bos, vms, ctxs, syncobjs;	/* live objects */
	uint32_t sync_files;			/* open sync_file fds */
	uint32_t mappings;
	uint32_t jobs_run, dummies_run, renders_run, faults;
	uint64_t last_fault_addr;
};

struct sgxfive_mock;

struct sgxfive_mock *sgxfive_mock_create(const struct sgxfive_mock_config *cfg);
void sgxfive_mock_destroy(struct sgxfive_mock *m);
const struct sgxfive_backend *sgxfive_mock_backend(struct sgxfive_mock *m);
void sgxfive_mock_get_stats(const struct sgxfive_mock *m, struct sgxfive_mock_stats *s);

#endif
