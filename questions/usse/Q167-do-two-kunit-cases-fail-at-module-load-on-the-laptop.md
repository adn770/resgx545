+++
id = "Q167"
question = "why did gma500_sgx_render (test_pb) and gma500_sgxfive_debug (test_pb_small) report \"Expected pt != NULL\" in the KUnit run at module load on the laptop, when the same suites pass under qemu"
unit = "usse"
kind = "kernel"
phase = 11
evidence = ["E549", "E591"]
terms = []
+++

On the laptop, the KUnit run at module load of the module built from the 11.29 series (srcversion
5AD04F33F6BCDA7B880E238) had one failure in each of these suites: gma500_sgx_render (test_pb) and
gma500_sgxfive_debug (test_pb_small), both "Expected pt != NULL". The author read it as an
allocation failure on the 2 GB machine after the builds [infer]. The series check under qemu passed
the same suites: 106 cases debug off, 157, 164 and 172 debug on. The module-load output was not
kept, so what the cases allocate, and whether the failure repeats on a freshly booted laptop, is not
known. Open: reload the module on a freshly booted laptop, keep the KUnit output, and see whether
the two cases fail again; if they do, find which allocation returns NULL. A repeat that passes would
leave the memory reading standing; a repeat that fails again would be a defect of the cases or of
the code under test.

Narrowed in 11.34 (E591, two module loads on the laptop, up about 29.5 and 30.6 hours, neither a
fresh boot). The load of the module of the runs (34729EB8, one minute after its build) passed all 14
suites with the output kept: `sgx_render_test_pb` and `sgxfive_debug_test_pb_small` ok. The load of
the amended module (B21FDA82, right after a build and a 22 minute series check) failed three other
cases, `sgxfive_coredump_test_bounds`, `sgxfive_debug_test_render_newest` and
`sgxfive_debug_test_render_donor`, each "Expected ctx->mem.va != NULL", with the kernel's "page
allocation failure: order:5, mode GFP_KERNEL|__GFP_ZERO|__GFP_COMP" in the journal from the KUnit
thread, 122 MB free of 2 GB; the kpoke suite passed 32 of 32. So the allocation reading has its
first kernel line [infer: the cases allocate a large contiguous block that a fragmented machine
cannot always give] and it is not specific to the two cases first seen. It does not close this
question: no load has been on a freshly booted laptop, and whether the cases should avoid a
contiguous allocation (a vmalloc or a smaller block) is the kernel's design question this one is.
Open: reload on a freshly booted laptop and keep the output; decide whether the cases allocate
differently.
