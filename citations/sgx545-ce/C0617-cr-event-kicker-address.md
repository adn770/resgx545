+++
id = "C0617"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:751"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L751"
quote = "#define EUR_CR_EVENT_KICKER_ADDRESS_MASK    0xFFFFFFF0U"
terms = ["CR_EVENT_KICKER.ADDRESS"]
+++

Line 751 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_KICKER_ADDRESS`. It backs the glossary bit field `CR_EVENT_KICKER.ADDRESS`: address
the event kicker reads (16-byte aligned).
