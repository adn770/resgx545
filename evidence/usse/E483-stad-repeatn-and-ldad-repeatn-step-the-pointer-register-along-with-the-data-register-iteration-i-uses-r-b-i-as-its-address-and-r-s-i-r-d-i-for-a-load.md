+++
id = "E483"
claim = "stad.repeatN and ldad.repeatN step the pointer register along with the data register: iteration i uses r(b + i) as its address and r(s + i) (r(d + i) for a load) as its data, the address read for every iteration i for N up to 16, and the pointer registers r40 to r43 move by the increment of the form (k after its own access for [rb,#k++], before it for [rb,++#k], not at all for [rb,+#k]), in 26 of 26 stad cases of the follow-up with 16 valid pointers (five plain, five post-increment, three pre-increment, twelve after an smlsi and one 16-dword copy) and in 7 of 7 ldad.repeat cases, in a client pixel task; the pointer movement was read for r40 to r43 only (the probe stores its marker through those four pointers, whatever N, so min(N, 4) markers: 2, 3 and 4 at N = 2, 3 and 4 and 4 above), so that whether r44 to r55 move, and whether the pointers a repeat does not use stay, was not read; after smlsi #a, #b, #c, #d the second increment sets the step of the pointer register and the fourth the step of the data register, the first and third doing nothing to a store (12 of 12; they were varied only together, in (1, 0, 1, 1) and (1, 1, 1, 1)), so that smlsi #0, #0, #0, #1 and stad.repeat16 [r40,#1++], r2 store r2 to r17 at the 16 consecutive dwords from r40 and move r40 by 16 (2 of 2: the smlsi probe's case 2 and the 16-dword copy after an ldad.fetch16); with only r40 a valid pointer, 27 of the 43 cases of the first run faulted the job"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1122 (sha256 ec423efc3d9aa34576553da70916be4ceb715a729cbc02cc4bd89fa052511244): probes/usse/store-repeat.toml (7 probes, 43 cases, the first run: only r40 and r41 hold pointers, one run by the campaign, the dataset, and one by probe.py outside the data: the same 27 of the 43 cases fault in both and the 16 that completed store the same dwords, while in 11 of the 27 faulted jobs the stores that landed before the fault differ between the two runs), the follow-up probes/usse/store-repeat-regs.toml (6 probes, 33 cases: r40-r55 hold 16 pointers 0x100 bytes apart, r56-r71 16 load pointers; the campaign and a second whole-table probe.py run, identical in 33 of 33) and probes/usse/store-repeat-regs2.toml (one probe, 7 cases, two runs identical, the ldad.repeat cases of the follow-up redone under a new name, because the marker stores of its probe stored a marker at the end of every one of four pointers whatever N: a table error, the failed run is kept in the dataset usse-store-repeat-regs as usse-store-repeat-regs-ldad-repeat, NONE of the hypotheses fits; its loads agree with the hypothesis in every case)"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-store-repeat", "usse-store-repeat-regs", "usse-store-repeat-regs2"]
terms = []
+++

**What runs.** `stad.repeatN [r40,+#0]`, `[r40,#K++]`, `[r40,++#K], r2` for N 2 to 16 and K 1 and
2, with r2-r33 the sources 0xA5000002 + n; `smlsi #a, #b, #c, #d, incrementmode x 4, #0, #0, #0`
immediately before a `stad.repeat4 [r40,#1++], r2` (11 sets in the first table, 12 in the
follow-up); `ldad.fetch16` then `stad.repeat16`; `ldad.repeatN r10, [r41 or r56, ...], drc0`. A
marker 0xB1B1B1B1 is stored 32 dwords past the final value of each pointer under test, so that
every pointer's end is read from where its marker lands. The first table set only r40 (the store
pointer) and r41 (the load pointer) and left r42 as the marker: so iteration 2 stored to r42's
value, 0xB1B1B1B1, and r43 and up held nothing set.

