+++
id = "C0012"
source = "emgd-psb_regs"
locator = "drm/emgd/include/psb_regs.h:424"
link = "https://github.com/EMGD-Community/intel-binaries-linux/blob/e6884ec2eaaf1afe88d5ff9dd44d70403525be5b/drm/emgd/include/psb_regs.h#L424"
quote = "#define _PSB_CUC_BASE_DM_MASK                   (0x3 << 25)"
terms = ["CR_USE_CODE_BASE_0.DM"]
+++

Line 424 of `psb_regs.h` in Intel's EMGD register list (psb_regs.h) defines `_PSB_CUC_BASE_DM_MASK`.
It backs the glossary bit field `CR_USE_CODE_BASE_0.DM`: data master using this base (vertex, pixel,
reserved, event).
