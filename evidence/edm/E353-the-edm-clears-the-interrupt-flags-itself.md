+++
id = "E353"
claim = "The EDM itself clears InterruptFlags and InterruptClearFlags: its POWER handler clears bit 1 of both, and the routine at instructions 0x1c4-0x599, which tests InterruptClearFlags bit 0, clears bit 0 of both after zeroing its TA/3D control words and setting the kernel CCB's read offset to the write offset; the same routine sets InterruptFlags bit 0 after counting a lockup and bit 1 when the active-power countdown reaches zero, each followed by a SW_EVENT write; no other resolved EDM access writes either word"
unit = "edm"
method = "the EDM dataflow of E013 (harness/ukernel-extract/edm_dataflow.py on the microkernel cut from the user's firmware, dataset firmware-edm-dataflow-11): every read, write and test of HOST_CTL+0x20 and +0x24 and the writes near them, with the kick-address table of E012 naming the handlers; our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE"]
date = "2026-11-03"
data = ["firmware-edm-dataflow-11"]
terms = [
    "host_ctl.interrupt_flags", "host_ctl.interrupt_clear_flags",
    "host_ctl.ukernel_detected_lockups", "host_ctl.active_powman_sample_rate",
    "host_ctl.init_status", "CMD.POWER", "CR_EVENT_STATUS.SW_EVENT",
]
+++

**What the dataflow lists.** Every access to the two words, by instruction index (byte offset /
8):

- In the `POWER` handler (`0xd4`-`0xea`, E012): both words are read, and each is written back
  `& ~2` (`0xdd`, `0xdf`).
- In the routine `0x1c4`-`0x599`: `InterruptClearFlags` is read and its bit 0 tested (`0x1d1`),
  next to the write of `InitStatus` = 1 (`0x1d3`). Further on, after the TA/3D control words
  `+0x50`, `+0x54`, `+0x60`-`+0x74`, `+0x7c`, `+0xb8`, `+0xbc` and `+0xd0` are written 0 and the
  kernel CCB's read offset is set to its write offset (`0x2a7`-`0x2b9`), both words are written
  back `& ~1` (`0x2bd`, `0x2c1`).
- In the same routine: `ukernel_detected_lockups` is incremented and `InterruptFlags |= 1`
  (`0x391`, `0x394`), then `EVENT_STATUS` is written `0x4000`, `SW_EVENT` (`0x398`). And a
  countdown in `sa11`, loaded from `active_powman_sample_rate`, is skipped while 0, else
  decremented; at zero `InterruptFlags |= 2` (`0x4d1`) and `EVENT_STATUS` = `0x4000` (`0x4d5`).

No other instruction the dataflow resolves writes either word (379 memory accesses stay
unresolved, E013).

**What it shows.** The host never writes `InterruptFlags` and writes `InterruptClearFlags` only
to acknowledge a request (E005: the DDK's recovery and active-power paths); the firmware clears
both: the recovery bit (0) on the path that also drops the kernel CCB's pending commands, the
active-power bit (1) on a `POWER` command [RE]. With `active_powman_sample_rate` = 0 (E005) the
countdown never runs, so bit 1 is never set [infer]. The dataflow does not resolve which branch
of the `0x1d1` test leads to the clearing, and no run has caused a lockup the EDM detects, so the
clearing has not been seen on the hardware.
