/* SPDX-License-Identifier: MIT */
#ifndef HOST_LINUX_UNALIGNED_H
#define HOST_LINUX_UNALIGNED_H
#include <string.h>
#include <linux/types.h>

static inline u16 get_unaligned_le16(const void *p)
{
	const u8 *b = p;

	return b[0] | b[1] << 8;
}
static inline u32 get_unaligned_le32(const void *p)
{
	const u8 *b = p;

	return get_unaligned_le16(b) | (u32)get_unaligned_le16(b + 2) << 16;
}
static inline u64 get_unaligned_le64(const void *p)
{
	const u8 *b = p;

	return get_unaligned_le32(b) | (u64)get_unaligned_le32(b + 4) << 32;
}
static inline void put_unaligned_le32(u32 v, void *p)
{
	u8 *b = p;

	b[0] = v; b[1] = v >> 8; b[2] = v >> 16; b[3] = v >> 24;
}
static inline void put_unaligned_le64(u64 v, void *p)
{
	put_unaligned_le32((u32)v, p);
	put_unaligned_le32((u32)(v >> 32), (u8 *)p + 4);
}
#endif
