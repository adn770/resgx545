+++
id = "C0068"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:454"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L454"
quote = "#define EUR_CR_EVENT_HOST_ENABLE            0x0130"
terms = ["CR_EVENT_HOST_ENABLE"]
+++

Line 454 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_ENABLE`. It backs the glossary register `CR_EVENT_HOST_ENABLE`: events routed to
the host interrupt, bank 1.
