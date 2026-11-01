+++
id = "E362"
claim = "With the PB descriptor's flag bit 0 set at a render's first kick the EDM's write to the render context's page faults (CR_BIF_FAULT on page 0x32411000, the requester of its own writes) under the context's directory, where the kernel's memory is read-only, and the job fails; with CR_DPM_REG_074C bit 8 (0x100, and 0x1ff) on contexts for 4096x4096 and 1024x768 targets the render is exact and the TA data is the control's to the dword; two runs and one"
unit = "dpm"
method = "probes/render/word-pokes.toml on the laptop, linux fork b5a86838ae59 with the debug option on: tri with --kpoke-render 1:pb:0^=0x1 (twice) and 1:ta:167=V (V 0x100, 0x1ff; one 64x64 render on contexts declared for 4096x4096 and 1024x768 targets), each with --dump-render, the TA data compared dword by dword with an unpoked control on the same context size; the driver's lines per case"
tiers = ["HW", "infer"]
date = "2026-11-03"
data = ["render-word-pokes"]
terms = ["hw_pb_desc.pb_flags", "CR_DPM_REG_074C", "cmd_ta.dpm_reg_074c", "CR_BIF_FAULT"]
+++

**Results.**

- *PB flag bit 0.* Both runs: "BIF fault 0x80400 at 0x3241100e" (and 0x32411008), 0.11 s after
  the poke; the job fails with -EIO, its target keeps the sentinel, the GPU is recovered and the
  next jobs run exactly. `CR_BIF_INT_STAT` bit 10 is the bit E319's fault of the EDM's own write
  sets; the page is the context's (its HW context at 0x32411000, its PB descriptor at +0x380); the
  low bits name the context's directory list (E360).
- *Bit 8.* With 0x100 and with 0x1ff, at 4096x4096 and 1024x768, the triangle is exact, no fault is
  logged, the cleanup completes, and none of the TA data's dwords differs from the control's.

**What it shows.**

- The EDM's page-table builder, asked for by the flag, writes into the kernel's context page
  through the client's directory before anything else of the job, so with our kernel's read-only
  mapping it cannot run; its stride is still not measured (Q067) [HW] [infer: the builder is what
  the flag starts, E200].
- Whatever bit 8 makes the DPM access near TA data offset 0x6010 on a context whose TA data covers
  it, it leaves the TA data as it was: a read, or a write of the value already there (Q081) [HW].
