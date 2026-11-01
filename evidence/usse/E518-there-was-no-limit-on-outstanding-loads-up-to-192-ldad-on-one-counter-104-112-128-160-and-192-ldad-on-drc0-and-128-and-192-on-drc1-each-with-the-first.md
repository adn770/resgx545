+++
id = "E518"
claim = "No limit on outstanding loads was seen up to 192 ldad on one counter: 104, 112, 128, 160 and 192 `ldad` on drc0, and 128 and 192 on drc1, each with the first 100 into r4 to r103 and the others reloading r4 onward with a different line, then one wdf, left every one of the 8 sampled registers holding the line of its last load in 7 of 7 jobs (the 4 or 5 reloaded registers read per job, 4 of 4 up to 5 of 92, the new line, the others the first line), no reload seen lost, and no job hung or faulted, in a client pixel task"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e): probes/usse/reload-growth.toml (7 probes of one case, campaign runner, each with the baseline triangle clean after it); ldad r(4 + k mod 100), [r104,#16++], drc0|1 for k = 0 to N - 1 (the lines 16 dwords apart, a pointer post-incremented), one wdf, then stad of eight sampled registers (the first reloaded, the last reloaded, the first not reloaded, r54, r103 and three more of the 8); the hypotheses (before the run): no limit; loads past the 100th lost (the reloaded registers keep their first line); the sampled registers are r4 to r9, r54 and r103 at 104; r4, r5, r10, r15 to r17, r54 and r103 at 112; r4, r5, r18, r31 to r33, r54 and r103 at 128; r4, r5, r34, r54, r63 to r65 and r103 at 160; r4, r5, r50, r54, r95 to r97 and r103 at 192 (the same lists on drc1); this redoes the \"up to 200 ldad\" claim of E478, whose reload cases repeated one line per register and so could not show a lost reload"
tiers = ["HW"]
date = "2026-11-08"
data = ["usse-reload-growth"]
terms = []
+++

**Results.** 7 of 7 probes SETTLED the no-limit hypothesis: each sampled register holds the line of
the last load that named it (r4 = line 100 = 0xD0000A40 at N = 104; the words are in the dataset);
no job faulted or hung. Of the sampled registers the reloaded ones are 4 of 4 (N = 104), 4 of 12
(112), 4 of 28 (128), 5 of 60 (160) and 5 of 92 (192): the other registers that were reloaded were
not read. The program is 192 loads long at most; 200 distinct loads in one program were not run,
and why the table stopped at 192 is not recorded (E478 ran 200 `ldad` that repeat lines, so the
tool's program length alone does not explain it).

**What it shows.** [HW] A wdf covers up to 192 outstanding ldad on one counter, 92 of them reloads
of registers whose first load is still outstanding, on drc0 (104, 112, 128, 160, 192) and drc1 (128,
192), for the 4 or 5 reloaded registers read in each job: a lost reload of one of those would have
kept the older line, and none did; a lost or reordered reload of a register not read would not show.
The later line won on each of those registers (one pair of loads per register: each register is
reloaded once). All of this was measured in client pixel tasks (fills), not in firmware
tasks.

**What it does not show.** The reloaded registers that were not read (at 192, 87 of the 92), more
than 192 loads in one program, mixed counters in one wait, ldr,
loads of the same dword from other instances.
