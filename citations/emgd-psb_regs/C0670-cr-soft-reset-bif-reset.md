+++
id = "C0670"
source = "emgd-psb_regs"
locator = "drm/emgd/include/psb_regs.h:103"
link = "https://github.com/EMGD-Community/intel-binaries-linux/blob/e6884ec2eaaf1afe88d5ff9dd44d70403525be5b/drm/emgd/include/psb_regs.h#L103"
quote = "#define _PSB_CS_RESET_BIF_RESET\t\t\t\t\t(1 << 0)"
terms = ["CR_SOFT_RESET.BIF_RESET"]
+++

Line 103 of `psb_regs.h` in Intel's EMGD register list (psb_regs.h) defines
`_PSB_CS_RESET_BIF_RESET`. It backs the glossary flag `CR_SOFT_RESET.BIF_RESET`: hold the BIF (MMU)
in reset.
