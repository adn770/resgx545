+++
id = "C0136"
source = "emgd-psb_regs"
locator = "drm/emgd/include/psb_regs.h:634"
link = "https://github.com/EMGD-Community/intel-binaries-linux/blob/e6884ec2eaaf1afe88d5ff9dd44d70403525be5b/drm/emgd/include/psb_regs.h#L634"
quote = "#define PSB_CR_BIF_DIR_LIST_BASE1               (SGX_BASE + 0x0C38)"
terms = ["CR_BIF_DIR_LIST_BASE1"]
+++

Line 634 of `psb_regs.h` in Intel's EMGD register list (psb_regs.h) defines
`PSB_CR_BIF_DIR_LIST_BASE1`. It backs the glossary register `CR_BIF_DIR_LIST_BASE1`: page-directory
base, list 1: the first kick of a VM after a reset writes the render context's page directory there
(the HW context's PD word, 3 of 3 jobs); the TA and 3D requestors translate through it during a
render.
