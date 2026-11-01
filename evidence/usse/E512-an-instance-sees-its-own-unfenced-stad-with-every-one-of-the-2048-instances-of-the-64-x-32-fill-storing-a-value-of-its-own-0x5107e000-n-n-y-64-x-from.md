+++
id = "E512"
claim = "An instance sees its own unfenced stad: with every one of the 2048 instances of the 64 x 32 fill storing a value of its own (0x5107E000 + n, n = y * 64 + x from pa0) to a dword of its own and loading it back, the load returns that instance's own value in 2048 of 2048 pixels in each of nine cases (ldad, ldad.bypassl1, ldad.fcfill, ldad on drc1 and ldad after a wdf drc0 with no idf, two stad of V1 then V2 where the load returns V2, with an idf drc0, bif and its wait between, and with the idf at the end), and a load of another region that was never stored returns the fill value in 2048 of 2048 in the tenth, and 2048 dwords of the region changed in all ten cases (32 values read, 2016 counted), among them the seven with no idf at all and no fence at the end"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e): probes/usse/store-own2.toml probe usse-store-own2-load (10 cases, campaign runner, one run) and the first run of the same programs, usse-store-own-load of the dataset usse-store-own (identical pixels in 10 of 10 cases; its verdict is NONE only because the table expected the 2048 changed scratch dwords one by one while the tool prints 32 changed dwords and then a count: a table error, kept, redone under the new name with the 32 shown dwords as the expectation and the count read from the \"more changed\" line); per-instance address r40 = scratch + 0x8000 + 4 n from pa0 (--coords), every pixel read (--pixels), the dwords of the region read back from the scratch (the tool shows the first 32 changed dwords and the number that changed after them: 2016 more in each of the ten cases, so 2048 changed dwords), the predictions (the three hypotheses of the table: sees its own store and every store reaches the host, sees it but an unfenced store is lost, does not see it before an idf) written before the run"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-store-own2", "usse-store-own"]
terms = []
+++

**What runs.** Every instance computes n from pa0, stores V1(n) with `stad [r40,+#0], r5` to the
dword 0x2000 + n of the scratch and loads it with `ldad r10, [r40,+#0], drc0; wdf drc0` (variants:
`ldad.bypassl1`, `ldad.fcfill`, drc1, a `wdf drc0` only between, an `idf drc0, bif; wdf drc0`
between, `stad` of V1 then V2, an `idf` and its wait or the `idf` alone at the end of the program,
no fence at all at the end), and o0 = r10, every pixel read. Control: the load addresses region B
(dwords 0x2800 + n), which no instance stored.

**Results.** The pixel of every instance holds its own V1 (V2 in the two-store case) in the nine
cases that load the stored dword (18432 of 18432 pixel reads) and the fill value 0xD0002800 + n in
the control (2048 of 2048). The scratch shows 2048 changed dwords in each of the ten cases, the
first 32 holding V1(n) (V2(n)), with the end of the program having no idf and no fence at all in
seven of them (ldad, bypassl1, fcfill, drc1, two stores, the control, and the case with a `wdf`
only between: cases 0, 2, 3, 4, 5, 6 and 9 of the table) and an `idf` in the other three: at the end
with a wait (case 7) or alone (case 8), and between the store and the load with no fence at the end
(case 1).

**What it shows.** [HW] A load of a dword that the same instance stored returns the stored value
without an idf, also through ldad.bypassl1 and ldad.fcfill, on drc1, after a second stad of the
dword (the later value), and with only a wdf between: in a client pixel task an instance sees its
own unfenced stad (the case E481 could not isolate, since all instances stored the same value). [HW]
A store with no fence before the end of the job changes the dword the host reads: 2048 dwords
changed (the first 32 read, the other 2016 counted) in the seven cases with no idf and no fence at
all. The documented model's
assumption for one instance holds here. [infer] The same would hold for `str` then `ldr`; not
measured (Q134).

**What it does not show.** That the host sees an unfenced store at any time before the job ends (it
reads after the job); a texture fetch of a stored dword; `str` and `ldr`; the values of the 2016
stores after the first 32 (they are counted, not read; the load pixels of all 2048 instances are).
All of this was measured in client pixel tasks (fills), not in firmware tasks.

**Correction, 2026-11-09 (11.35).** The measurements above are unchanged. The table's `load` verdict
(SETTLED) came from an exact expectation of the 32 scratch dwords the tool shows: it could not fail
on the other 2016 changed dwords, which are counted by the tool and not shown, so that "2048 dwords
changed" rests on the tool's count and on the first 32 values, not on the values of the 2016. The
pixels (all 2048 of every case, `pixels = true`) are checked in full; the claim that an instance
sees its own stad rests on them. Tables can now state the count (`scratch_more`).
