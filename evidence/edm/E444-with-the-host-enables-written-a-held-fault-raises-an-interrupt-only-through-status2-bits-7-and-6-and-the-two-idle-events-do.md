+++
id = "E444"
claim = "With a bus-interface fault held and the host event enables written through debugfs kregnow, the host interrupts that come with no SW_EVENT are those of CR_EVENT_STATUS bit 29 and CR_EVENT_STATUS2 bit 10, which an idle GPU has set too, of bit 7 after a TA fault (status2 0x480), and of bit 6 after a background program's fetch fault (0x440); the EDM's write to a read-only page leaves status2 at the idle 0x400 and sets no further bit; the fault itself raises no host interrupt while only the EDM's event is enabled (14 held faults: five of the TA read and of the PDS fetch, four of the EDM write; and an idle control)"
unit = "edm"
method = "probes/edm/host-events.toml (host-events.sh) on the laptop (direct cable), linux fork ef6ba7cd1b9f with the debug option on: debugfs hold_recovery set, then one of three faults held (tri --fault, the TA's read of an unmapped stream page; alias_ta3d_ro, the EDM's write to the read-only TA/3D control block; tri --pixels --poke cmd:23^=0x08000000, a background program fetched from the pixel PDS heap), the event registers read 2.5 s later, then debugfs kregnow written: none; every bit of CR_EVENT_HOST_ENABLE and CR_EVENT_HOST_ENABLE2; each bit that reads set in status, alone with the EDM's bit 14 (one fault each); the counts of host interrupts and the status of the last read from kregnow; debugfs reset after each case"
tiers = ["HW", "infer"]
date = "2026-11-07"
data = ["edm-host-events"]
terms = ["CR_EVENT_HOST_ENABLE", "CR_EVENT_HOST_ENABLE2", "CR_EVENT_STATUS", "CR_EVENT_STATUS2", "CR_EVENT_STATUS.TIMER", "CR_EVENT_STATUS.MASTER_INTERRUPT", "CR_EVENT_STATUS2.TRIG_TA", "CR_EVENT_STATUS2.TRIG_3D", "CR_EVENT_STATUS2.DCU_INVAL_COMPLETE", "CR_BIF_INT_STAT", "CR_BIF_FAULT"]
+++

**What runs.** The kernel's only host interrupt handler acknowledges the EDM's SW_EVENT (bit 14 of
`CR_EVENT_STATUS`) and nothing else, and the firmware enables nothing but that event in
`CR_EVENT_HOST_ENABLE` (0x4000; `CR_EVENT_HOST_ENABLE2` is 0). debugfs kregnow (linux fork commit
36) writes either enable at any time, also while a fault is held, and counts every host interrupt;
an interrupt with no SW_EVENT while the enables were written is counted as extra, its status kept,
and the enables are put back at once (the event is not acknowledged, so it would raise the
interrupt again). Each case is a fresh debugfs reset, hold_recovery, one fault held for 2.5 s,
the registers read, kregnow written, one second, the registers and counts read.

**Results.** Before any enable the registers read as follows in the held faults, in every run of
the kind:

| fault | `CR_EVENT_STATUS` | `CR_EVENT_STATUS2` | `CR_BIF_INT_STAT` | `CR_BIF_FAULT` |
|---|---|---|---|---|
| TA read of an unmapped stream page | 0x20000000 | 0x480 | 0x90008 | 0x3e000001 |
| EDM write to a read-only page | 0x20000000 | 0x400 | 0x80400 | 0x32004001 |
| background program fetch, pixel PDS heap | 0x20000000 | 0x440 | 0xd0400 | 0x0001f061 |

With nothing written the extra count stayed 0 in all three kinds (the status bits are set; no
interrupt came). With every bit of both enables written, two extra interrupts came in each kind
(host interrupts 2, 2 and 3: the PDS kind had one more before, from the job itself), the last with
status 0xa0000000 (bits 31 and 29) and status2 as above. Alone, in each kind:

