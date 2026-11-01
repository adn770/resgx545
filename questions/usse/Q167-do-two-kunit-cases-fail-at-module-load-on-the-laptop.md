+++
id = "Q167"
question = "why did gma500_sgx_render (test_pb) and gma500_sgxfive_debug (test_pb_small) report \"Expected pt != NULL\" in the KUnit run at module load on the laptop, when the same suites pass under qemu"
unit = "usse"
kind = "kernel"
phase = 11
evidence = ["E549"]
terms = []
+++

On the laptop, the KUnit run at module load of the module built from the 11.29 series (srcversion
5AD04F33F6BCDA7B880E238) had one failure in each of these suites: gma500_sgx_render (test_pb) and
gma500_sgxfive_debug (test_pb_small), both "Expected pt != NULL". The author read it as an
allocation failure on the 2 GB machine after the builds [infer]. The series check under qemu
passed the same suites: 106 cases debug off, 157, 164 and 172 debug on. The module-load output was
not kept, so what the cases allocate, and whether the failure repeats on a freshly booted laptop,
is not known. Open: reload the module on a freshly booted laptop, keep the KUnit output, and
see whether the two cases fail again; if they do, find which allocation returns NULL. A repeat that
passes would leave the memory reading standing; a repeat that fails again would be a defect of the
cases or of the code under test.