**First table (kept, run twice).** 27 of 43 cases faulted the job (I/O error, recovered):
stad.repeat2 completed in its four forms ([r40,+#0], [r40,#1++], [r40,#2++], [r40,++#1]) and
repeat3 in the plain one, stad.repeat4, 8 and 16 in the plain, post-increment and pre-increment
forms faulted (9 of 9), as did ldad.repeat2, 4, 8 and 16 (7 of 7), two of the four copy cases and 9
of the 11 smlsi cases (all of stad.repeat4 [r40,#1++]; the two that completed are named below).
What the faulted jobs did store showed the rule: stad.repeat2 [r40,+#0], r2 stored r2 at r40 and r3
at r41's address (dword 1024), not at dword 65; [r40,#1++] moved r40 by one dword and r42, a
pointer holding 0xB1B1B1B1, by 4 bytes (0xB1B1B1B5 read from the marker store). The two smlsi cases
that completed (smlsi #0, #0,
#0, #1 and #1, #0, #1, #1) stored r2 to r5 at the four consecutive dwords b to b + 3.

**Follow-up (r40-r55 valid pointers).** The hypothesis written after the first run (each iteration
uses the next pointer register and the next data register; each pointer moves by its own increment)
fits all 26 stad cases: plain N = 2, 3, 4, 8, 16 (5 of 5; iteration i stores r(2 + i) at the dword
r(40 + i) holds, read for every i), post-increment (N, K) = (2, 1), (4, 1), (16, 1), (4, 2), (8, 2)
(5 of 5; the data addresses are read for every i; the final value of a pointer was read only for r40
to r43: of those the used ones end K dwords on; at N = 2 only r40 and r41 have a marker, so that the
unused r42 and r43 were not read), pre-increment (2, 1), (4, 1), (4, 2) (3 of 3), smlsi (12 of 12:
increments (0,0,0,1), (1,0,1,1), (0,0,0,2), (0,0,0,0), (0,2,0,1), (0,1,0,1), (1,1,1,1), (0,1,0,0),
with K 1 or 2, plain, post- and pre-increment forms, N = 4 and 16; the data register steps by the
fourth increment, including 0, which stores the same register every iteration, and 2, which stores
every second one; the pointer by the second: 0 gives consecutive dwords from one post-incremented
pointer, 2 every second pointer), and the 16-dword copy (1 of 1). ldad.repeat: the follow-up table's
verdict is "none of the hypotheses fits" because of its marker stores (the loads agree: 7 of 7:
iteration i loads the dword r(56 + i) addresses into r(10 + i)); redone as store-repeat-regs2: 7 of
7 fit for the loads, with markers through 2 or 4 pointers only, so the pointer movement of
ldad.repeat was read for those.

**What it shows.** [HW] A repeat in the form of these probes is not a series of accesses from one
pointer: it indexes the pointer register by iteration, as it indexes the data register, and moves
the pointer registers r40 to r43 by the form's increment (the others were not read). [HW] smlsi,
with its second increment 0, gives the
one-pointer series: stad.repeatN [r40,#1++] then stores N registers to N consecutive dwords and
moves r40 by N, so the 16-dword copy is two instructions (smlsi, stad.repeat16 [rB,#1++], r2) and
needs no one-dword shift, against the one instruction of stad.fetch16 with the shift (E482).
[infer] The first run faulted because r43 and up did not hold addresses (r42's store went to
0xB1B1B1B1 without a fault).

**What it does not show.** That the first or the third smlsi increment alone does nothing to a store
(they changed together only); the effect of smlsi on instructions other than the next repeat (the
marker stores after the repeat behaved as plain stores); the meaning of increments 1 and 3 for other
operands (they did nothing visible to a store); repeat counts of 5 to 7, 9 to 15 and above 16 (N =
2, 3, 4, 8 and 16 plain, 2, 4, 8 and 16 post- increment, 2 and 4 pre-increment were run); the final
value of the pointers r44 to r55 (N = 8, 16), and of the pointers a repeat does not use; the pointer
movement of ldad.repeat beyond the 2 or 4 pointers whose markers were stored; `.repeatN` of a load
with a pre-increment form. All of this was measured in client pixel tasks (fills), not in firmware
tasks.
