+++
id = "E231"
claim = "No render-level ISP word we can set makes a punch-through pass obey the ISP stencil: with the stencil compare at never and at always alike, every bit of render command words 12, 21 and 22 and the kernel pokes of 0x04dc bits 0 and 2 and 0x04e8 bits 0 and 8 leave the punch-through image at 1062 and 36 pixels in all 202 probes, while command word 12 with any of bits 1 to 5 set, and with all bits set, removes a plain opaque triangle"
unit = "isp"
method = "the probes isp-punch-through-stencil-ptst-never*, -ptst-always* and -ptst-opaque-cmd12-* of probes/isp/punch-through-stencil.toml, one probe a case, fenced (the 64x64 baseline triangle compared with its clean image before and after each), on the laptop with the linux fork and the debug option on, one run (no follow-up run)"
tiers = ["HW"]
date = "2026-11-02"
data = ["isp-punch-through-stencil"]
terms = ["CR_ISP_CTL", "CR_ISP_REG_04DC", "CR_ISP_REG_04E8", "ISP0"]
+++

**What runs.** The punch-through scene of E226 (five copies of the triangle, depth test less, ISP0
0x08400300, a pixel program that loads 0xe001 into r2 and ends in `atst8 ... fb`, the copy's
depth written to o0). ISP word 2 is 0x000000ff (the table's question: stencil at never) in the
`ptst-never` probes and 0x0e0000ff (always) in the `ptst-always` probes. For each of the two
there is a probe with no word changed and 100 more, each changing one word: each of the 32 bits
of render command words 12, 21 and 22 flipped alone (96), the kernel pokes of 0x04dc bits 0 and 2
(rd21) and of 0x04e8 bits 0 and 8 (rd51). Bit 1 of 0x04dc is left out, as it hangs punch-through
passes (E222). The `ptst-opaque-cmd12-*` probes draw the plain opaque triangle (green) with
command word 12 at 0x00000000, 0x000f0102, 0x000f0104, 0x000f0108, 0x000f0110, 0x000f0120 and
0xffffffff.

**Results.** One run; every baseline before and after a probe was clean (0 of 4096 pixels).

- Punch-through. All 202 probes drew 2998 pixels of the background (0xff203040), 1062 of
  0x00000000 (the copy at z 0) and 36 of 0x3d800000 (z 1/16), the image of the scene with
  no stencil (E226), at stencil never and at stencil always, for every word and bit tried.
  Since no case dropped a pixel at never, the always probes were not needed to tell a stencil
  kill from a removed object, and they agree.
- Command word 12 on the opaque triangle. At 0x00000000 the triangle is drawn (1062 pixels of
  green over 3034 of background). With 0x000f0102, 0x000f0104, 0x000f0108, 0x000f0110 or
  0x000f0120 (bits 1 to 5 set on top of 0x000f0100) and with 0xffffffff, the triangle is gone
  and only the background remains. Bit 0 (0x000f0101) is not among these probes; E232 has it.

**Not shown.** Whether another word, one the kernel does not let us set, enables the stencil in a
punch-through pass, or whether none does. What command word 12 bits 5:0 select is in E232 and
E233. Pairs of bits and multi-bit words were not tried beyond 0xffffffff on the opaque triangle,
and bits 13 to 31 of command word 12 were not run on it. The data come from one run.
