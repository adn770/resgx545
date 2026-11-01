/* SPDX-License-Identifier: MIT */
#ifndef HOST_LINUX_BITOPS_H
#define HOST_LINUX_BITOPS_H
#include <linux/types.h>

static inline unsigned int hweight32(u32 v)
{
	return __builtin_popcount(v);
}
#endif
