+++
id = "E149"
claim = "The firmware's HWPerf routine (from instruction 0x1979) appends a 100-byte record to the HWPerf circular buffer, in which it stores the nine registers 0x0044-0x0064 (CR_HWPERF_COUNTER0 to 8) and then the eight registers 0x0e84, 0x0e88, 0x0e8c, 0x0e90, 0x0eb8, 0x0eb4, 0x0ebc and 0x0ec0, once each per record, after a header that holds CR_TIMER; the reads do not depend on the record type, and each of its 33 callers first tests a bit of the HWPerf status word; read from a shader, in one run, 0x0044-0x0064 read 0 twice, 0x0e84, 0x0e88 and 0x0e8c were unchanged over the 24 fmads, and 0x0e90, 0x0eb4, 0x0eb8, 0x0ebc and 0x0ec0 rose"
unit = "platform"
method = "(RE) the ukernel of the cut firmware (00_ukernel.bin of firmware-images, 6637 instructions) disassembled with our usse-dis and read by hand: the routine at 0x1979, its 33 call sites, and every instruction that takes its register number from a register; our disassembly of the firmware, for interoperability; facts only, no code; (HW) probes/platform/hwperf.toml on the laptop, linux fork with the debug option on: a 2048-pixel fill whose shader reads registers 0x0044-0x0060 (case 0), 0x0064, 0x0e84-0x0e90, 0x0eb4-0x0ebc (case 1) and 0x0ec0 (case 2) with ldr, runs 24 fmads and reads them again; one run of each case"
tiers = ["RE", "HW"]
date = "2026-11-02"
data = ["firmware-images", "platform-hwperf"]
terms = ["CR_HWPERF_COUNTER0", "CR_HWPERF_COUNTER1", "CR_HWPERF_COUNTER2", "CR_HWPERF_COUNTER3", "CR_HWPERF_COUNTER4", "CR_HWPERF_COUNTER5", "CR_HWPERF_COUNTER6", "CR_HWPERF_COUNTER7", "CR_HWPERF_COUNTER8", "CR_TIMER", "CR_SOFT_RESET"]
+++

**What was read.** Instruction numbers are indices in hex (byte address / 8). A register named by
its address is the `str`/`ldr` register number times 4. Most of the firmware names the register in
the instruction; the HWPerf routine puts the register number in a register first, so it was read
one call at a time, and so were the other instructions that do the same (listed below).

**Results.** The routine at `0x1979` is entered with four arguments: one word naming two TA3DCtl
dwords to copy (the frame-number and PID dwords of the TA or the 3D side), a record type word, a
value, and the TA3DCtl dword that holds the RT data. It appends one record to the HWPerf buffer
(TA3DCtl dword 43, E002).

- The buffer's dword 0 is the write index, dword 1 the read index and dword 2 a record counter;
  the records start 12 bytes into the buffer, 100 bytes each, 256 slots (the index is kept
  modulo 256). The routine stores the copied dwords, the type, the value and the counter into the
  first 32 bytes, reads `CR_TIMER` (`0x0144`) into the header's last used dword, and increments the
  counter (bit 31 cleared) in the buffer.
- It stores the nine registers `0x0044` to `0x0064` (register numbers `0x11` to `0x19`, read in a
  loop of nine) into the next 36 bytes. An outer count wraps this loop; it compares the count
  with 1 after the first pass, so the loop runs once and never reaches `0x0080`
  (`CR_SOFT_RESET`).
- It then reads eight registers one by one, by constants `0x3a1`, `0x3a2`, `0x3a3`, `0x3a4`,
  `0x3ae`, `0x3ad`, `0x3af` and `0x3b0`, that is `0x0e84`, `0x0e88`, `0x0e8c`, `0x0e90`,
  `0x0eb8`, `0x0eb4`, `0x0ebc` and `0x0ec0`, in that order, into the last 32 bytes; the outer
  count again allows one pass.
- At the end it advances the write index by one, wrapping, unless that would make it equal
  the read index (a full buffer keeps the old index).

None of these reads is guarded by a test of the record type or of the status word. The 33 call
sites (`0x14`, `0x39`, `0x47`, `0x55`, `0x85`, `0xce`, `0x1e4`, `0x37b`, `0x38a`, `0x491`,
`0x508`, `0x5a8`, `0x5bc`, `0x5cd`, `0x5e7`, `0x600`, `0x817`, `0x8e5`, `0xabf`, `0xdb1`, `0xe18`,
`0xe38`, `0xe46`, `0xe54`, `0xe6d`, `0xe87`, `0xeae`, `0x10e3`, `0x1126`, `0x12d8`, `0x1432`,
`0x1506`, `0x157c`) each test the HWPerf status word (`sa19`) first and skip the call when the
tested bits are clear: bit 1 (mask 2) at most of them, bit 3 (mask 8) at the starts of the event
and request tasks, bit 2 (mask 4) once and bits 1 to 3 (mask 14) twice.

The other instructions that take a register number from a register are `0x2c8` (the nine
constants its callers load are `0x2c4`, `0x2e3`, `0xa8`, `0xc1`, `0x1c9`, `0xcd`, `0x2c3`, `0x2e2`
and `0x111`) and the directory-list code at `0x17ec` to `0x184b` (`0x321`, and `0x30d` plus a
count). None of those numbers is in the `0x0e80` block.

**What the registers hold [HW].** The shader reads each register, runs 24 `fmad`s, and reads it
again; the two reads are in the scratch buffer (first reads at +0x00, second at +0x20). The state
of `CR_HWPERF_CTRL` was not read in this run.

| register | first read | second read |
|---|---|---|
| `0x0044` to `0x0064` (nine) | 0 | 0 |
| `0x0e84` | `0x000003cc` | `0x000003cc` |
| `0x0e88` | `0x000003f5` | `0x000003f5` |
| `0x0e8c` | `0x002735b5` | `0x002735b5` |
| `0x0e90` | `0x007cac3f` | `0x007cb2cf` |
| `0x0eb4` | `0x00d39a99` | `0x00d39aa1` |
| `0x0eb8` | `0x00a3e26c` | `0x00a3e8d6` |
| `0x0ebc` | `0x00399615` | `0x003996f6` |
| `0x0ec0` | `0x01a83f74` | `0x01a843b8` |

Over the 24 `fmad`s `0x0e90` rose by 1680, `0x0eb4` by 8, `0x0eb8` by 1642, `0x0ebc` by 225 and
`0x0ec0` by 1092. `0x0ec0` was read in its own job; its first read differs between the pixels
(the four commonest values cover 136 of the 2048 pixels, 1912 pixels read others), and the table
gives the pair that one pixel left in the scratch buffer. The nine zero registers were read in
two jobs (eight in the first, `0x0064` in the
second). All three jobs filled exactly as the control. This is one run, so a register that did not
change here may change in another.

**Not shown.** What the registers count: which unit or event each one measures. Whether the zeros
are because no counter group is enabled (`CR_HWPERF_CTRL` was not read, and no group was set
by this table). Whether `0x0e84` to `0x0e8c` stay constant from run to run. How the host reads the
records, and which events the callers record.
