+++
id = "E097"
claim = "smlsi's swizzle mode makes iteration k of a repeat use the swizzle's k-th component as its register offset (source 1 under wzyx reads r4, r3, r2, r1, under xxxx r1 four times; a destination under wzyx writes r23 down to r20); smoa's offsets shift an operand's register number on every instruction (destination +1 writes r11, source 1 +1 or +2 shifts a repeat8 by that much), and with an smr range R and mode repeat the destination index wraps once, to index - R (smr 2, 4, 8 put r20 at r18, r16, r12, and offset +2 moves each up two); moest writes no register and no scratch dword and setfc changes nothing a load or a repeat shows"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/moe.toml, probes swizzle, smr-smoa, window, smoa-all-repeat, moest-dest, moest-store and setfc, fills whose pixel program sets the MOE state and runs a mov, mov.repeat4 or mov.repeat8 on preset registers, then dumps the temporaries to scratch; one run each"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-moe"]
terms = []
+++

**What runs.** The state is set by `smlsi`, `smr` and `smoa`, then `mov.repeat4 r20, r1`
(swizzle), `mov r10, r1` and `mov.repeat2` (smr-smoa), or `mov.repeat8 r20, r1`
(window, smoa-all-repeat); registers hold distinct values so a destination names its source.

**Results.**

- Swizzle, source 1: `swizzle(wzyx)` writes r4, r3, r2, r1 to r20 to r23; `xxxx` writes r1 four
  times, `yyyy` r2 four times, `xyzw` r1 to r4. With the destination in swizzle mode and
  sources incrementing, `wzyx` puts the four values into r23 down to r20.
- smoa offsets: `smoa #1, #2, #0, #0, none x4` then `mov r10, r1` writes r11 (r10 keeps
  its preset), and `mov.repeat2 r10, r1` writes r11 and r12. `smoa #0, #0, #1, #0` before
  `mov.repeat8 r20, r1` makes r20 to r27 take r2 to r9 in none, repeat, clamp and mirror
  mode; with offset +2 on source 1 they take r3 to r10.
- smoa mode repeat on the destination with smr R: `mov.repeat8 r20, r1` writes the eight sources to
  r18 to r25 (R = 2), r16 to r23 (R = 4) and r12 to r19 (R = 8); with destination offset +2 to
  r20 to r27, r18 to r25 and r14 to r21; a plain `mov r20, r1` with offset +6 and R = 4 writes
  r22. The index is 20 + offset, 4 or R taken off once, then the iterations count up with no
  second wrap. Source 1 in repeat mode with R = 4 does not wrap (r20 to r27 get r1 to r8, and
  r3 to r10 with offset +2).
- moest: in moest-dest (10 cases) the destination register or internal register keeps its
  preset; in moest-store (11 cases, selectors 0 and 6, a register holding the scratch
  address) the dump of all 11 is identical and holds no extra scratch dword. setfc #0-#1,
  #0-#1 (setfc, 5 cases): the dump is identical to the same program without setfc, for a
  plain ldad and a mov.repeat4.

**Not shown.** The state persists past the probed instruction: the dump instructions of the
same program run under it (a clamp or mirror on the destination scrambles the dump), which is
why the all-register tables clear it after the instruction. The clamp and mirror modes are
not covered here. One run.
