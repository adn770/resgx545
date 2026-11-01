+++
id = "C0748"
source = "sgx545-ce"
locator = "src/services4/include/sgxinfo.h:337"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgxinfo.h#L337"
quote = "} SGX_CCB_KICK;"
terms = ["ccb_kick"]
+++

Line 337 of `sgxinfo.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares `SGX_CCB_KICK`.
It backs the glossary structure `ccb_kick`: bridge payload of SGX_DOKICK (kernel-side kick of a
CMDTA).
