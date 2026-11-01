+++
id = "C0149"
source = "sgx545-ce"
locator = "src/services4/include/servicesint.h:171"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/servicesint.h#L171"
quote = "} PVRSRV_DEVICE_SYNC_OBJECT;"
terms = ["device_sync_object"]
+++

Line 171 of `servicesint.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`PVRSRV_DEVICE_SYNC_OBJECT`. It backs the glossary structure `device_sync_object`: pending values +
complete-counter addresses of one sync.
