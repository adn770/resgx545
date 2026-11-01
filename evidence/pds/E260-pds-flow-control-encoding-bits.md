+++
id = "E260"
claim = "bra and call read bits 19-23 as target bits: each of the ten flips sent the fetch 4 << k bytes past the program, where the job faulted with the BIF fault address 0x2e000000 + (4 << k) (low bits aside); rtn's and halt's bits 23:0 and nop's bits 26:0 change nothing the readback shows, and with each nop bit flipped a later pc.0 read gives what the plain nop gives, within the fetch pc's run-to-run variation (E261)"
unit = "pds"
method = "probes/pds/encoding-bits-flow.toml (tools/usse-asm/pds_bits.py) on the laptop, linux fork with the debug option on: as E259, the base instructions 'bra skip' over a marked mov32, 'call sub' with a marked return, 'rtn' in that call, the program's final 'halt', and 'nop' followed by 'mov32 ds0[52], pc.0', each unmapped bit flipped once; the faults from the kernel log the runner kept (pds/encoding-bits-flow/kernel.log); one run"
tiers = ["HW"]
date = "2026-11-02"
data = ["pds-encoding-bits-flow"]
terms = ["CR_BIF_FAULT"]
+++

**Results.**

| form | unmapped bits | flips | outcome |
|---|---|---|---|
| `bra` (target 18 skips one `mov32`) | 23:19 | 5 | each job faulted |
| `call` | 23:19 | 5 | each job faulted |
| `rtn` | 23:0 | 24 | as the base |
| `halt` | 23:0 | 24 | as the base |
| `nop` | 26:0 | 27 | as the base, but bit 2 once: `pc.0` one less |

The ten faults, in order (`bra` bits 19-23, then `call`): status 0x92000 at 0x2e20001a, then
0xd2000 at 0x2e400011, 0x2e800011, 0x2f000011, 0x30000011; `call` the same addresses, the first
0x2e200014. Each address is 0x2e000000 plus 4 << k for the flipped bit k (0x200000, 0x400000,
0x800000, 0x1000000, 0x2000000), so the bit moves the fetch by 2^k instructions of four bytes: it
is part of the target, which so has at least 24 bits. The driver recovered each job; the triangle
and a fill drew exact after the table.

The `nop` bit 2 case read `pc.0` = 0x13 where the base read 0x14; the follow-up (E261) ran it five
times against the plain `nop` five times and both read 0x15 and 0x16 alike, so that was the fetch
pc's own variation, not the bit.
