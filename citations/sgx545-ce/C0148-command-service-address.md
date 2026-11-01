+++
id = "C0148"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:51"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L51"
quote = "IMG_UINT32\t\t\t\tui32ServiceAddress;"
terms = ["command.service_address"]
+++

Line 51 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32ServiceAddress`. It backs the glossary field `command.service_address`: EDM handler address
(aui32HostKickAddr[type]).
