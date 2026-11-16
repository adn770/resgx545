/* SPDX-License-Identifier: MIT */
#ifndef HOST_LINUX_KERNEL_H
#define HOST_LINUX_KERNEL_H
#include <linux/types.h>

#define DIV_ROUND_UP(n, d)	(((n) + (d) - 1) / (d))
#define round_up(x, y)		((((x) - 1) | ((__typeof__(x))((y) - 1))) + 1)
#define round_down(x, y)	((x) & ~((__typeof__(x))((y) - 1)))
#define ALIGN(x, a)		(((x) + (a) - 1) & ~((__typeof__(x))(a) - 1))
#define IS_ALIGNED(x, a)	(((x) & ((__typeof__(x))(a) - 1)) == 0)
#define max(a, b)		((a) > (b) ? (a) : (b))
#define min(a, b)		((a) < (b) ? (a) : (b))
#define max_t(t, a, b)		((t)(a) > (t)(b) ? (t)(a) : (t)(b))
#define min_t(t, a, b)		((t)(a) < (t)(b) ? (t)(a) : (t)(b))
#define clamp(v, lo, hi)	min(max(v, lo), hi)
#ifndef READ_ONCE
#define READ_ONCE(x)		(*(const volatile __typeof__(x) *)&(x))
#define WRITE_ONCE(x, v)	(*(volatile __typeof__(x) *)&(x) = (v))
#endif
#endif
