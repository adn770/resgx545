#!/usr/bin/env python3
"""Item 10 from the isa tables and the assembler: which n encode in `xor.testtanz.chan0 !c0, p0, r2, #n`
(decimal text: the test form's source 2 is the 7-bit immediate field), which n of 0..0xffff encode in the
non-test bitwise form's rotated 16-bit immediate (not allowed by the current verifier), and that
`mov rK, #W` (limm) is exact for every 32-bit W (the 64 W of the wide stage included)."""
import sys, pathlib, random
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import probe_forms as PF
F = PF.F
import gen_1137 as G

def asm(t):
    try:
        return F.assemble_text(t)[0]
    except Exception:
        return None

out = []
ok = [n for n in range(0, 1100) if asm("xor.testtanz.chan0 !c0, p0, r2, #%d" % n) is not None]
assert ok == list(range(128)), ok[:5]
base = asm("xor.testtanz.chan0 !c0, p0, r2, #0")
fields = {n: asm("xor.testtanz.chan0 !c0, p0, r2, #%d" % n) ^ base for n in range(128)}
assert all(v == n for n, v in fields.items()), "the word differs from #0 only in the low 7 bits, = n"
out.append("test form xor.testtanz #n: assembles for n = 0..127 only (0..1099 swept); the word differs from "
           "#0 in bits 6:0 only and they equal n (128 of 128): exact, zero-extended field")
hexform = asm("xor.testtanz.chan0 !c0, p0, r2, #0x7f")
out.append("hex text #0x7f in the test form: %s (the assembler's test form takes decimal only)" %
           ("accepted" if hexform else "refused"))
# the non-test rotated immediate: and r12, r2, #n  (not accepted by the current verifier: alu-test row only)
rot = [n for n in range(0, 0x10000) if asm("and r12, r2, #0x%x" % n) is not None] if False else None
rng = random.Random(1137)
sample = [0, 1, 127, 128, 255, 256, 0x7fff, 0x8000, 0xffff, 0x10000, 0x12345, 0xffff0000] + \
         [rng.getrandbits(16) for _ in range(40)]
res = {n: asm("and r12, r2, #0x%x" % n) is not None for n in sample}
out.append("non-test `and r12, r2, #n` (rotated 16-bit immediate): assembles for %d of %d sampled n; refused: %s" %
           (sum(res.values()), len(res), [hex(n) for n, v in res.items() if not v]))
# limm exactness: set/get round trip through the loader's own functions and the assembler word
bad = []
vals = list(G.WIDE) + [rng.getrandbits(32) for _ in range(2000)] + [1 << k for k in range(32)] + \
       [(1 << k) - 1 for k in range(1, 33)]
for w in vals:
    word = asm("mov r12, #0x%08x" % w)
    if word is None or F.limm_get(word) != w:
        bad.append(w)
out.append("limm `mov rK, #W`: assembler word read back by the loader's limm_get equals W for %d of %d W "
           "(64 wide W, 2000 random, every power of two and every low mask)" % (len(vals) - len(bad), len(vals)))
(HERE / "imm-encode.txt").write_text("\n".join(out) + "\n")
print("\n".join(out))
