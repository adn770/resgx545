+++
id = "C0440"
source = "emgd-psb_regs"
locator = "drm/emgd/include/psb_regs.h:76"
link = "https://github.com/EMGD-Community/intel-binaries-linux/blob/e6884ec2eaaf1afe88d5ff9dd44d70403525be5b/drm/emgd/include/psb_regs.h#L76"
quote = "#define _PSB_C_CLKGATECTL_TSP_CLKG_MASK         (0x3 << 8)"
terms = ["CR_CLKGATECTL.TSP_CLKG"]
+++

Line 76 of `psb_regs.h` in Intel's EMGD register list (psb_regs.h) defines
`_PSB_C_CLKGATECTL_TSP_CLKG_MASK`. It backs the glossary bit field `CR_CLKGATECTL.TSP_CLKG`:
clock-gating mode of the TSP (0 on, 1 off, 2 auto per psb_regs.h).
