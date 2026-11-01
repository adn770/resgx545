+++
id = "E486"
claim = "In a client pixel task (a proxy: not a firmware task), a register past the allocation reads back as the register whose index is the register's modulo the allocation in most pixels, and a write to it was not seen to reach that register: with --temps 8, 16, 32 and 64, r(n) for n of the allocation T and above reads the marker written to r(n mod T) in 88 to 99.6 percent of the 2048 pixels in 15 of 15 cases that write nothing to r(n) (T = 8: r10, r11, r18, r29; T = 16: r18, r19, r34, r53; T = 32: r34, r35, r66, r101; T = 64: r66, r67, r123), reads the scratch pointer held in r1 for r(T + 1) in 2040 and 1968 pixels of two cases (r9 with T = 8, r33 with T = 32), and in 4 of 4 cases at T = 8 and 32 (none at 16 and 64) that also write a marker to r(n) (r12 and r108 with T = 8, r36 and r48 with T = 32) the pixels and r(n mod T) read the value written to r(n mod T), not the one written to r(n), the rest of the pixels reading other values; the 5 further cases with n a multiple of T (r8, r24, r48 with T = 8; r32, r96 with T = 32) read varying leftovers of earlier jobs"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1122 (sha256 ec423efc3d9aa34576553da70916be4ceb715a729cbc02cc4bd89fa052511244): probes/usse/temps-past.toml probes t008 (6 cases) and t032 (5 cases), two runs (probe.py, then the campaign, the dataset: the same value for the four cases that read r(n mod T) and the same pointer in the two r(T + 1) cases, the printed pixel lists differing in 5 of the 11 cases, those that read r0 among them), and probes/usse/temps-wrap.toml (4 probes, 15 cases: only r(n mod T) is written, r(n) is read; the follow-up under a new name; the campaign, the dataset, and a second probe.py run: the most frequent value the same in 15 of 15 and its count different in 3 (2040 and 2016, 1984 and 1986, 1887 and 1888), the printed lists in 7; the second run's counts are 1808 to 2016)"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-temps-past", "usse-temps-wrap"]
terms = []
+++

**What runs.** temps-past: a fill with `--temps T` (8 or 32) writes marker Ml to r(lo) and Mh to
r(T + d) with d = 0, 1, 4, 16, 40, 100 (T = 8) or 0, 1, 4, 16, 64 (T = 32), lo = (T + d) mod T (2
when 0 or 1), stores r(lo) to dword 0 and reads r(T + d) as the pixel. temps-wrap: only Ml is
written (to r(n mod T)) and r(n) is the pixel, for T = 8, 16, 32, 64 and n = T + 2, T + 3, 2T + 2,
3T + 5 (T = 64: 66, 67, 123).

**Results (temps-wrap, 15 of 15).** The most frequent pixel value is the marker of r(n mod T) in
every case: T = 8 with n = 10, 11, 18, 29 in 2016, 2040, 1984, 1952 pixels; T = 16 (18, 19, 34, 53)
in 2016, 2016, 1984, 1952; T = 32 (34, 35, 66, 101) in 1968, 1969, 1890, 1808; T = 64 (66, 67, 123)
in 1888, 1888, 1887 of 2048. The other pixels hold other values (leftovers, or r(n) of a
neighbouring instance [infer]). temps-past: reading r9 (T = 8) and r33 (T = 32), whose index mod T
is 1, returns 0x3E003000, the scratch address r1 holds (2040 and 1968 pixels); r12, r108 (T = 8)
and r36, r48 (T = 32) return r4's (or r16's) marker Ml in 2016, 1632, 1968 and 1968 pixels, never
the Mh just written to them; r8, r24, r48 (T = 8) and r32, r96 (T = 32), whose index mod T is 0,
return varying leftover values (the markers of earlier probes among them). No case faulted or hung.

**What it shows.** [HW] In a client pixel task, a majority of the pixels (1808 to 2040 of 2048,
88.3 to 99.6 percent) read r(n mod T) for r(n) past the allocation: by T, 95.3 to 99.6 percent at
T = 8 (1952 to 2040), 95.3 to 98.4 at T = 16 (1952 to 2016), 88.3 to 96.1 at T = 32 (1808 to
1969) and 92.1 to 92.2 at T = 64 (1887 and 1888). The rule is "most pixels", not an exact one: the
fraction follows T and n, not n/T (T = 64 with n = 66 is lower than T = 8 with n = 29), the other
pixels read other values, and the probe.py run of the same cases gave a different count in 3 of 15
cases. The write past the allocation was not seen to reach the register read (4 of 4, at T = 8 and
32 only): it is dropped or lands in another instance's storage [infer]. So an allocation smaller
than the highest register a program uses does not fault: it reads another register, in most
pixels. A task must ask for the temporaries it uses (E487). What the other pixels read is not
known.

**What it does not show.** A firmware task (these are pixel tasks of client fills); whether the
write is dropped at T = 16 and 64 (not run with a marker written past the allocation); which
instance's registers the other pixels read; whether the write past
the allocation lands in a neighbour (Q132); the case of an allocation of 4; allocations of 8, 16,
32 and 64 only, no other value (the read wrap is shown at those four sizes, modulo T there).
