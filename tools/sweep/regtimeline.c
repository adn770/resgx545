// SPDX-License-Identifier: MIT
/*
 * regtimeline: a timeline of SGX registers around one command, read-only
 * through /dev/mem, for the sweep probes (tools/sweep).
 *
 *   sudo ./regtimeline TOTAL LEAD REGS -- COMMAND...
 *
 * REGS is a list of byte offsets in the register bank, "LO-HI" ranges or
 * single offsets, comma-separated (0x0484-0x0490,0x0740), dword-aligned and
 * below 0x4000. The registers are sampled in a tight loop; COMMAND starts
 * after LEAD seconds with the same stdout; sampling goes on for TOTAL seconds
 * (and until COMMAND exits; TOTAL 0 samples only while it runs). Then, after
 * COMMAND's own output:
 *
 *   timeline: regs 0x0484 ... samples N seconds T start NS end NS rc R
 *   tl T_NS V0 V1 ...       one line per change of any register (the first
 *                           sample too), T_NS from the start, values in hex
 *
 * The bank is at physical 0x80080000 (the laptop's); REGTIMELINE_BASE
 * overrides it and REGTIMELINE_MEM the file (/dev/mem), which lets the tests
 * sample a plain file. Nothing is ever written. Exit 2 on usage errors, else
 * COMMAND's exit status (125 if it did not exit normally).
 */
#define _GNU_SOURCE
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

#define BANK_BASE	0x80080000ull
#define BANK_SIZE	0x4000u
#define MAX_REGS	(BANK_SIZE / 4)
#define STORE_BYTES	(64u << 20)	/* the changes kept, at most */

static uint64_t now_ns(void)
{
	struct timespec t;

	clock_gettime(CLOCK_MONOTONIC, &t);
	return (uint64_t)t.tv_sec * 1000000000u + (uint64_t)t.tv_nsec;
}

static int usage(void)
{
	fprintf(stderr, "usage: regtimeline TOTAL LEAD LO-HI[,LO-HI...] -- COMMAND...\n");
	return 2;
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

static int wait_rc(pid_t pid, int flags, int *rc)
{
	int st;

	if (waitpid(pid, &st, flags) != pid)
		return 0;
	*rc = WIFEXITED(st) ? WEXITSTATUS(st) : -1;
	return 1;
}

int main(int argc, char **argv)
{
	static uint32_t offs[MAX_REGS];
	const char *memf = getenv("REGTIMELINE_MEM"), *basev = getenv("REGTIMELINE_BASE");
	const unsigned long long base = basev ? strtoull(basev, NULL, 0) : BANK_BASE;
	uint64_t t0, end, go, start = 0, stop = 0, samples = 0, maxch;
	uint32_t *ch, *prev, *cur, maxoff = 0;
	uint64_t *ct, nch = 0;
	volatile const uint32_t *m;
	double total, lead;
	size_t len;
	pid_t pid = 0;
	int n, fd, rc = -1;

	if (argc < 6 || strcmp(argv[4], "--"))
		return usage();
	total = atof(argv[1]);
	lead = atof(argv[2]);
	n = parse_regs(argv[3], offs);
	if (n <= 0 || total < 0 || lead < 0)
		return usage();
	for (int i = 0; i < n; i++)
		maxoff = offs[i] > maxoff ? offs[i] : maxoff;
	len = ((size_t)maxoff + 4 + 4095) & ~(size_t)4095;
	fd = open(memf ? memf : "/dev/mem", O_RDONLY | O_SYNC);
	if (fd < 0) {
		perror(memf ? memf : "/dev/mem");
		return 1;
	}
	m = mmap(NULL, len, PROT_READ, MAP_SHARED, fd, (off_t)base);
	close(fd);
	if (m == MAP_FAILED) {
		perror("mmap");
		return 1;
	}
	maxch = STORE_BYTES / (4ull * n + 8);
	ch = malloc(maxch * 4 * n);
	ct = malloc(maxch * 8);
	prev = calloc(n, 4);
	cur = calloc(n, 4);
	if (!ch || !ct || !prev || !cur) {
		perror("malloc");
		return 1;
	}
	fflush(stdout);
	t0 = now_ns();
	end = t0 + (uint64_t)(total * 1e9);
	go = t0 + (uint64_t)(lead * 1e9);
	for (uint64_t t; (t = now_ns()) < end || !pid || !stop;) {
		if (!pid && t >= go) {
			start = t;
			pid = fork();
			if (!pid) {
				execvp(argv[5], argv + 5);
				_exit(127);
			}
			if (pid < 0) {
				perror("fork");
				return 1;
			}
		}
		if (pid > 0 && !stop && wait_rc(pid, WNOHANG, &rc))
			stop = now_ns();
		for (int r = 0; r < n; r++)
			cur[r] = m[offs[r] / 4];
		samples++;
		if ((!nch || memcmp(cur, prev, 4ull * n)) && nch < maxch) {
			memcpy(ch + nch * n, cur, 4ull * n);
			ct[nch++] = t - t0;
			memcpy(prev, cur, 4ull * n);
		}
		if (total > 0 && t >= end && pid > 0 && !stop) {
			/* sampling is over: just wait for the command */
			wait_rc(pid, 0, &rc);
			stop = now_ns();
		}
	}
	printf("timeline: regs");
	for (int r = 0; r < n; r++)
		printf(" 0x%04x", offs[r]);
	printf(" samples %llu seconds %g start %llu end %llu rc %d\n",
	       (unsigned long long)samples, total, (unsigned long long)(start - t0),
	       (unsigned long long)(stop - t0), rc);
	for (uint64_t i = 0; i < nch; i++) {
		printf("tl %llu", (unsigned long long)ct[i]);
		for (int r = 0; r < n; r++)
			printf(" %08x", ch[i * n + r]);
		putchar('\n');
	}
	munmap((void *)m, len);
	return rc < 0 ? 125 : rc;
}
