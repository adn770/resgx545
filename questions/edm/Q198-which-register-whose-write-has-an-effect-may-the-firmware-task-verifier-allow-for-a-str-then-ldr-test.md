+++
id = "Q198"
question = "after E604 (0x0814 and 0x0a78 read back what a firmware task stored while a client fill was started), does the user want the firmware-task verifier's str allow list widened to a register whose write has an effect, or to a wider value, for a str-then-ldr test while a job runs, and which"
unit = "edm"
kind = "fw"
phase = 11
evidence = ["E534", "E604"]
terms = []
+++
This is a decision for the user, not a question for the hardware. The str allow list (regs.toml;
the ldr list also holds CORE_ID, CORE_REVISION and CR_TIMER) holds only 0x0814 and 0x0a78, both
plain storage (E026, E534), and E604 shows they read back across the start of a fill. Every
register whose write does something (0x0abc: bits 4:1 clear hang the next job, E026) and every
clock-gate register is refused by the verifier and not part of any run. A test of "a write
during a job reaches the hardware at once" needs a register with an effect.

To settle it: the user names a register and a value (and says a hang or watchdog is acceptable),
or declines. Until then the str allow list stays as it is.
