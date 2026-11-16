/* SPDX-License-Identifier: MIT */
#ifndef HOST_LINUX_MATH64_H
#define HOST_LINUX_MATH64_H
#include <linux/types.h>

static inline u64 div_u64(u64 n, u32 d)
{
	return n / d;
}

static inline u64 div_u64_rem(u64 n, u32 d, u32 *rem)
{
	*rem = n % d;
	return n / d;
}
#endif
