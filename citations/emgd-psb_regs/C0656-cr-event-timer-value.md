+++
id = "C0656"
source = "emgd-psb_regs"
locator = "drm/emgd/include/psb_regs.h:533"
link = "https://github.com/EMGD-Community/intel-binaries-linux/blob/e6884ec2eaaf1afe88d5ff9dd44d70403525be5b/drm/emgd/include/psb_regs.h#L533"
quote = "#define _PSB_CE_TIMER_VALUE_MASK                (0xFFFFFF << 0)"
terms = ["CR_EVENT_TIMER.VALUE"]
+++

Line 533 of `psb_regs.h` in Intel's EMGD register list (psb_regs.h) defines
`_PSB_CE_TIMER_VALUE_MASK`. It backs the glossary bit field `CR_EVENT_TIMER.VALUE`: timer period
when written; read back, the count, which moves while the timer runs.
