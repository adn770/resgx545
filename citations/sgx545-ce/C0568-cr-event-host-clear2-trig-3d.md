+++
id = "C0568"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:302"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L302"
quote = "#define EUR_CR_EVENT_HOST_CLEAR2_TRIG_3D_MASK 0x00000040U"
terms = ["CR_EVENT_HOST_CLEAR2.TRIG_3D"]
+++

Line 302 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_CLEAR2_TRIG_3D`. It backs the glossary bit field `CR_EVENT_HOST_CLEAR2.TRIG_3D`:
clear: 3D trigger.
