/* SPDX-License-Identifier: MIT */
#ifndef HOST_LINUX_STRING_H
#define HOST_LINUX_STRING_H
#include <ctype.h>
#include <string.h>
#include <linux/types.h>

static inline ssize_t strscpy(char *d, const char *s, size_t n)
{
	size_t l = strlen(s);

	if (l >= n)
		return -7;			/* -E2BIG */
	memcpy(d, s, l + 1);
	return l;
}

static inline char *strim(char *s)
{
	size_t n;

	while (isspace((unsigned char)*s))
		s++;
	n = strlen(s);
	while (n && isspace((unsigned char)s[n - 1]))
		s[--n] = 0;
	return s;
}
#endif
