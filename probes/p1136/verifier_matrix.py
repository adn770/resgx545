#!/usr/bin/env python3
"""Run the landed verifier (tools/fwtask/fwtask.py, read only) over one snippet per form the items 7 to 16
need, inside the trc_31 wrapper of probe_forms.py; writes verifier-matrix.txt.  The verdict is the
assembler's (ASM) or the verifier's first refusal (VER) or ACCEPTED."""
import sys, pathlib
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import probe_forms as PF

ROWS = [
 (7, "ima32.u r11, i0, r5, c56, r4", "high word with the extra operand"),
 (7, "ima32.s r11, i0, r5, c56, r4", "signed, extra operand"),
 (7, "xor.testtanz.chan0 !c0, p0, r5, i0", "test of i0 against a register"),
 (7, "xor.testtanz.chan0 !c0, p0, i0, #0", "test of i0 against 0"),
 (7, "mov i0, r5", "write i0 from a register"),
 (8, "p0 mov r12, #5", "predicated limm"),
 (8, "!p0 mov r12, #5", "negated predicated limm"),
 (8, "p0 mov r12, r5", "predicated register move"),
 (8, "!p0 mov r12, r5", "negated predicated register move"),
 (8, "p0 br @c1", "predicated relative branch"),
 (8, "!p0 br @c1", "negated predicated relative branch"),
 (8, "p0 ba #8198", "predicated absolute branch"),
 (8, "!p0 ba #8198", "negated predicated absolute branch"),
 (9, "ima32.u r10, i0, r10, r10, r10", "high word, one register four times"),
 (10, "xor.testtanz.chan0 !c0, p0, r5, #127", "test immediate 127"),
 (10, "xor.testtanz.chan0 !c0, p0, r5, #128", "test immediate 128 (assembler)"),
 (10, "mov r12, #0x0000ffff\nxor.testtanz.chan0 !c0, p0, r5, r12", "wide value by limm and a register test"),
 (11, "mov r123, #0x12345678\nmov r12, r123", "r123 write and read"),
 (11, "ldad.bypassl1 r123, [r1,+#3], drc0\nwdf drc0", "r123 as a load destination"),
 (12, "ldad.bypassl1 r12, [r1,+#40], drc0\nldad.bypassl1 r13, [r1,+#41], drc0\nwdf drc0", "two loads, one wdf"),
 (12, "ldad.bypassl1.fetch4 r12, [r1,+#40], drc0\nwdf drc0", "ldad with fetch"),
 (12, "ldad.bpcache r12, [r1,+#40], drc0", "ldad.bpcache"),
 (12, "ldad.bypassl1 r12, [r1,+#40], drc1", "ldad on drc1"),
 (12, "mov r12, r1\nldad.bypassl1 r13, [r12,+#40], drc0", "load base copied from the page base"),
 (12, "ldad.bypassl1 r12, [r1,+#40], drc0\nldad.bypassl1 r13, [r12,+#0], drc0", "load base from memory"),
 (13, "ldab r12, [r1,+#40], drc0", "ldab"),
 (13, "ldaw r12, [r1,+#40], drc0", "ldaw"),
 (13, "stab [r1,+#40], r12", "stab"),
 (13, "staw [r1,+#40], r12", "staw"),
 (14, "ima32.u r8, r8, #1, r9.neg", "the one ima32 word (counter increment)"),
 (15, "str #517, r12", "str 0x0814 (allow list)"),
 (15, "ldr r12, #517, drc0", "ldr 0x0814 (allow list)"),
 (15, "str #670, r12", "str 0x0a78 (allow list)"),
 (15, "str #1, r12", "str CR_CLKGATECTL2 (never)"),
 (15, "str #687, r12", "str 0x0abc (a register whose write hangs jobs, E026)"),
 (15, "str #517, r12\nldr r12, r13, drc0", "register-index ldr"),
 (16, "emitpds.tasks.taske #0, r2, r3, r4, #0x0", "emitpds"),
]


def main():
    out = ["%-4s %-17s %-48s %s" % ("item", "verdict", "form", "what")]
    for item, snip, what in ROWS:
        if snip.startswith("str #1,"):
            snip = snip.replace("str #1,", "str #%d," % (0x0004 // 4))
        v, why = PF.verdict(snip)
        first = snip.splitlines()[0] if "\n" not in snip else snip.replace("\n", " ; ")
        tag = {"ACCEPTED": "ACCEPTED", "ASM-REFUSED": "ASM-REFUSED", "VERIFIER-REFUSED": "VER: " + why}[v]
        out.append("%-4d %-17s %-48s %s" % (item, tag[:60], first[:48], what))
    (HERE / "verifier-matrix.txt").write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