| enable written | TA read fault | EDM write fault | PDS fetch fault |
|---|---|---|---|
| `CR_EVENT_HOST_ENABLE` bit 29 | 1 extra | 1 extra | 1 extra |
| `CR_EVENT_HOST_ENABLE2` bit 10 | 1 extra | 1 extra | 1 extra |
| `CR_EVENT_HOST_ENABLE2` bit 7 | 1 extra | not run | not run |
| `CR_EVENT_HOST_ENABLE2` bit 6 | not run | not run | 1 extra |

An idle GPU, with every bit of both enables written, also raised two extra interrupts, with status
0xa0000000 and status2 0x400: bit 29 and status2 bit 10 are set with no job, and a fill after the
control ran (diff 0). The kernel's log has one line per extra interrupt with that status.

"Not run" cells are cases that were not tried: an enable bit was written alone only where the
fault's before-line showed the matching status bit set (bit 7 only after the TA read fault, bit 6
only after the PDS fetch fault).

**What it shows.**

- The status registers of the EDM's write fault read as the idle ones, and the TA's read fault and
  the PDS fetch fault are followed by one `CR_EVENT_STATUS2` bit each, bit 7 (`TRIG_TA`) and
  bit 6 (`TRIG_3D`), as E357 saw [HW]. Those two bits do raise the host interrupt once their
  enable bit is written, alone, so each is a host event, not only a latched flag [HW]. Bit 7 is
  the TA trigger's and not the fault's alone (E357 saw it for a hang with no fault). The kernel
  does not enable them, which is why E021 and E317 saw no interrupt [infer].
- Bit 29 of `CR_EVENT_STATUS` (`TIMER`) and bit 10 of `CR_EVENT_STATUS2` (`DCU_INVAL_COMPLETE`)
  are set with no job and are host events too; they say nothing about a fault [HW].
- Bit 31 of `CR_EVENT_STATUS` (`MASTER_INTERRUPT`) reads set with an enabled event pending and is
  clear without one (0x20000000 before, 0xa0000000 after an enable) [HW], as its name says.

**What it does not show.** Which unit raises bits 7 and 6 (E357 saw bit 7 set for a hang with no
fault too, so it is the TA's trigger, not the fault's), whether other fault kinds (a fault of the
3D's own fetch, of the texture unit's, a transfer's) set other bits, and what bits 16 to 18 of
`CR_BIF_INT_STAT` name: no event bit moves with them here. Each case ran once per fault kind; the
enables were written once a fault had been held 2.5 s, so an interrupt raised only at the moment
of the fault is not covered.

**Provenance.** The campaign read the srcversion of the installed module file (modinfo), not of
the loaded module. This run was on an earlier boot than the other four 11.17 runs (uptime 34312 s
against 183 to 511 s): its output prints the installed file's srcversion F156823E6F1F976458D94BF
(the kit's env.toml had been patched afterwards to E431D4FEB0F36E3C337AD50, the other four runs'
file; the data now says F156823E...). The loaded module was an intermediate build of the fork
(commit 36 or later) with kregnow, which the kernel log shows in use and which the installed
file's older build need not have had; its srcversion was not recorded. This record uses only
kregnow of the new controls. The other four runs print E431D4FEB0F36E3C337AD50 for the installed
file; that it was also the loaded module is inferred (one boot after the install, no reload
logged).

The linux series was revised after these runs (tip 01cff214d7d2, the one of the control runs of E445
and E446): the debug switches (kregnow's arm, alias_ctx_rw, render_share_pb, tadata_fill) are
disarmed at a firmware load and at a reset, kregnow's arm, read and write and the host-interrupt
restore run under one lock, a render context that shares a PB holds a reference on its donor until
it is freed, and the cleanup commands and the TA data fill are moved into helpers with the same
order and effect. The scripts of these runs reset the GPU before they arm anything, nothing resets
between the arming and its use, and the shared PB's context is closed before its donor, so the
revision does not change the paths the runs used (read against the diff of the two tips and the
scripts) [infer].
