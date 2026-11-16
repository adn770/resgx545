// SPDX-License-Identifier: GPL-2.0-only OR MIT
/*
 * Host harness for the kernel's own-task code (drivers/gpu/drm/gma500/sgxfive/sgxfive_owntask.c
 * and sgx_fw.c), built with the shim headers of host/shim in place of the kernel's. It never
 * prints a firmware byte.
 *
 *   own_host verify FILE
 *       FILE is blobs, each a u32 little-endian length and that many bytes. Prints one line per
 *       blob: "OK", "EINVAL" (malformed), or "EPERM <reason>" (what sgx_own_verify() gives).
 *   own_host fw FW LAYOUT [BLOB SLOTS ENTRIES TRC RES]
 *       Builds the firmware buffers the way the kernel's load does (sgx_fw_build()), then, with a
 *       BLOB, applies the overlay (sgx_own_apply(): SLOTS the slot mask, ENTRIES the entry points
 *       as a comma list, TRC the temporaries field, RES the results page address, all in
 *       hexadecimal where numbers). Prints "buf <id> <sha256>" for each buffer, "code <sha256>"
 *       and "apply <return value>": digests and a status, no byte of any buffer. LAYOUT is
 *       fwdump's layout text ("addr <id> <hex>", "heap <id> <hex>", "pd_phys <hex>").
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <linux/unaligned.h>

#include "sgx_fw.h"
#include "sgx_own_regs.h"
#include "sgxfive_owntask.h"

static u8 *read_file(const char *path, size_t *len)
{
	FILE *f = fopen(path, "rb");
	u8 *data = NULL;
	long n;

	if (!f)
		return NULL;
	if (fseek(f, 0, SEEK_END) == 0 && (n = ftell(f)) >= 0 && fseek(f, 0, SEEK_SET) == 0 &&
	    (data = malloc(n ? n : 1)) && fread(data, 1, n, f) == (size_t)n) {
		*len = n;
	} else {
		free(data);
		data = NULL;
	}
	fclose(f);
	return data;
}

/* ---- sha256 ----------------------------------------------------------------------------------- */
static const u32 K[64] = {
	0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
	0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
	0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
	0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
	0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
	0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
	0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
	0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
};

#define ROR(x, n) ((x) >> (n) | (x) << (32 - (n)))

static void sha_block(u32 h[8], const u8 *p)
{
	u32 w[64], a, b, c, d, e, f, g, hh, t1, t2;
	int i;

	for (i = 0; i < 16; i++)
		w[i] = p[4 * i] << 24 | p[4 * i + 1] << 16 | p[4 * i + 2] << 8 | p[4 * i + 3];
	for (i = 16; i < 64; i++) {
		u32 s0 = ROR(w[i - 15], 7) ^ ROR(w[i - 15], 18) ^ (w[i - 15] >> 3);
		u32 s1 = ROR(w[i - 2], 17) ^ ROR(w[i - 2], 19) ^ (w[i - 2] >> 10);

		w[i] = w[i - 16] + s0 + w[i - 7] + s1;
	}
	a = h[0]; b = h[1]; c = h[2]; d = h[3]; e = h[4]; f = h[5]; g = h[6]; hh = h[7];
	for (i = 0; i < 64; i++) {
		t1 = hh + (ROR(e, 6) ^ ROR(e, 11) ^ ROR(e, 25)) + ((e & f) ^ (~e & g)) + K[i] + w[i];
		t2 = (ROR(a, 2) ^ ROR(a, 13) ^ ROR(a, 22)) + ((a & b) ^ (a & c) ^ (b & c));
		hh = g; g = f; f = e; e = d + t1; d = c; c = b; b = a; a = t1 + t2;
	}
	h[0] += a; h[1] += b; h[2] += c; h[3] += d; h[4] += e; h[5] += f; h[6] += g; h[7] += hh;
}

static void sha256_hex(const u8 *data, size_t len, char out[65])
{
	u32 h[8] = { 0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
		     0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19 };
	u8 tail[128];
	size_t i, n = len / 64 * 64, rem = len - n, tl;
	u64 bits = (u64)len * 8;

	for (i = 0; i < n; i += 64)
		sha_block(h, data + i);
	memset(tail, 0, sizeof(tail));
	memcpy(tail, data + n, rem);
	tail[rem] = 0x80;
	tl = rem < 56 ? 64 : 128;
	for (i = 0; i < 8; i++)
		tail[tl - 1 - i] = bits >> (8 * i);
	for (i = 0; i < tl; i += 64)
		sha_block(h, tail + i);
	for (i = 0; i < 8; i++)
		sprintf(out + 8 * i, "%08x", h[i]);
}

