+++
id = "E664"
claim = "A model of the ZLS load and the pass over it (sgx-pipe zls.rs pass, load_word, Ctl) reproduces the 30 cases of E467's load run (a flat triangle at z 0.5 over the whole 256 x 128 target, G = 33, depth test never or less) with 0 differences in 983040 counted stored dwords (counts, not dwords: no stored dump exists for this run, so what was compared is the run's class counts and value histograms; 8 x (32768 depth + 8192 stencil) in the ten controls' copy cases, 12 x 32768 in the less cases and 8 x 32768 in the sign cases), as 30 vectors of the kind zls-load: with bit 1 and bit 14 the pass starts from the loaded depth with its sign bit cleared (0xbe800000 stored as 0x3e800000, 0xdeadbeef as 0x5eadbeef, 0xffffffff as 0x7fffffff, 0x80000000 as 0), without them from the clear value 1.0 (every control without both bits stores 1.0 at 32768 dwords); the depth test less against a depth loaded 0.25f and 0.75f by bit K of the dword index (K = 0, 3, 9) draws 16384 of 32768 pixels and stores 0.25f at 16384 and 0.5 at 16384, and against the clear value draws 32768; bit 13 with bit 1 copies each stencil dword of the load buffer to the same index of the store, per 128-dword tile slot (8191 loaded dwords and the dword 0 that is 0 either way), without them the stencil store holds 0; the load-only controls store nothing; the counts are the same under any bijection of the dword indices, so the vectors do not test the address rule (the unit tests now pin the depth address to the store rule and the stencil slot to 128 * (ty * (G + 1) + tx), the stencil slot resting on the identity copy alone, Q121); every vector goes through E465's fitted address rule (the load is read at the address the store writes), so all 30 are reported fitted and none matched; refused by input alone: a compare closer than 3 units of 2^-23 (Q200, 12.3's rule), a compare against a loaded NaN or infinity and an integer format (Q243), a target with edge tiles (Q122), overlapping tiles and a triangle depth other than 0.5 and the ramp's 0.25 to 0.4166 (Q242), bit 19 with a load (Q101), bit 0 (Q244)"
unit = "zls"
method = "offline, no new run: sgx-pipe zls.rs pass and the unit kind zls-load of unitvec.rs against the output lines of the dataset zls-load-copy (the 30 vectors of unit-vectors/zls-load/ built by tools/usse-asm/zls_vectors.py from every result line of output.txt: tests/zls_vectors.rs); the expectation of each vector is the line's own counts in the classes of the run's reduction script (zero, loaded, clear, other) or its stored values; the load buffers are the fills the script names (the dword's index, 0.25f or 0.75f by bit K of it, one value); a vector whose expected draw count or class counts were changed fails (tests/zls_vectors.rs); no stored dump exists for this run, so the checks are the script's counts, not the dwords; the pass-address unit tests of the r124 fold were written to kill two surviving mutants (the stencil slot with pitch G, the depth address with G + 1) and the mutations were rerun"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["zls-load-copy", "unit-vectors-12-4"]
terms = ["CR_ISP_ZLSCTL", "CR_ISP_ZLOAD_BASE", "CR_ISP_ZSTORE_BASE", "CR_ISP_STENCIL_LOAD_BASE", "CR_ISP_STENCIL_STORE_BASE"]
+++

**What ran.** `zls::pass` stores the depth of a target made of whole tiles: with the control's load
bits it starts each pixel from `load_word(buffer[address])`, otherwise from the clear depth; the
flat triangle then replaces it under the depth test less where it is nearer (never replaces
nothing); the result is stored at the address rule's dword. The stencil store is a copy by dword:
slot `ty * (G + 1) + tx`, 128 dwords, the loaded dword where bits 1 and 13 are set and 0 otherwise,
since the in-tile order of the stencil is open (Q121).

**Results.** [HW] The 30 lines of E467's run, 30 of 30 reproduced as counts (an independent
simulator of the pass agrees on all 30, with any address function: the counts do not depend on it);
the counts are in the claim. The
classes of the copy cases are those of the script: with bit 1 and bit 14 the depth store is 32767
"loaded" and one "zero" (dword 0 loaded as 0, which the script cannot tell from a clear), with bit 1
and bit 13 the stencil store likewise 8191 and one; every other case stores one value at 32768
dwords. The control words of the ten cases decode as E467 reads them (E665). [infer] That the
stencil copy and the depth load use the same slots is read from the identity of the copy (E467) and
from E466's stencil count for 1024 x 768; it is not an in-tile order.

**Fitted.** Everything stored goes through E465's address rule, so the verdict is fitted for all 30.
The load itself is E467's measured rule; the sign mask is "a mask or an absolute value" in the
record, and the model uses the mask (the two differ for no dword of this run).

**What it does not show.** Multi-object scenes over a loaded depth: no hardware run of a load with
two objects exists in the data (E628's two-triangle jobs overflow and are the partial render's:
Q038, Q107; the five-copy depth scenes are refused upstream at Q094). `isp::resolve_tile_from`
runs a tile over a loaded start with several objects, tested with synthetic ones only. A run with
one object over a loaded depth exists (E411 part B: 936, 512 and 1382 wrong pixels with a loaded
0.25), but it is counts and hashes, no image dump, and the counts include the background object
and the stencil test, which the pipeline does not model together with a ZLS load: it was not used
to check `resolve_tile_from`. The translucent and opaque order is not done, and the
dataset load-store (the load and store arrangement the plan lists) is unused here. The stencil
test against a loaded stencil, the load of an integer format, a load at another address than the
store's (Q243), the unpatched word 0x0011700a (Q088, a firmware question).
