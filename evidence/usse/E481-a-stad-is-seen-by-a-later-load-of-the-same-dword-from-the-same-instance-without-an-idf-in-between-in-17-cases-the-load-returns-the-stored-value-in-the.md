+++
id = "E481"
claim = "A stad is seen by a later load of the same dword without an idf in between, by instances that all store the same value to the same dword (a single instance's store is not isolated, since each of the 2048 instances of the fill stores to that dword and a load may return another instance's identical store): in 17 cases the load returns the stored value in the 16 that load the stored dword (ten with no idf, among them ldad, ldad.bypassl1, ldad.fcfill, eldd, ldad.bpcache and ldad on drc1, two stad of one dword where the later wins, and sixteen stad then a load of the last and of the first dword, each returning its own store; four with an idf and its wait; two with an idf not waited) and the buffer's fill in the control, a load of the next, untouched dword, so an idf is not needed for this order"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1122 (sha256 ec423efc3d9aa34576553da70916be4ceb715a729cbc02cc4bd89fa052511244): probes/usse/fence-batching.toml probes store-then-load (11 cases) and store-then-load-recorded (6 cases, no hypothesis); fill probes, stores of 0x5107E001 (V1) and 0x5107E002 (V2) to a dword at scratch dword 2048, the load into a register that is stored to dword 0; two runs agree in 17 of 17"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-fence-batching"]
terms = []
+++

**What runs.** `stad [r40,+#0], rV` then `ldad rD, [r40,+#0], drc0; wdf drc0` and `stad [r1,+#0],
rD`: with no idf; with `idf drc0, bif; wdf drc0` between; with `ldad.bypassl1`, `ldad.fcfill`,
`eldd`, and (recorded) `stad.bpcache` with `ldad.bpcache`; on drc1 with and without `idf drc1,
bif`; with an idf not waited, an idf on drc1 and drc2, a `wdf drc0` with no idf; two `stad` of V1
then V2; sixteen `stad` to dwords 2048-2063 (the last V2) then `ldad` of the last and of the first
dword; control: `ldad` of the dword next to the stored one.

**Results.** The loaded register holds the stored value in all 16 cases that load the stored dword
(V2 in the cases of two stores and the load of the last of sixteen, V1 for the first), and the fill
value 0xD0000801 in the control.

**What it shows.** [HW] Store then load of one dword, with all 2048 instances storing the same value
to it, returns the stored value without any fence (the model's assumption for `stad` and `ldad` is
for one instance; E098 showed the same for one case); a load that returns the stored value may have
seen another instance's identical store (the value V2 of the two-store case is also stored by every
instance), so it is not shown that an instance sees its own store unfenced, also through the
cache-control variants, on drc1, and after a second store. [infer] The same would be true of `str`
then `ldr`, which is not measured (Q134): no client `str` was seen to land (usse_isa 6.21, 7.11).
Nothing in these 17 cases needs an `idf`; when an `idf drc, bif` after a `stad` is required (another
instance, the host during the job, a texture fetch of the stored data) is not shown (Q134).

**What it does not show.** That one instance sees its own store (the same programs with a
per-instance address, from pa0 or the instance number in the pointer, or with one instance selected
by a test of pa0, were not run; Q134); another instance's load of the stored dword, a store followed
by a load of a different word of the same line, a store and load through different virtual addresses
of the same page, and `str` / `ldr`. All of this was measured in client pixel tasks (fills), not in
firmware tasks.
