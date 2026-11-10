+++
id = "E480"
claim = "A wdf, or an idf drcN, bif, with nothing outstanding returns at once and does not hang the job: as the first instruction after phas on each of drc0, drc1, drc2 and drc3, twice in a row, on all four in a row, with an idf drc0 or drc1, bif, and as the second and third wdf after one load or a wdf on a counter nothing was issued on (11 of 11 cases, the pixel reads the sentinel), and in seven short programs the dword or dwords the host reads after the job hold the stored value whether or not a fence precedes the end of the program (7 of 7 cases; every one of the 2048 instances of the fill stores the same value to the same dword, so this shows the final value of that dword, not that any one instance's unfenced store reaches the host): one stad followed by no fence, by idf drc0, bif only, by wdf drc0 only, by the usual idf and wdf, or by one nop (5 cases), and sixteen stad followed by no fence or by idf drc0, bif only (2 cases)"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1122 (sha256 ec423efc3d9aa34576553da70916be4ceb715a729cbc02cc4bd89fa052511244): probes/usse/fence-batching.toml probes empty-wdf (11 cases) and end-of-program (7 cases), fill probes, the pixel o0 a sentinel (0xC0DE0001) written last, stores to scratch dwords read back by the host; two runs (the campaign and a whole-table probe.py run) agree in all 18"
tiers = ["HW"]
date = "2026-11-08"
data = ["usse-fence-batching"]
terms = []
+++

**What runs.** empty-wdf: `wdf drc0` (and drc1, drc2, drc3) as the first instruction after `phas`;
`wdf drc0` twice; `wdf drc0-3` in a row; `idf drc0, bif` and `idf drc1, bif`, with and without a
following `wdf`; one `ldad` then `wdf drc0` three times; `wdf drc1` after a load on drc0.
end-of-program: `stad` of 0x5107E001 to dword 0 (and to dwords 0-15), then the end of the program
with no fence, `idf drc0, bif` only, `wdf drc0` only, the usual `idf drc0, bif; wdf drc0`, or one
`nop`.

**Results.** All 11 empty-wdf cases end with the pixel at the sentinel and the job complete, the
one-ldad cases with the loaded dword in scratch dword 0. All 7 end-of-program cases leave the
stored value in scratch dword 0 (and in dwords 0-15 for the two sixteen-store cases: no fence, and
idf only), whatever fence, if any, precedes the end.

**What it shows.** [HW] A wdf with nothing outstanding is a no-op (the fence-batching question),
also as the first instruction of a program and on counters never used; `idf drc0, bif` with nothing
stored too. [HW] After a stad that is not fenced the host reads the stored value in the dword at the
end of the job (2 of 2 with no fence at all, one store and sixteen; 5 of 5 with a partial fence or a
nop). All 2048 instances of the fill store the same value to the same dword, so a single instance's
unfenced store lost at the end would be hidden by the other 2047: the cases show the dword's value,
not the fate of one instance's store.

**What it does not show.** Whether the same holds for an EDM (firmware) task, whose end the
microkernel handles itself (the overlap question, answered by E752); that one instance's unfenced store reaches the host (all 2048
instances store the same value to the same dword; a per-instance address, or one instance selected
by a test of pa0 as the emitpds probe does, was not run; Q134); visibility of an unfenced store to
another instance or to the host while the job still runs.

**Correction, 2026-11-08 (11.27).** The measurements above are unchanged (all 2048 instances stored
the same value to the same dword). E512 ran the same end-of-program cases with a dword of the
instance's own (0x5107E000 + n, n from `pa0`) and a value of its own: all 2048 dwords of the region
changed in the seven cases that ended with no `idf` and no fence (the first 32 read, the other 2016
counted), so an unfenced `stad` changes the dword the host reads in a client pixel task for each
instance of the fill (2048 changed dwords, 32 values read), and in E513 for the four lanes of a quad
(4 of 4 in each of the 5 jobs that stored). 'One instance' in the sentence above was a quad of four
lanes where the instance was selected by a test of `pa0` (E513). Not run: the host reading during
the job and an EDM task (Q143, and the overlap question answered by E752).
