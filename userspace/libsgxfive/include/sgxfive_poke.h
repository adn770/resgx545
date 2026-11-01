/* SPDX-License-Identifier: MIT */
/*
 * Pokes: changes to the words of a built job, made right before it is
 * submitted, for sweeps (one job run many times with one word changed each
 * time). A poke addresses one word by
 * space and index, never by a name: SPACE:INDEX=VALUE sets it and
 * SPACE:INDEX^=VALUE flips the bits of VALUE in whatever the job would have
 * written. The spaces:
 *
 *   cmd:N        dword N of the render command (struct drm_sgxfive_render_cmd)
 *   xfer:N       dword N of the transfer command (struct drm_sgxfive_transfer_cmd)
 *   vdm:N        word N of the triangle's VDM stream
 *   eos:N        word N of the triangle's end-of-scene state block
 *   blk:N        word N of the triangle's state block
 *   pds:SLOT:N   data dword N of the PDS program in SLOT
 *   tex:N        texture word TN of a copy (in its PDS primary's data)
 *   bg:N         word N of a fill's or copy's background object
 *
 * Which spaces and slots a job has, and their sizes, come from the job's
 * layout (sgxfive_render_poke_layout, sgxfive_xfer_poke_layout). The engines
 * need only the types here; the functions are in src/poke.c.
 */
#ifndef SGXFIVE_POKE_H
#define SGXFIVE_POKE_H

#include <stdbool.h>
#include <stdint.h>

enum sgxfive_poke_space {
	SGXFIVE_POKE_CMD,
	SGXFIVE_POKE_XFER,
	SGXFIVE_POKE_VDM,
	SGXFIVE_POKE_EOS,
	SGXFIVE_POKE_BLK,
	SGXFIVE_POKE_PDS,
	SGXFIVE_POKE_TEX,
	SGXFIVE_POKE_BG,
	SGXFIVE_POKE_SPACE_COUNT,
};

#define SGXFIVE_POKE_SLOT_MAX	16	/* a slot name and its NUL */
#define SGXFIVE_POKE_VIEWS_MAX	16	/* the most views a job has */
#define SGXFIVE_POKE_MAX	64	/* the most pokes a command line takes */

struct sgxfive_poke {
	uint32_t space;				/* enum sgxfive_poke_space */
	char slot[SGXFIVE_POKE_SLOT_MAX];	/* pds: the program's slot; else "" */
	uint32_t index;
	uint32_t value;
	bool flip;				/* ^=: XOR value in; =: set to value */
};

/*
 * A range of words a job exposes: word i is words[map ? map[i] : i]. words is
 * NULL in a layout (sizes only).
 */
struct sgxfive_poke_view {
	uint32_t space;
	const char *slot;			/* pds: the slot's name; else NULL */
	uint32_t *words;
	uint32_t count;
	const uint8_t *map;
};

/*
 * A function the engines call with the views of a built job right before
 * they submit it (sgxfive_xfer_set_hook, sgxfive_render_set_hook); a
 * non-zero return fails the job unsubmitted with that error.
 */
typedef int (*sgxfive_job_hook)(void *priv, const struct sgxfive_poke_view *v, unsigned int n);

/* Pokes as a job hook: priv is a struct sgxfive_poke_set; sgxfive_poke_apply's errors. */
struct sgxfive_poke_set {
	const struct sgxfive_poke *pk;
	unsigned int n;
};
int sgxfive_poke_hook(void *priv, const struct sgxfive_poke_view *v, unsigned int n);

/* "cmd", "xfer", ...; NULL for an unknown space. */
const char *sgxfive_poke_space_name(uint32_t space);

/* Parse SPACE[:SLOT]:INDEX=VALUE or ^=VALUE (numbers as strtoul base 0). -EINVAL. */
int sgxfive_poke_parse(const char *arg, struct sgxfive_poke *pk);

/*
 * The view a poke addresses: 0, -ENOENT when the job has no such space or
 * slot, -ERANGE when the index is past the view's end.
 */
int sgxfive_poke_find(const struct sgxfive_poke_view *v, unsigned int nv,
		      const struct sgxfive_poke *pk, const struct sgxfive_poke_view **out);

/*
 * Check every poke against the views, then apply them in order. On an error
 * nothing is written and *bad (if not NULL) is the failing poke's index.
 */
int sgxfive_poke_apply(const struct sgxfive_poke_view *v, unsigned int nv,
		       const struct sgxfive_poke *pk, unsigned int n, unsigned int *bad);

/* 64-bit FNV-1a of n dwords, as little-endian bytes: the hash of a target. */
uint64_t sgxfive_hash_dwords(const uint32_t *p, uint64_t n);

#endif
