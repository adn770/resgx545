// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
/*
 * The user's side of one default triangle render (sgxfive-test `tri`, its first render: the
 * default triangle in green on 0xff203040), built by libsgxfive against its in-process mock of
 * the render node: the library chooses every address it maps, so the command is the one the tool
 * submitted on the laptop. Linked with libsgxfive at the tool's commit (tools/fwsim/kick.py).
 *
 *   tri_cmd WIDTH HEIGHT
 *       Prints "cmd:N=0x..." for each dword of the struct drm_sgxfive_render_cmd.
 */
#include <stdio.h>
#include <stdlib.h>

#include "sgxfive.h"
#include "sgxfive_mock.h"
#include "sgxfive_render.h"

int main(int argc, char **argv)
{
	struct sgxfive_mock_config cfg = { 0 };
	struct sgxfive_mock *m;
	struct sgxfive_dev *dev = NULL;
	struct sgxfive_vm *vm = NULL;
	struct sgxfive_render *r = NULL;
	struct sgxfive_tri_params p;
	const uint32_t *cw;
	uint32_t ctx, w, h;
	int ret;

	if (argc != 3)
		return 2;
	w = strtoul(argv[1], NULL, 0);
	h = strtoul(argv[2], NULL, 0);
	m = sgxfive_mock_create(&cfg);
	ret = m ? sgxfive_dev_open(sgxfive_mock_backend(m), NULL, &dev) : -1;
	if (!ret)
		ret = sgxfive_vm_create(dev, &vm);
	if (!ret)
		ret = sgxfive_render_ctx_create_flags(vm, w, h, 0, &ctx);
	if (!ret)
		ret = sgxfive_render_create(vm, ctx, &r);
	if (!ret) {
		/* sgxfive-test tri, render 1 (colours[0]) */
		sgxfive_tri_default(&p, w, h);
		p.bg_src = 0;
		p.colour = 0xff00ff00;
		p.bg_colour = 0xff203040;
		ret = sgxfive_render_tri_flags(r, &p, 0, 0, 0);
	}
	if (ret) {
		fprintf(stderr, "tri_cmd: %d\n", ret);
		return 1;
	}
	cw = (const uint32_t *)sgxfive_render_last_cmd(r);
	for (unsigned int i = 0; i < sizeof(struct drm_sgxfive_render_cmd) / 4; i++)
		printf("cmd:%u=0x%08x\n", i, cw[i]);
	sgxfive_render_wait(r, 1000000000);
	sgxfive_render_destroy(r);
	sgxfive_vm_destroy(vm);
	sgxfive_dev_close(dev);
	sgxfive_mock_destroy(m);
	return 0;
}
