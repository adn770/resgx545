/* SPDX-License-Identifier: MIT */
/* Host shim for the kernel headers sgx_render.c and sgx_xfer.c include (tools/fwsim/host). */
#ifndef HOST_LINUX_BITS_H
#define HOST_LINUX_BITS_H
#include <linux/types.h>

#define BIT(n)		(1u << (n))
#define GENMASK(h, l)	((~0u >> (31 - (h))) & (~0u << (l)))
#endif
