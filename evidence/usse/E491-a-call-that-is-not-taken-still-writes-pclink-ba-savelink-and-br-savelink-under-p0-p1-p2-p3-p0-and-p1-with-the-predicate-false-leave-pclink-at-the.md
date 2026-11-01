+++
id = "E491"
claim = "A call that is not taken still writes pclink: with the predicate false, ba.savelink and br.savelink left pclink at the index of the instruction after the call in all 16 not-taken calls of the fill table (p0, p1, p2 and p3 false for each form, !p0 and !p1 with the predicate false, p0 with pclink preset 0 and 0x3ffff and with the next instruction at index 48 and 84), in all 3 not-taken calls of a chain of two calls, and in all 10 jobs of five placed programs (5 programs, 2 jobs each, at heap offsets 0x10000 and 0x1ff000); the reading that a call not taken leaves pclink as it was fits none of them (0 of 16, 0 of 3, 0 of 10), and the taken calls write the same link (2 of 2 in the fill table, 4 of 4 placed jobs)"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1124 (sha256 58907b06a8e9030472a809cd669d2c3823946fd67aaf4775f942704a90f6a5ae): probes/usse/callfalse2.toml (dump.s, 2 probes: link 18 cases and chain 3), the same table run before it as probes/usse/callfalse.toml (usse-callfalse, kept as ran), and 7 of the 17 probes of probes/usse/place-more.toml (the false and the taken call in a placed program, 2 jobs each, the same program twice: 14 jobs); the campaign runner once for each table, no probe.py first run. The first table, callfalse, is a table error of mine: its label and expected index for the next instruction read 25 where the call's next instruction is at index 24 (r12 and r15 read 24 in every case), so its link probe read NONE of the hypotheses; its 21 cases (18 + 3) were run again under callfalse2 with the index corrected, and the scratch words of all 21 cases are the same in the two runs, so each case was run twice with identical readbacks. The placed probe br-true carries the question text of the false-call probes (it says 'not taken'), but its predicate is true: its two jobs per offset are the taken controls"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-callfalse2", "usse-callfalse", "usse-place-more"]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

**What runs.** The fill program sets pclink to 0x77 (or 0 or 0x3ffff), sets p0-p3 with
`and.testtanz.chan0 !c0, pN, rK, rK` from r1-r4, then `<pred> ba.savelink #L` or `<pred> br.savelink
#4`, a fall-through marker `mov r11, #2`, and `mov r15, pclink` right after the call and at the
target. r12 holds the index of the instruction after the call, as the assembler resolves it. The 18
link cases, by what the call is: `ba.savelink` under p0, p1, p2 and p3 with the predicate false (4),
under `!p0` and `!p1` with p0 and p1 set so that the predicate is false (2); `br.savelink` under p0,
p1, p2 and p3 false (4) and under `!p0` with p0 set (1); `p0 ba.savelink` false with pclink preset 0
and 0x3ffff (2), `p0 br.savelink` false with pclink preset 0 (1), and `p0 ba.savelink` and `p0
br.savelink` false with the next instruction at index 48 and 84 (2): 16 calls not taken. Two cases
are taken calls, `!p0 ba.savelink` with p0 clear and `!p1 br.savelink` with p1 clear. The chain
probe runs `p0 br.savelink` and then `p1 ba.savelink` (next instructions at 22 and 26) with (p0, p1)
= (0, 1), (1, 0) and (0, 0), reading pclink after each call: the cases (0, 1) and (0, 0) leave the
first call not taken (and the second taken or not taken), and (1, 0) takes the first call to index
26, past the second, so it contains no call not taken: 3 calls not taken in all. The placed programs
(sgxfive-test `--place OFFSET=FILE --place-form cbase`, as E476) preset pclink 0x77, set p0, run one
call and return the link read after it in o0: `p0 br.savelink #1` with p0 clear at 0x10000 and at
0x1ff000, `!p0 br.savelink #1` with p0 set at both, `p0 ba.savelink #8198` with p0 clear at 0x10000
only (5 programs, 2 jobs each), and `p0 br.savelink #1` with p0 set (taken) at both offsets (4
jobs).

**Results.** Fill: r15 = r12 = the index after the call in the 16 not-taken calls and in the 2 taken
ones, r11 = 2 in the 16 not-taken calls and still 0xa4a5a6a7 in the 2 taken ones, for every
predicate and call form above, every preset (0x77, 0 and 0x3ffff) and at the indices 24, 48 and 84;
the preset was never read back. Chain: after the first call the link is 0x16 although the call was
not taken (cases (0, 1) and (0, 0)), and after the second 0x1a, taken or not; case (1, 0) leaves
0x16, the link of the taken call. Placed: o0 = 0x2006 at 0x10000 in the 6 not-taken jobs and the 2
taken ones, 0xfe06 at 0x1ff000 in the 4 not-taken and 2 taken jobs; 0x77 is never read. No job
failed (kernel.log holds the campaign marks only).

**What it shows.** [HW] The call writes its link whether or not its predicate holds, for
`ba.savelink` and `br.savelink`, under p0 to p3 and under `!p0` and `!p1`, in a fill and in programs
placed at 0x10000 and 0x1ff000 (E475 had one case, `p0 ba.savelink` in a fill). The model of the
probe tables, that a call not taken leaves pclink as it was, fits none of the 29 not-taken cases (16
calls, 3 calls and 10 jobs). A call not taken overwrites a link the program needs: save pclink
before a predicated call. [infer] That `!p2` and `!p3` calls cannot be run is the assembler's
refusal (`!p0` and `!p1` assemble), not a hardware result.

**What it does not show.** `ba.savelink` not taken at 0x1ff000 or at any placement besides 0x10000
(the placed `ba` was one program, two jobs); `lapc` under a false predicate, a call with a repeat,
`.nosched` on a call (refused by the assembler); a call not taken in a firmware task (Q124); whether
the link is written before the predicate is known (only the resulting link is seen); a predicate
other than the four p registers and two negations listed. Narrows E475's one case to the forms and
placements above.
