// SPDX-License-Identifier: MIT
/*
 * Pokes (include/sgxfive_poke.h): parse SPACE[:SLOT]:INDEX=VALUE and ^=VALUE,
 * find the word a poke addresses among a job's views, check and apply.
 */
#include <errno.h>
#include <stdlib.h>
#include <string.h>

#include "sgxfive_poke.h"

static const char *const space_names[SGXFIVE_POKE_SPACE_COUNT] = {
	[SGXFIVE_POKE_CMD] = "cmd", [SGXFIVE_POKE_XFER] = "xfer", [SGXFIVE_POKE_VDM] = "vdm",
	[SGXFIVE_POKE_EOS] = "eos", [SGXFIVE_POKE_BLK] = "blk", [SGXFIVE_POKE_PDS] = "pds",
	[SGXFIVE_POKE_TEX] = "tex", [SGXFIVE_POKE_BG] = "bg",
};

const char *sgxfive_poke_space_name(uint32_t space)
{
	return space < SGXFIVE_POKE_SPACE_COUNT ? space_names[space] : NULL;
}

/* A whole unsigned 32-bit number (strtoull base 0) in s[0..len). */
static int parse_num(const char *s, size_t len, uint32_t *v)
{
	char buf[24], *end;
	unsigned long long x;

	if (!len || len >= sizeof(buf) || s[0] == '-' || s[0] == '+' || s[0] == ' ')
		return -EINVAL;
	memcpy(buf, s, len);
	buf[len] = 0;
	errno = 0;
	x = strtoull(buf, &end, 0);
	if (errno || *end || x > 0xffffffffull)
		return -EINVAL;
	*v = (uint32_t)x;
	return 0;
}

int sgxfive_poke_parse(const char *arg, struct sgxfive_poke *pk)
{
	const char *op = strchr(arg, '='), *colon = strchr(arg, ':'), *idx;
	struct sgxfive_poke p = { 0 };
	size_t len;

	if (!op || !colon || colon > op)
		return -EINVAL;
	len = (size_t)(colon - arg);
	p.space = SGXFIVE_POKE_SPACE_COUNT;
	for (uint32_t s = 0; s < SGXFIVE_POKE_SPACE_COUNT; s++)
		if (strlen(space_names[s]) == len && !strncmp(arg, space_names[s], len))
			p.space = s;
	if (p.space == SGXFIVE_POKE_SPACE_COUNT)
		return -EINVAL;
	idx = colon + 1;
	if (p.space == SGXFIVE_POKE_PDS) {
		const char *c2 = strchr(idx, ':');

		if (!c2 || c2 > op || c2 == idx || (size_t)(c2 - idx) >= sizeof(p.slot))
			return -EINVAL;
		memcpy(p.slot, idx, (size_t)(c2 - idx));
		idx = c2 + 1;
	}
	if (op > idx && op[-1] == '^') {
		p.flip = true;
		op--;
	}
	if (parse_num(idx, (size_t)(op - idx), &p.index))
		return -EINVAL;
	op += p.flip ? 2 : 1;
	if (parse_num(op, strlen(op), &p.value))
		return -EINVAL;
	*pk = p;
	return 0;
}

int sgxfive_poke_find(const struct sgxfive_poke_view *v, unsigned int nv,
		      const struct sgxfive_poke *pk, const struct sgxfive_poke_view **out)
{
	for (unsigned int i = 0; i < nv; i++) {
		if (v[i].space != pk->space)
			continue;
		if (pk->space == SGXFIVE_POKE_PDS && (!v[i].slot || strcmp(v[i].slot, pk->slot)))
			continue;
		if (pk->index >= v[i].count)
			return -ERANGE;
		*out = &v[i];
		return 0;
	}
	return -ENOENT;
}

int sgxfive_poke_apply(const struct sgxfive_poke_view *v, unsigned int nv,
		       const struct sgxfive_poke *pk, unsigned int n, unsigned int *bad)
{
	const struct sgxfive_poke_view *got;

	for (unsigned int i = 0; i < n; i++) {
		int ret = sgxfive_poke_find(v, nv, &pk[i], &got);

		if (!ret && !got->words)
			ret = -EINVAL;		/* a layout: nothing to write to */
		if (ret) {
			if (bad)
				*bad = i;
			return ret;
		}
	}
	for (unsigned int i = 0; i < n; i++) {
		uint32_t *w;

		sgxfive_poke_find(v, nv, &pk[i], &got);
		w = &got->words[got->map ? got->map[pk[i].index] : pk[i].index];
		*w = pk[i].flip ? *w ^ pk[i].value : pk[i].value;
	}
	return 0;
}

int sgxfive_poke_hook(void *priv, const struct sgxfive_poke_view *v, unsigned int n)
{
	const struct sgxfive_poke_set *s = priv;

	return sgxfive_poke_apply(v, n, s->pk, s->n, NULL);
}

uint64_t sgxfive_hash_dwords(const uint32_t *p, uint64_t n)
{
	uint64_t h = 0xcbf29ce484222325ull;

	for (uint64_t i = 0; i < n; i++)
		for (unsigned int b = 0; b < 4; b++) {
			h ^= (p[i] >> (8 * b)) & 0xff;
			h *= 0x100000001b3ull;
		}
	return h;
}
