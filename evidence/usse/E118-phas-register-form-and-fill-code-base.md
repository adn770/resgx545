+++
id = "E118"
claim = "A fill's shader starts at its code base (pclink read after a call at instruction 5 gives 6 in both runs); in a two-phase pixel program phase 1 closed by phas.end completes with every one of the 1062 pixels written, with or without a call or a pclink move; phas's register form, phas srcA, srcB, started no next phase from the next phase's absolute index, an offset or the doutu U0 layout against the immediate form's fields or its whole high dword: six cases hung, one faulted and the offset case completed with 166 pixels of neither phase's colour"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/phases.toml, probes usse-phases-filladdr (client fill), usse-phases-phasreg-0 to -3, usse-phases-phasreg-diag-call, -diag-link, -diag-neither and usse-phases-phasreg2-0 to -4 (the triangle's pixel shader pix_phas_reg.s), one probe a case, one run"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["usse-phases"]
terms = []
+++

**What runs.** In the fill probe `br.savelink #1` stands at instruction 5 and `mov r20, pclink`
follows; the pixel is r20. The pixel program of the other probes has an immediate `phas` that
starts phase 1 at instruction 8. Phase 0 can make a call and move pclink into r5 (the absolute
index of instruction 2), and computes the index of a phase 2, its offset from phase 1's start
(3), the immediate form's high fields (`0x00000002`), and for the second group the whole high
dword (`0xFA440002`) and the doutu U0 layout (index shifted by 4, temporaries in bits 31:24).
Phase 1 starts with `phas srcA, srcB` and writes o0 red; phase 2 writes it blue. Blue pixels
would show that the register form started phase 2. The controls close phase 1 with
`phas.end #0, #0, pixel, end, parallel` and have no register `phas`.

**Results.** The fill reads 6 for pclink in both runs, so its code starts at its base and its
`phas #N` names local index N. Controls: with the call and pclink move (phasreg-0), with only
the call, only the move, or neither, the job completes and writes 1062 pixels of `0xffff0000`
(red). The register forms:

| srcA | srcB | result |
|------|------|--------|
| phase 2's absolute index (r5) | fields (r7) | hung |
| fields | absolute index | faulted |
| offset (r8) | fields | completed: 166 pixels of `0xff00ff00`, no red or blue |
| absolute index | whole high dword | hung |
| whole high dword | absolute index | hung |
| U0 layout | 0 | hung |
| 0 | U0 layout | hung |
| U0 layout | fields | hung |

Each hang ended `job hung, context lost (Connection timed out)` and the fault `job faulted,
context lost (Input/output error)`; every baseline triangle before and after was exact.

**What it shows.** The register form is an instruction that changes how a task runs, but none
of these sources started phase 2: the six hangs and the fault leave its sources open. The
offset case completes with pixels that no phase of the program writes in those colours (the
colour `0xff00ff00` is the baseline triangle's, **[infer]** left by the previous job), so the
offset form probably ended the task without writing its pixels.

**Not shown.** That a pixel program without a `phas` hangs, and that a phase closed by `nop.end`
with no `phas` declaring it the last hangs, are not tested here apart from these cases: every
register-form case closes phase 1 with `nop.end` and one of them completed. One run per probe.
