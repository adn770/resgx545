+++
id = "E228"
claim = "ISP word 0 bit 11 turns on a two-sided stencil: with it set a back-facing triangle is drawn or not by the stencil word of presence bit 5 and needs the back ISP word 0 of presence bit 3, while a front-facing one keeps the front words; presence bit 4 is optional and the back word 0's own ISP-word-2-present bit is not needed; without bit 11 no back-face case draws; ISP word 0 bit 18 hangs the render"
unit = "isp"
method = "the stencil probes of probes/isp/stencil.toml with the back-face words (st-front-*, st-back-*, ts-*, 35 probes) on the laptop, linux fork with the debug option on: the opaque 64x64 triangle with ISP word 2 and, added to its state block, presence bits 3 (back ISP word 0), 4 (back ISP word 1) and 5 (back stencil word); front-facing, or mirrored in y by the viewport word (0xc2000000, -32.0, no culling) to back-facing; stencil compare never or always (mask 0xff); each unnamed ISP word 0 bit set in turn; every pixel read back, each probe fenced by a baseline render before and after; one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["isp-stencil"]
terms = ["ISP0"]
+++

**What runs.** The block-growing host (presence bits 3, 4, 5 and 7 added to the state block)
first: a region clip written into the grown block (presence bit 7) leaves the triangle whole when
it covers the 64x64 surface (1062 pixels) and cuts it to 432 pixels when it covers tile column 0,
rows 0 and 1, so the grown block is read. Then the stencil cases. The front stencil word is never
(0xff) unless a probe says otherwise. The back words are ISP word 0 = 0x01d00300 (presence bit 3),
ISP word 1 = 0x10f0 (bit 4) and the stencil word always = 0x0e0000ff (bit 5). Two-sided probes set
ISP word 0 of the triangle to 0x01d00b00 (bit 11 added to 0x01d00300). "Drawn" is the triangle's
1062 pixels.

**Results.**

| face | bit 11 | front word | back words | drawn |
|---|---|---|---|---|
| front | clear | always | none | yes |
| front | clear | never | none; or bit 5 always | no, no |
| back | clear | never | none; an always word at bit 3; at bit 5; bits 3, 4, 5 | no (4 probes) |
| back | set | never | bits 3, 4, 5 (back always) | yes |
| back | set | never | bits 3 and 5 | yes |
| back | set | never | bits 3 and 4 | no |
| back | set | never | bit 5 only | no |
| back | set | never | bits 3, 4, 5, back word 0 without its word-2-present bit (0x01d00200) | yes |
| back | set | always | bits 3, 4, 5 with the back stencil never | no |
| front | set | never | bits 3, 4, 5 with the back stencil always | no |
| front | set | always | bits 3, 4, 5 with the back stencil never | yes |

With the back words (bits 3, 4, 5, or bit 5 alone) and bit 11 clear, setting in turn each other
unnamed ISP word 0 bit (10, 12, 13, 14, 19, 28, 29, 30, 31) left the back face removed in all 18
probes; bit 18 hung the job in both of its probes ("job hung, context lost"). Bit 11 itself with
bit 5 alone (no back word 0) drew nothing either.

**What it shows.** With ISP word 0 bit 11 set, a back-facing triangle is decided by the stencil
word of presence bit 5 (always draws it, never removes it) and only when the back ISP word 0 of
presence bit 3 is also present; a front-facing triangle is decided by the front word whatever the
back one holds. Presence bit 4 is not needed, and neither is the back word 0's word-2-present bit.
With bit 11 clear the back words changed nothing: no back-face case drew, with the front word at
never.

**Not shown.** Back faces with bit 11 clear and the front word at always were not run, so that
they then use the front word is not shown. "Back-facing" is the face the mirrored viewport gives
with no culling; culling was not part of this table. The contents of the back ISP word 1 were not
varied, and the back stencil's compare functions other than never and always were not run. What
bit 18 waits on is not shown. One run.
