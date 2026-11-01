+++
id = "E352"
claim = "srvinit asks SGX_GETMISCINFO once, for the driver's revision (eRequest 2), before its init connection; whether the answer is left as srvinit passed the struct, all zeros, a plausible one (DDK 1.7.17, build 862890, build options 0x60218) or one with every build option flipped, srvinit makes the same 57 bridge calls in the same order with the same sizes, returns 0, and its init info (2068 bytes) and all 15 buffers are byte-identical"
unit = "firmware"
method = "srvinit run under the harness without a GPU on the laptop as the build host (captures/firmware/miscinfo-replies.toml, fakedrm.c's MISC_REPLY knob), at the DDK's REV1 layout, once per answer and the plausible answer twice; the bridge log's calls (number, IN and OUT sizes), devinitpart2_in.bin and the alloc*.bin buffers compared across the five runs"
tiers = ["CAP"]
date = "2026-11-03"
data = ["firmware-miscinfo-replies"]
terms = []
+++

**What ran.** `fakedrm.c` answers the `SGX_GETMISCINFO` bridge call (97) through the struct whose
address srvinit passes. `MISC_REPLY` picks the answer to a `DRIVER_SGXREV` request (eRequest 2):
`untouched` leaves the struct as srvinit filled it (zeros up to dword 7, the `0xdead0001`
srvinit leaves in dword 8), `zero` writes 0 to dwords 2-8, `plausible` writes the DDK version
1.7.17, build 862890 and build options `0x60218` (the value srvinit names as its own, E011),
`mismatched` the same with the build options complemented (`0xfff9fde7`). The log line after each call shows the answer in
place.

**Results.** In all five runs srvinit connects once, enumerates and acquires the device, asks
`SGX_GETMISCINFO` with eRequest 2, then connects again for the init and makes the rest of its
calls: 57 bridge calls in all, the same numbers in the same order with the same IN and OUT sizes
(15 `ALLOC_DEVICEMEM`, 15 `MHANDLE_TO_MMAP_DATA` and 15 `RELEASE_MMAP_DATA` among them). Each
run returns 0 from `SrvInit`. The `SGX_DEVINITPART2` IN buffer (the init info, 2068 bytes) and
the 15 buffers srvinit leaves are byte-identical across the five runs. The logs differ only in
the process id and in user-space addresses, as two runs with the same answer also do.

**What it shows.** srvinit does not check the answer: it neither refuses mismatched build
options nor puts any of the answer's values into the init info or the buffers. A kernel that
runs srvinit may answer `DRIVER_SGXREV` with anything, zeros included, and gets the same boot
payload [CAP]. This covers the one request srvinit makes; it does not show what the closed
client libraries of the GLES stacks do with their own requests.
