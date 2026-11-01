"""Which forms the landed verifier accepts: assemble one snippet inside the trc_31 wrapper
and report assembler / verifier verdicts.  Read-only against ~/src/resgx545 (no bytecode)."""
import os, sys, pathlib
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
sys.dont_write_bytecode = True
R = pathlib.Path.home() / "src/resgx545"
os.environ.setdefault("FWTASK_USSE_ASM", str(R / "tools/usse-asm/usse-asm"))
sys.path.insert(0, str(R / "tools/fwtask"))
import fwtask as F

WRAP = """@entry 0
        mov r1, #0xdeadbeef                 ; @patch res+0
        ldad.bypassl1 r2, [r1,+#1], drc0
        wdf drc0
        and.testtanz.chan0 !c0, p0, r2, r2
        p0 br @work
tail:
        mov r30, #0xdeadbeef                ; @patch cont0
        mov pclink, r30
        lapc
work:
        xor.testtaz.chan0 !c0, p1, r2, #1
        p1 br @c1
        br @tail
c1:
%s
        mov r9, #0xdeadbeef                ; @patch res+272
        stad [r9,+#0], r12
        br @done
done:
        mov r3, #0x00000002
        stad [r1,+#2], r3
        br @tail
"""

def verdict(body):
    src = WRAP % "\n".join("        " + l for l in body.strip().splitlines())
    try:
        lines, entries, patches = F.preprocess(src)
        words = F.assemble_text("\n".join(lines))
    except Exception as e:
        return "ASM-REFUSED", str(e).splitlines()[0][:90]
    err = F.verify_why(words, patches, F.load_regs(), entries)
    if not err:
        return "ACCEPTED", ""
    return "VERIFIER-REFUSED", "; ".join(f"{w}" for _, w, _ in err[:2])

if __name__ == "__main__":
    for blk in sys.stdin.read().split("\n---\n"):
        v, why = verdict(blk)
        print(f"{v:17s} {why:50s} | {blk.strip().splitlines()[0]}")
