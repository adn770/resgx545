// SPDX-License-Identifier: MIT
/*
 * regwidth: which bits of SGX registers take a write, through /dev/mem, for the
 * campaign runner's regwidth tables (tools/campaign/regwidth.py).
 *
 *   sudo ./regwidth REGS        write test
 *   sudo ./regwidth -r REGS     read only
 *
 * REGS is a list of byte offsets in the register bank, "LO-HI" ranges or single
 * offsets, comma-separated, dword-aligned and below 0x1000. The write test reads
 * each register twice; if the two reads differ the register moves on its own and is
 * not written ("regwidth 0xOFFS moving A B"). Otherwise it writes all ones, reads,
 * writes the prior value back, reads, writes zero, reads, writes the prior value back
 * and reads, and prints
 *
 *   regwidth 0xOFFS prior P ones O back B zero Z restored R
 *
 * so that a register spends as little time as possible away from its value. A
 * register that does not read its prior value at the end is written once more and
 * the program stops (exit 3). The read-only mode prints "regval 0xOFFS 0xVALUE".
 *
 * Whatever it is asked, the program never writes a register of its deny list (the
 * clock gating, soft reset, event, start, cache invalidate, USSE slot and service
 * queue, EDM and BIF/MMU registers): a list that names one is refused before anything
 * is written (exit 2). The bank is at physical 0x80080000 (the laptop's);
 * REGWIDTH_BASE overrides it and REGWIDTH_MEM the file (/dev/mem), which lets the
 * tests use a plain file. Exit 2 on usage errors.
 *
 * Every register access goes through reg_read() and reg_write(). A build with
 * -DREGWIDTH_TEST adds faults for the tests, which a plain file cannot show: with
 * REGWIDTH_DROP=OFF the register at OFF takes only its first three writes (so the
 * restore fails), with REGWIDTH_MOVING=OFF each read of OFF returns one more than the
 * last (a register that moves on its own); it logs each write on stderr.
 */
#define _GNU_SOURCE
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

#define BANK_BASE	0x80080000ull
#define BANK_SIZE	0x1000u
#define MAX_REGS	(BANK_SIZE / 4)

/* Never written, whatever the table says: inclusive offset ranges. */
static const uint32_t deny[][2] = {
	{ 0x0000, 0x000c },	/* clock gating control, status, override */
	{ 0x0080, 0x0080 },	/* soft reset */
	{ 0x0110, 0x0144 },	/* event enable, clear, status; PDS cache events; timer */
	{ 0x0200, 0x0200 },	/* VDM start */
	{ 0x0224, 0x0224 },	/* TE tail-pointer cache clear and flush */
	{ 0x024c, 0x024c },	/* MTE OTPM operation */
	{ 0x0428, 0x0428 },	/* ISP start render */
	{ 0x0430, 0x0430 },	/* a write the kernel's register file treats as starting work */
	{ 0x043c, 0x043c },	/* TSP parameter cache invalidate */
	{ 0x0450, 0x0450 },	/* a write the kernel's register file treats as starting work */
	{ 0x063c, 0x063c },	/* DPM 3D deallocate */
	{ 0x0648, 0x064c },	/* DPM TA allocate, DPM 3D */
	{ 0x0658, 0x0658 },	/* DPM partial render */
	{ 0x0680, 0x06a0 },	/* DPM tasks, out-of-memory response, free context */
	{ 0x0804, 0x0804 },	/* cache control: invalidates */
	{ 0x0a08, 0x0a08 },	/* USSE instruction cache invalidate */
	{ 0x0a0c, 0x0a48 },	/* USSE code bases, the EDM's (15) among them */
	{ 0x0a58, 0x0a70 },	/* event-to-PDS enable and the event PDS programs */
	{ 0x0aa4, 0x0aa8 },	/* USSE slot allocation, USSE 0 and 1 */
	{ 0x0ab8, 0x0ab8 },	/* PDS execution base */
	{ 0x0ac4, 0x0aec },	/* event kicker, kicks, EDM timer, PDS invalidates */
	{ 0x0b0c, 0x0b20 },	/* USSE 0 and 1 service queues, the EDM task registers */
	{ 0x0b80, 0x0b98 },	/* USSE slot allocation and service queues, USSE 2 and 3 */
	{ 0x0c00, 0x0cfc },	/* BIF: MMU control, faults, directories, banks, requestors */
	{ 0x0e80, 0x0e80 },	/* HWPerf pulse */
};

#ifdef REGWIDTH_TEST
static long fault_drop = -1, fault_moving = -1;
static unsigned int drop_writes, moving_reads;

static uint32_t reg_read(volatile uint32_t *m, uint32_t off)
{
	uint32_t v = m[off / 4];

	if ((long)off == fault_moving)
		v += ++moving_reads;
	return v;
}

