/* SPDX-License-Identifier: MIT */
#ifndef HOST_LINUX_SLAB_H
#define HOST_LINUX_SLAB_H
#include <stdlib.h>

#define GFP_KERNEL 0
static inline void *kvzalloc(size_t n, int flags)
{
	(void)flags;
	return calloc(1, n);
}
static inline void kvfree(void *p)
{
	free(p);
}
#endif
