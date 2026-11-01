/* SPDX-License-Identifier: MIT */
#ifndef HOST_LINUX_KSTRTOX_H
#define HOST_LINUX_KSTRTOX_H
#include <errno.h>
#include <stdlib.h>
#include <linux/types.h>

static inline int kstrtouint(const char *s, unsigned int base, unsigned int *res)
{
	char *end;
	unsigned long v;

	if (!*s || *s == '-')
		return -EINVAL;
	errno = 0;
	v = strtoul(s, &end, base);
	if (errno || *end || v > 0xffffffffUL)
		return -EINVAL;
	*res = v;
	return 0;
}
#endif
