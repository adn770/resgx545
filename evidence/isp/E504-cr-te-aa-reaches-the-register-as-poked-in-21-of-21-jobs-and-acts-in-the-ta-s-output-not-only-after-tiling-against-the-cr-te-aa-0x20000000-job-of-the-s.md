+++
id = "E504"
claim = "CR_TE_AA reaches the register as poked in 21 of 21 jobs and acts in the TA's output, not only after tiling: against the CR_TE_AA 0x20000000 job of the same size and mode, a value of 0 gives 0 differing dwords of the 1150976-dword parameter buffer and of the 6144-dword TA data (3 of 3 pairs), 0x60000000 and 0xa0000000 each differ in 76 and 132 dwords (mode 0 and mode 2, 64 x 64), 0xe0000000 in 204 and 279 (64 x 64, mode 2, twice) and 805 and 367 (128 x 128), and 0x40000000, 0x80000000 and 0xc0000000 remove the triangle (3969 of 4096 pixels differ, 6 of 6)"
unit = "isp"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e), probes/isp/msaa-te-dumps.toml (script msaa-te-dumps.sh): probe-less tri --tri-full --dump-render with mode 0 and mode 2 at 64 x 64 and mode 2 at 128 x 128, CR_TE_AA in {0x20000000, 0, 0x40000000, 0x60000000, 0x80000000, 0xa0000000, 0xc0000000, 0xe0000000}, sample words 0xeaa26e26, registers 0x0200 to 0x0218 read back; 21 jobs, 2 repeats; the dumps (render_param, render_tadata) compared dword by dword on the Mac by recompute_p1126b.py (recompute_p1126.py crashed on a faulted job of another dataset; the second skips tokens that do not parse); declared sets: 64 x 64 fit, 128 x 128 held out, two repeats"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["isp-msaa-te-dumps"]
terms = ["CR_TE_AA", "CR_ISP_MSAA", "CR_TE_MTILE1", "CR_TE_MTILE2"]
+++

**What ran.** 21 jobs: mode 0 and mode 2 at 64 x 64 with the eight CR_TE_AA values (16), mode 2 at
128 x 128 with 0x20000000, 0 and 0xe0000000 (3), and two repeats (mode 2, 64 x 64, 0x20000000 and
0xe0000000). All exited with the job done; the three values without bit 29 and bits 30 or 31 (0x40,
0x80, 0xc0 in modes 0 and 2) and mode 0 with 0xe0000000 ended with the tool's image check failing
(rc 1), and the tool writes no dump after a failed check, so those 7 jobs have no dumps. 14 jobs
have dumps.

**Registers.** [HW] `CR_TE_AA` (0x0204) read back the poked word in 21 of 21 jobs. `CR_TE_MTILE1`
and `CR_TE_MTILE2` read 0x01004004 and `CR_TE_MACROTILE_STRIDE` 0x10 in 21 of 21 (the 128 x 128 job
as well, whose context is sized by the library), `CR_TE_SCREEN` 0x3001 (18) and 0x7003 (3, the 128 x
128 jobs).

**Images (the tool's check).** Mode 0 and mode 2 at 64 x 64: 0x20000000, 0, 0x60000000 and
0xa0000000 draw exactly (diff 0 of 4096, 8 of 8); 0x40000000, 0x80000000 and 0xc0000000 leave 3969
of 4096 pixels differing (6 of 6, the same hash 0xfc5ff15e0434a325: the triangle is gone, as E281
found); 0xe0000000 draws exactly in mode 2 and leaves 136 pixels in mode 0, the first at (32, 32).
Mode 2 at 128 x 128 draws exactly for all three values.

**Dumps.** The parameter buffer and TA data are those of CR_TE_AA 0x20000000 for a value of 0 (0 of
1150976 and 0 of 6144 dwords differ, in mode 0, mode 2 and the 128 x 128 job). With bit 30 or bit
31 set (with bit 29), 76 parameter and 132 TA data dwords differ, identically many for 0x60000000
and 0xa0000000 and for modes 0 and 2, though not the same values (at dword 1120 of the parameter
buffer 0x4690ffff becomes 0x4688000f for 0x60000000 and 0x46880007 for 0xa0000000; at 1056
0x4688000f becomes 0x46880007 for both); 0xe0000000 gives 204 and 279 (64 x 64, mode 2, the same in
the repeat) and 805 and 367 (128 x 128). TA data dwords such as 4108 go from 0x00000002 to
0x00000001 and 4099 from 0x00020000 to 0x00010000 [HW]; they look like halved counts and
coordinates [infer].

**What it shows.** [HW] CR_TE_AA bits 30 and 31 change what the TA writes (the parameter buffer and
the TA data), and the changed dwords are the same in value and position in mode 0 and mode 2 (the
76 and 132 of 0x60000000 and 0xa0000000, 64 x 64); bit 29 and a clear word change no dword.
[infer] So the window of E503 (a rule read post hoc) is chosen in the tiling, in contrast to
`CR_ISP_MSAA` bit 31 which acts after it (E281); this is an inference, since E503 has bit 30 acting
in mode 2 only while the changed dwords are the same in mode 0 and mode 2, so the TA's output does
not by itself explain the stored window, and no mode 1 dump was taken. [infer] Bit 29 enables the
window selection and bits 31 and 30 name the window; which dwords hold which field is not decoded
(Q142).

**What it does not show.** The meaning of each differing dword; mode 1 dumps; sizes other than 64 x
64 and 128 x 128.
