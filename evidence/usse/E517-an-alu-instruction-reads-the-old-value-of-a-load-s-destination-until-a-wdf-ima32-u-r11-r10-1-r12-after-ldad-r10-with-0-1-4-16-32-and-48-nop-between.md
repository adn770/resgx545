+++
id = "E517"
claim = "An ALU instruction reads the old value of a load's destination until a wdf: `ima32.u r11, r10, #1, r12` after `ldad r10` with 0, 1, 4, 16, 32 and 48 `nop` between read the marker (6 of 6 cases, r11 = marker + 7 and r10 still the marker when stored), so the ALU reader has no interlock either; a load not waited for had landed when a stad read r10 after 40, 100 and 128 `nop` and not after 48 and 64 (3 of 5 cases landed), so it can land with no wdf, not as a function of the slot count; and a `mov r10, #X` after an `ldad r10` and before its `wdf` is overwritten by the load in 4 of 4 cases (0, 4, 16 and 32 `nop` between), while a mov after the wdf wins (1 of 1)"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e): probes/usse/load-readers.toml probes alu (6 cases, SETTLED: old value), slots (5 cases, NONE: the table's two hypotheses were \"never lands\" and \"landed\", the data show both) and waw (5 cases, SETTLED: the load lands over the later write), one campaign run, one sample per case; the destination r10 preset to 0xAA55000A, the loaded dword 0xD0000400, the readers store to scratch dwords 0 and 1"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-load-readers"]
terms = []
+++

**Results.** alu: r11 = 0xAA550011 and r10 = 0xAA55000A in each of the six cases; slots: r10 =
0xD0000400 after 40, 100 and 128 `nop` and 0xAA55000A after 48 and 64; waw: 0xD0000400 after 0, 4,
16 and 32 `nop`, and 0x77AA0001 when the `wdf` comes before the `mov`.

**What it shows.** [HW] The ALU reader of an unwaited load sees the old value from the next
instruction to 48 `nop` on (6 of 6), as the stad did (E478): a `wdf` is needed before any use. [HW]
A load not waited for is not reliably pending after 32 slots: it had landed at 40, 100 and 128 and
not at 48 and 64, [infer] a timing effect of one sample per value, so no slot count replaces the
`wdf`. [HW] A load is not cancelled by a later write to its register: the load lands over a `mov`
issued before the wdf (4 of 4). All of this was measured in client pixel tasks (fills), not in
firmware tasks.

**What it does not show.** The latency in time; slots by repeats of a single value; a write other
than `mov`; a reader in the dual-issue secondary or the texture unit; the order of two loads to one
register (Q146).
