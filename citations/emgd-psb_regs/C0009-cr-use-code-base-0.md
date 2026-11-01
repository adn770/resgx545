+++
id = "C0009"
source = "emgd-psb_regs"
locator = "drm/emgd/include/psb_regs.h:422"
link = "https://github.com/EMGD-Community/intel-binaries-linux/blob/e6884ec2eaaf1afe88d5ff9dd44d70403525be5b/drm/emgd/include/psb_regs.h#L422"
quote = "#define PSB_CR_USE_CODE_BASE(i)                 (SGX_BASE + (0x0A0C + ((i) << 2)))"
terms = ["CR_USE_CODE_BASE_0"]
+++

Line 422 of `psb_regs.h` in Intel's EMGD register list (psb_regs.h) defines
`PSB_CR_USE_CODE_BASE(i)`. It backs the glossary register `CR_USE_CODE_BASE_0`: USSE code base 0:
address and data master.
