+++
id = "E478"
claim = "One wdf drc0 waits for every load outstanding on drc0, ldad, ldad.fetchN and ldr alike, and no limit on how many are outstanding was seen: 1, 2, 4, 8 and 16 independent ldad (5 of 5 cases), five mixes of ldad, ldad.fetchN of 2, 4, 8 and 16 dwords and ldr #7 and #8 (5 of 5), and, in the growth table, 24, 32, 48, 64, 80 and 100 distinct ldad on drc0 (6 cases), 32, 64 and 100 on drc1 (3), 128, 160 and 200 ldad that issue the same eight loads again over eight registers, which cannot show a lost reload (3) and 2, 4, 8, 12 and 16 ldad.fetch16, up to 256 dwords (5) (17 of 17 cases) all return their data after the one wdf, so what the data show is up to 100 distinct ldad on one counter (drc0 and drc1) and 16 ldad.fetch16, while a single ldad read by a stad after 0, 1, 2, 4, 8, 16 or 32 nops and four ldad after 0 or 16 nops still hold the register's marker (9 of 9 cases), in a client pixel task: the register still holds its marker 32 instruction slots after a single ldad (16 after four) with no wdf, and the wdf gives the data"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1122 (sha256 ec423efc3d9aa34576553da70916be4ceb715a729cbc02cc4bd89fa052511244): probes/usse/fence-batching.toml (probes one-wdf, mixed, no-wait; fill probes, 64 x 32 target, the scratch buffer's dwords 0xD0000000 | i and registers preset to markers 0xAA55000n before each load) and probes/usse/fence-growth.toml (ldad-drc0, ldad-drc1, ldad-reuse, fetch16; one probe at a time, risky table, none failed); runs: fence-batching.toml ran twice (the campaign, which is the dataset, and a whole-table probe.py run outside the data, not kept: the 19 cases of the probes one-wdf, mixed and no-wait read back the same in both) and fence-growth.toml twice (each probe alone by probe.py, as the table is risky, then the campaign: the same readbacks in 17 of 17 cases); the dataset holds one run of each case; the destination registers are stored to scratch dwords after the wdf and read back by the host"
tiers = ["HW"]
date = "2026-11-08"
data = ["usse-fence-batching", "usse-fence-growth"]
terms = []
+++

**What runs.** `ldad rN, [rB,+#o], drc0` into registers preset to a marker (0xAA55000n), N distinct
16-dword lines so that no two loads share a line, then one `wdf drc0`, then `stad` of each
destination (or of a sample, every 2nd to 6th and the last, for N of 24 and up, so that no more
than 31 dwords are stored: the probe tool shows 32 changed dwords). The no-wait control reads the
register after 0 to 32 `nop`s with no wdf. The fetch probe loads `ldad.fetch16` 2, 4, 8, 12 and 16
times into r4-r19 under one wdf (32 to 256 dwords). The `ldr` loads read id #7 and #8 (0x01150000
and 0x0001000d).

**Results.** One wdf: 1, 2, 4, 8 and 16 ldad, every destination holds its dword (5 of 5). Mixed
under one wdf: `ldad, ldad.fetch4, ldr #7, ldad`; `ldr #7, ldr #8, ldad`; `ldad.fetch16, ldad, ldr
#7`; three `ldad.fetch2`; `ldad.fetch8, fetch4, fetch2, ldad` (5 of 5, every register of every
fetch holds its dword, so a fetch is waited whole). Growth: 24, 32, 48, 64, 80 and 100 ldad on
drc0, 32, 64 and 100 on drc1, 128, 160 and 200 on drc0 onto eight registers, and 2 to 16 fetch16 (8
fetch and reuse cases and 9 sample cases, 17 of 17: the last register stored, the one most likely
to be late, holds its data in every case; the growth table stores only a sample, every 2nd to 6th
register and the last for the distinct ldad, the final 16 or 8 registers for the reloading cases,
so the other registers of those cases were not read). No-wait: a single ldad read after 0, 1, 2, 4,
8, 16 and 32 nops, and four ldad after 0 and 16 nops, keep the marker in all 9 of 9.

**What it shows.** [HW] A wdf drcN covers every load counted on drcN whatever the form (ldad,
ldad.fetchN, ldr), the whole fetch included, and the hardware showed no limit on outstanding loads
up to 100 distinct ldad on one counter (drc0 and drc1) or 256 dwords in 16 fetches, in a client
pixel task. The three reload cases (128, 160 and 200 ldad) load the same line into each of eight
registers 16 to 25 times, so every register holds the same value after its first load as after its
last: a lost or late reload would leave the data unchanged, and they show only that each register
received its load by the wdf; they cannot show that no reload is lost. [HW] A single ldad is not
complete 32 instruction slots after its issue and four ldad are not after 16, in the sense that the
register, read by a `stad` after the `nop`s, still holds the marker, so a program that reads a
destination with a `stad` and no wdf reads the old value. The number of instruction words of a
program is bounded by the tool (256 words), so counts above 200 loads were not run.

**What it does not show.** Distinct ldad beyond 100 (not run: the reload cases to 200 repeat lines);
a load read by an ALU instruction instead of a `stad` (the interlock of that reader might differ),
more than 32 slots without a wdf, and a load overwritten by a later write to its register; that the
marker staying is a load in flight rather than a landing delayed with no wdf; a load's latency in
time (the runner records none per case); the limit, if any, of outstanding loads on drc2 and drc3
(only ldr was run there, E479); loads of different counters at once (E479). All of this was measured
in client pixel tasks (fills), not in firmware tasks.
