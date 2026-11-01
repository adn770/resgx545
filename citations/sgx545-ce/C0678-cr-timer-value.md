+++
id = "C0678"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:631"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L631"
quote = "#define EUR_CR_TIMER_VALUE_MASK             0xFFFFFFFFU"
terms = ["CR_TIMER.VALUE"]
+++

Line 631 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_TIMER_VALUE`. It backs the glossary bit field `CR_TIMER.VALUE`: current timer count.
