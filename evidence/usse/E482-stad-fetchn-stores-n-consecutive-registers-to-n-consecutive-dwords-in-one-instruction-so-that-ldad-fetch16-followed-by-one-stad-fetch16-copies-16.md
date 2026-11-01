+++
id = "E482"
claim = "stad.fetchN stores N consecutive registers to N consecutive dwords in one instruction, so that ldad.fetch16 followed by one stad.fetch16 copies 16 dwords with two instructions and one wdf: the stores land one dword on from the base, dwords b + k + 1 to b + k + N for [rb,+#k] (stad.fetch2, 4 and 16 with k 1 and fetch4 with k 0: 4 of 4) and dwords b + 1 to b + N for [rb,#1++], which moves rb by N (fetch2, 4 and 16: 3 of 3), the layout of a load fetch, and the 16-dword copy from r2-r17 of the dwords a load fetch read matches in order (1 of 1); a plain stad [rb,#1++] repeated sixteen times, the control, stores b to b + 15 and moves rb by 16 (1 of 1)"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1122 (sha256 ec423efc3d9aa34576553da70916be4ceb715a729cbc02cc4bd89fa052511244): probes/usse/store-repeat.toml probes fetch-spelling (7 cases) and copy16 (case 2 and the control case 3; the other two cases of copy16 faulted, E483); fill probes, r2-r33 preset to 0xA5000002 + n, a marker 0xB1B1B1B1 stored 32 dwords past the base's final value, so that the end of the base is read from where the marker lands; two runs (the campaign and a whole-table probe.py run) agree in these 9 cases"
tiers = ["HW"]
date = "2026-11-08"
data = ["usse-store-repeat"]
terms = []
+++

**What runs.** `stad.fetchN [r40,+#k], r2` and `[r40,#k++]`, N = 2, 4 and 16; `ldad.fetch16 r2,
[r41,+#0], drc0; wdf drc0` (the dwords 1025 to 1040 of the scratch, E093) then `stad.fetch16
[r40,+#0], r2`; and sixteen plain `stad [r40,#1++], rN` for N = 2 to 17 as the control. The scratch
dwords that changed are compared as a set.

**Results.** `stad.fetch2/4/16 [r40,+#1], r2` store 0xA5000002 onward from dword b + 2 (b = r40's
dword), `fetch4 [r40,+#0]` from b + 1; `stad.fetchN [r40,#1++]` store from b + 1 and the marker
shows r40 moved by N (2, 4 and 16); the copy stores 0xD0000401-0xD0000410 at b + 1 to b + 16 (16 of
16 in order) and leaves r40; the sixteen plain stad store 0xD0000401-0xD0000410 at b to b + 15 and
move r40 by 16.

**What it shows.** [HW] stad.fetchN is the store twin of the load fetch: the N registers from the
named one go to N consecutive dwords, with the same one-dword shift of the address as E093 shows
for loads ([rb,+#k] starts at b + k + 1). So a 16-dword copy is `ldad.fetch16 rA, [rS,+#0], drc0;
wdf drc0; stad.fetch16 [rD,+#0], rA` with rD one dword (4 bytes) below the destination, or the
destination plus the shift; the loaded dwords of a load fetch also start one dword on. [HW]
[rb,#1++] with a fetch moves rb by N once, not per dword. The `.repeatN` spelling does not do this
(E483).

**What it does not show.** The post-increment forms with k other than 1 for a fetch (k = 1 only),
the pre-increment form of a fetch, a fetch wider than 16, and the offsets `[rb,+#k]` other than k =
0 (fetch4) and k = 1 (fetch2, 4 and 16). All of this was measured in client pixel tasks (fills), not
in firmware tasks.