/* ---- verify ----------------------------------------------------------------------------------- */
static int do_verify(const char *path)
{
	size_t len, pos = 0;
	u8 *data = read_file(path, &len);

	if (!data)
		return 2;
	while (pos + 4 <= len) {
		u32 n = get_unaligned_le32(data + pos);
		struct sgx_own_blob b;
		const char *why = "";
		int ret;

		pos += 4;
		if (n > len - pos)
			return 2;
		ret = sgx_own_parse(data + pos, n, &b);
		if (!ret)
			ret = sgx_own_verify(&b, &why);
		if (!ret)
			puts("OK");
		else if (ret == -EINVAL)
			puts("EINVAL");
		else if (ret == -EPERM)
			printf("EPERM %s\n", why);
		else
			printf("ERR %d\n", ret);
		pos += n;
	}
	free(data);
	return 0;
}

/* ---- the firmware buffers --------------------------------------------------------------------- */
static int read_layout(const char *path, struct sgx_fw_layout *l)
{
	char line[256], key[16];
	unsigned long id, val;
	FILE *f = fopen(path, "r");

	if (!f)
		return -1;
	memset(l, 0, sizeof(*l));
	while (fgets(line, sizeof(line), f)) {
		if (sscanf(line, "%15s %lu %lx", key, &id, &val) == 3 && !strcmp(key, "addr") &&
		    id < SGX_FW_MAX_BUFFERS) {
			l->addr[id] = val;
			l->addr_set |= 1u << id;
		} else if (sscanf(line, "%15s %lu %lx", key, &id, &val) == 3 && !strcmp(key, "heap") &&
			   id < SGX_FW_MAX_HEAPS) {
			l->heap_base[id] = val;
			l->heap_set |= 1u << id;
		} else if (sscanf(line, "%15s %lx", key, &val) == 2 && !strcmp(key, "pd_phys")) {
			l->pd_phys = val;
		}
	}
	fclose(f);
	return 0;
}

static int do_fw(int argc, char **argv)
{
	u8 *bufs[SGX_FW_MAX_BUFFERS] = { NULL };
	static u8 code[SGX_OWN_CODE_SIZE];
	struct sgx_fw_layout l;
	struct sgx_fw fw;
	size_t len;
#ifndef HOST_NO_APPLY
	size_t blen = 0;
#endif
	u8 *data;
#ifndef HOST_NO_APPLY
	u8 *blob = NULL;
#endif
	char hex[65];
	unsigned int i;
	int ret;
#ifndef HOST_NO_APPLY
	int apply = 0;
#endif

	if (argc != 4 && argc != 9)
		return 2;
	data = read_file(argv[2], &len);
	if (!data || read_layout(argv[3], &l))
		return 2;
	ret = sgx_fw_parse(&fw, data, len);
	if (ret)
		return printf("parse %d\n", ret), 1;
	for (i = 0; i < fw.nbuffers; i++) {
		bufs[fw.buffers[i].id] = calloc(1, fw.buffers[i].size ? fw.buffers[i].size : 1);
		if (!bufs[fw.buffers[i].id])
			return 2;
	}
	ret = sgx_fw_build(&fw, &l, bufs);
	if (ret)
		return printf("build %d\n", ret), 1;
#ifndef HOST_NO_APPLY			/* before the overlay commit of the series there is no apply */
	if (argc == 9) {
		struct sgx_own_blob b;
		struct sgx_own_arm a = { .trc = SGX_OWN_TRC_STOCK };
		char *tok, *list = argv[6];

		blob = read_file(argv[4], &blen);
		if (!blob)
			return 2;
		a.slots = strtoul(argv[5], NULL, 16);
		while ((tok = strsep(&list, ",")) && *tok)
			a.entry[a.nentry++] = strtoul(tok, NULL, 10);
		a.trc = strtoul(argv[7], NULL, 0);
		a.trc_hazard = a.trc > SGX_OWN_TRC_FREE_MAX;
		apply = sgx_own_parse(blob, blen, &b);
		if (!apply)
			apply = sgx_own_apply(&b, &a, &fw, &l, SGXFIVE_OWN_PDS_BUF,
					      bufs[SGXFIVE_OWN_PDS_BUF],
					      sgx_fw_buffer(&fw, SGXFIVE_OWN_PDS_BUF)->size, code,
					      strtoul(argv[8], NULL, 16)
#ifdef HOST_APPLY_PDS			/* from the emitpds commit on: the image, none here */
					      , NULL
#endif
					      );
		printf("apply %d\n", apply);
	}
#endif
	for (i = 0; i < SGX_FW_MAX_BUFFERS; i++) {
		const struct sgx_fw_buffer *fb = bufs[i] ? sgx_fw_buffer(&fw, i) : NULL;

		if (!fb)
			continue;
		sha256_hex(bufs[i], fb->size, hex);
		printf("buf %u %s\n", i, hex);
	}
	sha256_hex(code, sizeof(code), hex);
	printf("code %s\n", hex);
	return 0;
}

int main(int argc, char **argv)
{
	if (argc == 3 && !strcmp(argv[1], "verify"))
		return do_verify(argv[2]);
	if (argc >= 4 && !strcmp(argv[1], "fw"))
		return do_fw(argc, argv);
	fprintf(stderr, "usage: own_host verify FILE | fw FW LAYOUT [BLOB SLOTS ENTRIES TRC RES]\n");
	return 2;
}
