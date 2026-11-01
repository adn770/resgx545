+++
id = "E360"
claim = "TA/3D control block dword 49 is the bus interface directory list the EDM last gave a render context: the k-th context's first kick after a reset writes its page directory into CR_BIF_DIR_LIST_BASEk (k 1 to 14) or, at the 15th, CR_BIF_DIR_LIST_BASE0, and dword 49 reads k mod 15; list 15 keeps the EDM's own directory; a 16th live context takes list 1 from the first, whose next kick takes list 2, and all 30 contexts of two runs (14 and 16 alive at once) render their second render exactly; one run"
unit = "render"
method = "probes/render/context-lists.toml on the laptop, linux fork b5a86838ae59 with the debug option on: after a debugfs reset, 14 and then 16 sgxfive-test tri processes (each its own VM and render context) started one at a time; each renders a 128x128 triangle, then blocks writing its pixels into a pipe read once all are started; after each first render the control block's dword 49 (debugfs buf09), CR_BIF_DIR_LIST_BASE0 and BASE1 to BASE15 (debugfs regs) and the context's page directory (render_words ctx:2, saved by --words); then every process renders again on its live context; the EDM dataflow view (edm_dataflow.md) for the routine that writes the dword"
tiers = ["HW", "RE", "infer"]
date = "2026-11-03"
data = ["render-context-lists"]
terms = [
    "ta3d_ctl.render_context_count", "CR_BIF_DIR_LIST_BASE0", "CR_BIF_DIR_LIST_BASE1",
    "CR_BIF_DIR_LIST_BASE15", "CR_BIF_FAULT", "hw_render_context.pd_dev_paddr",
]
+++

**Results.**

- After the reset dword 49 reads 0 and the 14 client lists are 0; BASE15 holds 0x04d33000 (the
  EDM's directory, the address the kernel logs at boot) and BASE0 a directory left from before.
- The k-th context's first kick: dword 49 = k and BASEk = its directory (ctx:2), k = 1 to 14 in
  both runs; with 16 contexts the 15th context's directory goes to BASE0 with dword 49 = 0 and
  the 16th to BASE1 (replacing the first context's) with dword 49 = 1.
- Released together, every second render is exact (2 renders ok, 30 of 30). With 16 alive,
  at the end dword 49 reads 2 and BASE2 holds the first context's directory: its second kick,
  finding its directory in no list, took the next one, from the second context, whose second
  render had run.
- Faults name the list in `CR_BIF_FAULT` bits 3:0, the kernel reading the directory back from
  BASEn (sgxfive_fault_pd) [DDK]: list 8 in E362's fault (0x32411008), list 1 in E357's held fault
  (0x3e000001).
- In the EDM dataflow the dword is read and written in one routine (0x17ec-0x184b), which also
  writes registers whose number it computes and writes `CR_BIF_CTRL` (edm_dataflow.md §3, §6).

**What it shows.**

- Dword 49 is the index of the directory list last assigned, 0 to 14, bound at 15 because the bus
  interface has 16 directory lists and the EDM keeps one [HW] [RE]; a kick whose directory is in
  no list takes the next, so a live context survives losing its list [HW: one run].
- E314's "moves at each context's first kick, not at its later kicks" holds while no context has
  lost its list [HW].
