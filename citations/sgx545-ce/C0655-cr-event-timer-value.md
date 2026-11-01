+++
id = "C0655"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:762"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L762"
quote = "#define EUR_CR_EVENT_TIMER_VALUE_MASK       0x00FFFFFFU"
terms = ["CR_EVENT_TIMER.VALUE"]
+++

Line 762 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_TIMER_VALUE`. It backs the glossary bit field `CR_EVENT_TIMER.VALUE`: timer period
when written; read back, the count, which moves while the timer runs.
