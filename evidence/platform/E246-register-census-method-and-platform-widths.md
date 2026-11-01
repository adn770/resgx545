+++
id = "E246"
claim = "Of the registers the glossary places at an offset, and the 13 the firmware or the init script touches with no row, 118 were written with all ones and zero through /dev/mem with the firmware live and idle and put back, in ten batches after each of which a fill and the triangle came out exact with no MMU fault, in two runs that agree in every implemented bit; the 109 others stay read-only for a reason the table gives; the method reproduces the bits earlier records measured for 0x0418, 0x04dc, 0x0520 and 0x0368; CR_HWPERF_CTRL takes bits 12:0, the nine HWPerf counters take no write, and 0x0b30 takes bits 8 and 0"
unit = "platform"
method = "probes/platform/register-widths.toml on the laptop, linux fork with the debug option on: regwidth.c through /dev/mem writes each register with all ones, its prior value, zero and its prior value, reading after each write, with the firmware live and idle, in ten batches with a debugfs fill and the triangle checked after each; two runs"
tiers = ["HW"]
date = "2026-11-02"
data = ["platform-register-widths"]
terms = [
    "CR_HWPERF_CTRL", "CR_HWPERF_COUNTER0", "CR_HWPERF_COUNTER8", "CR_REG_0810", "CR_REG_0814",
    "CR_REG_0818",
]
+++

**What runs.** The table lists every register the glossary places at an offset and the 13 registers
the firmware or the init script touches with no glossary row (0x040c, 0x0410, 0x0430, 0x0444,
0x0448, 0x044c, 0x0450, 0x04c4, 0x0730, 0x0740, 0x0b30, 0x0b80, 0x0b84): 227 in all. Each is either
written (118, in ten numbered batches) or kept read-only (109), each read-only register with its
reason in the table. The campaign runner refuses a table that writes a register of the program's own
deny list. In these runs that list held the clock gating registers, the soft reset, the event
enable, clear and status registers, the VDM start, the ISP start render, the DPM 3D deallocate and
the DPM tasks (0x0680 to 0x06a0), the USSE code bases, the event-to-PDS registers, the PDS execution
base, the event kicker, kicks, timer and PDS invalidates, the EDM task registers and every BIF
register. The table kept read-only the registers the init script sets once, the cache
invalidates, the signatures and status words, the USSE slot and service registers, the DPM status
registers and those whose write the kernel's register file treats as starting work. Since these
runs the program's deny list also holds every one of them whose write starts work, invalidates a
cache or could inject a task (0x0224, 0x024c, 0x0430, 0x043c, 0x0450, 0x0648, 0x064c, 0x0658,
0x0804, 0x0a08, the USSE slot and service registers, 0x0e80), so that a mis-edited table cannot
write them; the census wrote none of them.

For each written register the program reads it twice (a register that moved between the reads would
not be written; none did), writes all ones, reads, writes the prior value, reads, writes zero,
reads, writes the prior value and reads. Before each batch the script asks the kernel for a
debug-group register write of 0x0810 with its own value, which the kernel takes only with the
firmware live and no job queued; after each batch it runs the debugfs fills and the 64x64 triangle
and reads the MMU fault count. The gate is checked once before the batch's writes and not held: a
job queued between the gate and the writes would not have been excluded, and only the check after
the batch would show its effect.

**Safety.** All ten checks of both runs pass: every fill reads correct, the triangle reads `diff:
0`, the MMU fault count stays 0, and every written register reads its prior value at the end. The
read-only registers read the same before and after the census except those that move with time or
jobs: in both runs `CR_TIMER` (0x0144), `CR_SETTLE_POLL0` (0x0308), `CR_EVENT_TIMER` (0x0acc), the
EDM's task register `CR_USE0_SERV_EVENT` (0x0b14), the USSE service status registers 0x0b0c,
0x0b10, 0x0b18, 0x0b88 and 0x0b94 and `CR_BIF_BANK0` (0x0c78); in the first run also the BIF
directory list bases 0x0c38 and 0x0c84 of the triangle's context.

**The method against earlier records.** Batch 1 holds five registers measured before: 0x0418 takes
bit 0, 0x04dc bits 2:0, 0x0520 bits 31:0 (as through kreg, E067) and 0x0368 bits 14:0 (as the TA
command loaded it, E054). The fifth, 0x02b4, reads 0x000000ff after a write of zero as after all
ones: the host cannot write it (E054 saw the value it holds).

**Platform registers.**

| register | name | value before | bits that took a write | width | read 1 after zero |
|---|---|---|---|---|---|
| `0x0040` | `CR_HWPERF_CTRL` | `0x000001ff` | 12:0 | 13 | - |
| `0x0044` | `CR_HWPERF_COUNTER0` | `0x00000000` | 0x00000000 | 0 | - |
| `0x0048` | `CR_HWPERF_COUNTER1` | `0x00000000` | 0x00000000 | 0 | - |
| `0x004c` | `CR_HWPERF_COUNTER2` | `0x00000000` | 0x00000000 | 0 | - |
| `0x0050` | `CR_HWPERF_COUNTER3` | `0x00000000` | 0x00000000 | 0 | - |
| `0x0054` | `CR_HWPERF_COUNTER4` | `0x00000000` | 0x00000000 | 0 | - |
| `0x0058` | `CR_HWPERF_COUNTER5` | `0x00000000` | 0x00000000 | 0 | - |
| `0x005c` | `CR_HWPERF_COUNTER6` | `0x00000000` | 0x00000000 | 0 | - |
| `0x0060` | `CR_HWPERF_COUNTER7` | `0x00000000` | 0x00000000 | 0 | - |
| `0x0064` | `CR_HWPERF_COUNTER8` | `0x00000000` | 0x00000000 | 0 | - |
| `0x0b30` | - | `0x00000100` | 8, 0 | 2 | - |

`CR_HWPERF_CTRL` holds 0x1ff and takes bits 12:0: the group field the firmware writes from the
HWPerf status (bits 12:9) and the nine bits below it. The counters read 0 and stay 0 whatever is
written. 0x0b30, set once to 0x100 by the init script and never reached by the firmware, takes bits
8 and 0, as `CR_ISP_REG_04E8` does (0x100 at boot, bits 8 and 0, E067).

**Not shown.** What a bit that took a write does; whether a bit that reads 0 after all ones is
absent, write-only or cleared by the hardware; the bits of the read-only registers, which were only
read. The second run's values are the table's; the first run's are kept beside them in the dataset
and give the same bits for every register; they differ only in the value 0x0674 held before and
after (a job between the runs set it).
