+++
id = "E185"
claim = "With the triangle's VDM state word 1 bits 11:9 at 0 the TA writes no object and every region header is empty, byte for byte the render memory of the culled triangle; at 1, 6 and 7 the render memory is byte for byte the drawn triangle's, in both runs"
unit = "vdm"
method = "the probe jobs of probes/vdm/state1.toml that set the whole VDM state word 1 (pix_op.s pixel program, 64x64 triangle) with the render memory dumped after the job, compared byte for byte with each other and with the dump of the culled triangle from probes/ta/zero-words.toml, on the laptop, linux fork with the debug option on; two runs (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["vdm-state1", "vdm-state1-followup", "ta-zero-words"]
terms = ["VDM_STATE1.BITS11_9", "VDM_STATE1.BIT8"]
+++

**What runs.** The probe jobs replace the triangle's pixel program by a copy of o0 and set word 1 of
the VDM stream whole: the host's word 0x0a022405 (bits 11:9 = 2, the control, probe `vdm1-default`),
bits 11:9 = 0 (`vdm-state-0`), 1, 6 and 7, bit 8 set, bit 25 clear, and the word with bits 15:13 =
7, bits 11:9 = 0 and bit 8 set (0x0a02e105, probe `vdm-state-closed`), and the word with bit 12 set
(`vdm1-b12-set`). After each job the kernel's copies of the parameter buffer (4603904 bytes) and of
the TA data (24576 bytes) are saved. They are compared byte for byte.

**Results.** The dumps fall into groups, the same in both runs:

- *Drawn.* `vdm1-default`, bits 11:9 = 1, 6 and 7, bit 8 set and bit 25 clear: one group. The
  parameter buffer holds an object at its first page and a control-stream page at 0x1000, with
  seven streams (each 128 bytes) in the TA data's region list of 64 headers; three further pages
  (at 0x422000, 0x423000 and 0x463000) are common to all dumps.
- *Nothing tiled.* Bits 11:9 = 0, the word with 15:13 = 7, 11:9 = 0 and bit 8 set, bit 12 set
  alone, and bit 25 clear with bit 12 set: one group. The parameter buffer has only the three
  common pages (no object, no stream page) and all 64 region headers carry no stream pointer.
  This group is byte-identical, both files, with the dump of the culled triangle (MTE cull mode
  1) of the ta/zero-words table.

In the nothing-tiled group the probe reads o0 = 0xff203040 in all 4096 pixels (no triangle);
the drawn group shows a triangle (E060). None of these jobs fails. Bit 12 set (with bits 11:9 at
2) is in the nothing-tiled group: with that bit set the TA writes no object either.

**Not shown.** Why bit 12 acts as it does: it was set in two probes only and not swept. The probe
jobs set the whole word, so a bits 11:9 value is tested together with the rest of the word as
given. The value 7 of bits 11:9 hangs in the sweep and renders in the probe (E060, Q015); here it
renders.
