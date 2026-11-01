+++
id = "E224"
claim = "0x0520 is read as four sample positions by ISP word 0 bit 28 and is not the base of a table the ISP reads or writes: pointed at the scratch buffer it changes no scratch dword, no ISP word 0 or word 1 bit tried changes a pixel with it except bit 28 (more pixels) and bit 18 (a fault that 0x0520 at 0 gives too), and the 55 values of the bit-28 sweep are fitted by sample positions"
unit = "isp"
method = "comparison of E214's probes with the open descriptions of other GPUs' ISP table base registers (no citation record of this tree covers them, so the reading is ours), hardware runs on the laptop, linux fork with the debug option on: the 30 probes isp-sample-positions-0520-* and the 55 isp-sample-positions-isp0b28-0520-*; one run"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["isp-sample-positions"]
terms = ["CR_ISP_SAMPLE_POS", "hw_render_details.isp_sample_pos", "CR_ISP_MULTISAMPLECTL", "programmable sample positions", "ISP0"]
+++

**The reading.** A 32-bit register that is 0 in the job and has all its bits implemented (E067),
placed among the ISP's state words, could be a base address of a table that objects index, as the
neighbouring registers of other GPUs' ISPs are (the reading is ours). A test would point it at a
scratch buffer and set every ISP word bit that no row names, to see whether anything reads or writes
the buffer.

**What runs.** 0x0520 (rd:19) at the scratch buffer's address 0x3e006000, with ISP word 0 bits 10
to 14, 18, 19 and 28 to 31 set in turn (word 0 = 0x01d00200 plus the bit) and ISP word 1 bits 16
to 22 and 24 to 31 (word 1 = 0x10f0 plus the bit), and the base job and an ISP word 1 bit 3
(visibility test) job.

**Results.** The base, the 15 ISP word 1 probes, the visibility probe and the ISP word 0 probes for
bits 10 to 14, 19 and 29 to 31 give the baseline 1062 triangle pixels. ISP word 0 bit 28 gives 1122
pixels with 0x0520 at the scratch address and 1098 with it left at 0. ISP word 0 bit 18 faulted the
job, with 0x0520 at the scratch address and with it left at 0. No probe printed a changed scratch
dword. The 55 probes of E214 set 0x0520 to values from 0 to ~0 with bit 28 set; their images are
fitted by sample positions, and the probe at the scratch address agrees with the sweep's probe
at the same number (the same pixels).

**What it shows.** Nothing in these runs reads or writes memory through 0x0520, and the one bit
that reacts to the register's value reacts like a sample position, so the table-base reading has no
support here.

**Not shown.** Only the ISP word bits tried were varied; a table the ISP reads only for objects
that use bits 15 to 17, 20 to 27 of word 0 or bits 0 to 2, 4 to 15, 23 of word 1 was not looked
for (those bits were not set in these probes). A read of the scratch buffer leaves no trace in the
data; the fault of bit 18 is a fault whatever the register holds, so it shows nothing about
0x0520. One run.
