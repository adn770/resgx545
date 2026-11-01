+++
id = "E467"
claim = "A render loads depth only with CR_ISP_ZLSCTL bits 1 and 14 and stencil only with bits 1 and 13 (neither without bit 1; load-only controls without the store enables store nothing), the loaded dword read at the address the store uses (32768 of 32768 depth dwords and 8191 of 8191 stencil dwords copied to the same index of a second buffer; stencil dword 0 cannot be told from the clear value 0), the loaded depth takes part in the depth test (16384 of 32768 pixels drawn when half the loaded depth is 0.25f and half 0.75f against the triangle at 0.5, less), and the sign bit of a loaded depth is cleared (0xdeadbeef stored as 0x5eadbeef, 0xffffffff as 0x7fffffff, 0x80000000 as 0)"
unit = "zls"
method = "probes/zls/load-copy.toml (load-copy.sh) on the laptop (direct cable), linux fork 6ee9501832af: sgxfive-test tri --tri-full --tri-z 0.5,0.5,0.5 on a 256 x 128 target with --depth, --depth-store, --stencil and --stencil-store (a load buffer and a store buffer each for depth and stencil, the load buffers holding each dword's index or 0.25f / 0.75f by a bit of the index, the store buffers 0xdeadbeef), G (bits 11:3) 33, the controls 0x0017110c plus bits 1, 13 and 14 in every combination, and 0x0011710a (load only); depth test never (blk:1 = 0x00000200) and less (0x00400200); reduced on the laptop (python3); one run of each case, each dataset ran once, after one run by hand of the script (outside the data) whose label of stencil dword 0 was changed afterwards; the dataset holds output.txt, kernel.log, env.toml and the script and no raw dumps, so the counts are the script's own at run time"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["zls-load-copy"]
terms = ["CR_ISP_ZLSCTL", "CR_ISP_ZLOAD_BASE", "CR_ISP_ZSTORE_BASE", "CR_ISP_STENCIL_LOAD_BASE", "CR_ISP_STENCIL_STORE_BASE"]
+++

**What runs.** `tri --depth --depth-store --stencil --stencil-store` (new in this phase) maps four
buffers and points the load and store bases of the depth (`0x0484`, `0x0488`) and the stencil
(`0x048c`, `0x0490`) at them with kernel pokes; the triangle covers the 256 x 128 target at depth
0.5. With the depth test never (`blk:1 = 0x00000200`) the triangle changes no depth, so what a
store holds is the clear value or what was loaded. The load buffers hold each dword's index
(`--depth-fill index`), so a stored dword equal to its own index was loaded from the same address.
One run of each case; no case was repeated. The script was run once by hand before the campaign
(outside the data, debug/phase11/lc.out): its reduction labelled the stencil's dword 0 "the loaded
dword" even without bit 1, and the campaign script changed the label so that dword 0 is reported
as ambiguous with the clear value 0 (8191 of 8192 stencil dwords are told apart; the depth's dword
0 is 0, not the clear 1.0, so all 32768 are).

**Which bit loads what.** With the store control 0x0017110c (G = 33) plus:

| bits added | depth store (32768 dwords) | stencil store (8192 dwords) |
|---|---|---|
| none, 1, 13, 14, 13 and 14 | 1.0, the clear value, at 32768 | 0, the clear value, at 8192 |
| 1 and 13 | 1.0 at 32768 | the loaded dword at 8191 of 8191 (dword 0 is 0, as the clear value is) |
| 1 and 14 | the loaded dword at 32767 of 32767 | 0 at 8192 |
| 1, 13 and 14 | the loaded dword at 32767 of 32767 | the loaded dword at 8191 of 8191 |
| 1, 13, 14 on the load-only control (0x0011d10a), and 1 on 0x0011710a | nothing stored | nothing stored |

So bit 1 turns the load on, bit 14 selects the depth and bit 13 the stencil, and neither acts
without bit 1. This answers the first part of Q088. The loaded dword is read at the index the
store writes: the copy is the identity at 32768 of 32768 depth dwords and 8191 of 8191 stencil
dwords (stencil dword 0 is 0 in both the load and the clear). The load-only controls (store
enables 17 and 18 clear) leave both store buffers untouched.

**The loaded depth is used.** With the depth test less and the depth buffer holding 0.25f where bit
K of the dword's index is 0 and 0.75f where it is 1 (K = 0, 3 and 9), the triangle at 0.5 is drawn
on 16384 of 32768 pixels, the others kept at 0.25f, with bits 1 and 14 and with bits 1, 13 and 14,
and on all 32768 pixels (stored depth 0.5) without bit 14 (control 0x0017110c, or bits 1 and 13):
the loaded depth feeds the depth test. The stored depth is 0.25f at 16384 dwords and 0.5 at 16384.

**The sign is cleared.** With bits 1, 13 and 14 and the depth test never, a loaded -0.25f is
stored as +0.25f (0xbe800000 as 0x3e800000, 32768 dwords), 0xdeadbeef as 0x5eadbeef, 0xffffffff as
0x7fffffff and 0x80000000 as 0x00000000: the depth is a 31-bit magnitude on load [infer: a mask of
the sign bit or an absolute value]. This is the 0x5eadbeef of E411 (the target's sentinel loaded
as a depth).

**What it does not show.** The stencil test against a loaded stencil (no stencil compare was set
up in the state block; the loaded stencil is seen only through its copy); the load of the integer
formats of E466; a load at another pitch or offset than the store's, or one buffer for the load
and the store as in E411 (here the load and the store bases point at four different buffers, each
tile read at the index it is written); whether the load reads 31 bits as a mask or the float's
absolute value (0xbe800000 to 0x3e800000 and 0x80000000 to 0 do not tell [infer]); the partial
render's reload (Q038, E468).