static void reg_write(volatile uint32_t *m, uint32_t off, uint32_t v)
{
	fprintf(stderr, "write 0x%04x 0x%08x\n", off, v);
	if ((long)off == fault_drop && ++drop_writes > 3)
		return;
	m[off / 4] = v;
}

static void faults(void)
{
	const char *d = getenv("REGWIDTH_DROP"), *mv = getenv("REGWIDTH_MOVING");

	if (d)
		fault_drop = strtol(d, NULL, 0);
	if (mv)
		fault_moving = strtol(mv, NULL, 0);
}
#else
static uint32_t reg_read(volatile uint32_t *m, uint32_t off)
{
	return m[off / 4];
}

static void reg_write(volatile uint32_t *m, uint32_t off, uint32_t v)
{
	m[off / 4] = v;
}

static void faults(void)
{
}
#endif

static int usage(void)
{
	fprintf(stderr, "usage: regwidth [-r] LO-HI[,LO-HI...]\n");
	return 2;
}

static int denied(uint32_t off)
{
	for (size_t i = 0; i < sizeof(deny) / sizeof(deny[0]); i++)
		if (off >= deny[i][0] && off <= deny[i][1])
			return 1;
	return 0;
}

/* One offset: a number, dword-aligned, inside the bank. */
static int parse_off(const char *s, char **end, uint32_t *off)
{
	unsigned long v = strtoul(s, end, 0);

	if (*end == s || v % 4 || v >= BANK_SIZE)
		return -1;
	*off = (uint32_t)v;
	return 0;
}

/* REGS into offs; the count, or -1. */
static int parse_regs(const char *s, uint32_t *offs)
{
	int n = 0;

	for (;;) {
		uint32_t lo, hi;
		char *end;

		if (parse_off(s, &end, &lo))
			return -1;
		hi = lo;
		if (*end == '-' && parse_off(end + 1, &end, &hi))
			return -1;
		if (hi < lo || n + (int)((hi - lo) / 4 + 1) > (int)MAX_REGS)
			return -1;
		for (uint32_t o = lo; o <= hi; o += 4)
			offs[n++] = o;
		if (!*end)
			return n;
		if (*end != ',')
			return -1;
		s = end + 1;
	}
}

int main(int argc, char **argv)
{
	static uint32_t offs[MAX_REGS];
	const char *memf = getenv("REGWIDTH_MEM"), *basev = getenv("REGWIDTH_BASE");
	const unsigned long long base = basev ? strtoull(basev, NULL, 0) : BANK_BASE;
	volatile uint32_t *m;
	int ro = 0, n, fd;

	faults();
	if (argc == 3 && !strcmp(argv[1], "-r"))
		ro = 1;
	else if (argc != 2 || argv[1][0] == '-')
		return usage();
	n = parse_regs(argv[argc - 1], offs);
	if (n <= 0)
		return usage();
	if (!ro)
		for (int i = 0; i < n; i++)
			if (denied(offs[i])) {
				fprintf(stderr, "regwidth: 0x%04x is on the deny list\n", offs[i]);
				return 2;
			}
	fd = open(memf ? memf : "/dev/mem", (ro ? O_RDONLY : O_RDWR) | O_SYNC);
	if (fd < 0) {
		perror(memf ? memf : "/dev/mem");
		return 1;
	}
	m = mmap(NULL, BANK_SIZE, ro ? PROT_READ : PROT_READ | PROT_WRITE, MAP_SHARED, fd,
		 (off_t)base);
	close(fd);
	if (m == MAP_FAILED) {
		perror("mmap");
		return 1;
	}
	for (int i = 0; i < n; i++) {
		const uint32_t o = offs[i];
		uint32_t p, p2, ones, back, zero, rest;

		if (ro) {
			printf("regval 0x%04x 0x%08x\n", o, reg_read(m, o));
			continue;
		}
		p = reg_read(m, o);
		p2 = reg_read(m, o);
		if (p != p2) {
			printf("regwidth 0x%04x moving 0x%08x 0x%08x\n", o, p, p2);
			continue;
		}
		reg_write(m, o, 0xffffffffu);
		ones = reg_read(m, o);
		reg_write(m, o, p);
		back = reg_read(m, o);
		reg_write(m, o, 0);
		zero = reg_read(m, o);
		reg_write(m, o, p);
		rest = reg_read(m, o);
		printf("regwidth 0x%04x prior 0x%08x ones 0x%08x back 0x%08x zero 0x%08x "
		       "restored 0x%08x\n", o, p, ones, back, zero, rest);
		fflush(stdout);
		if (rest != p) {
			reg_write(m, o, p);
			printf("regwidth 0x%04x not restored: reads 0x%08x\n", o, reg_read(m, o));
			return 3;
		}
	}
	munmap((void *)m, BANK_SIZE);
	return 0;
}
