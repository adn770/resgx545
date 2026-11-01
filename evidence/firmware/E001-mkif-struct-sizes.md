+++
id = "E001"
claim = "srvinit passes the kernel 13 MKIF structure sizes, among them CMDTA 0x2b0, TRANSFERCMD 0x4c8, HWRENDERDETAILS 0x1ec, HWTRANSFERCONTEXT 0xb4 and HOST_CTL 0x44"
unit = "firmware"
method = "the closed srvinit run to completion under the extraction harness at the two layouts layout_base and layout_moved of the capture table firmware/layout; its boot payload decoded with harness/ukernel-extract/initinfo.py"
tiers = ["CAP"]
date = "2026-10-30"
data = ["firmware-layout"]
terms = ["misc_info_struct_sizes.sizeof_cmd_ta", "misc_info_struct_sizes.sizeof_cmd_ta_shared", "misc_info_struct_sizes.sizeof_transfer_cmd", "misc_info_struct_sizes.sizeof_transfer_cmd_shared", "misc_info_struct_sizes.sizeof_3d_registers", "misc_info_struct_sizes.sizeof_hw_pb_desc", "misc_info_struct_sizes.sizeof_hw_render_context", "misc_info_struct_sizes.sizeof_hw_render_details", "misc_info_struct_sizes.sizeof_hw_rt_data", "misc_info_struct_sizes.sizeof_hw_rt_data_set", "misc_info_struct_sizes.sizeof_hw_transfer_context", "misc_info_struct_sizes.sizeof_host_ctl", "misc_info_struct_sizes.sizeof_command"]
+++

The boot payload `srvinit` hands the kernel (`devinitpart2_in.bin` of each layout capture),
decoded with `harness/ukernel-extract/initinfo.py`, carries 13 structure sizes. Both layouts
give the same sizes:

`CMDTA 0x2b0`, `CMDTA_SHARED 0x1e0`, `TRANSFERCMD 0x4c8`, `TRANSFERCMD_SHARED 0xdc`, `3DREGISTERS
0xd0`, `HWPBDESC 0x3c`, `HWRENDERCONTEXT 0x44`, `HWRENDERDETAILS 0x1ec`, `HWRTDATA 0x38`,
`HWRTDATASET 0x50`, `HWTRANSFERCONTEXT 0xb4`, `HOST_CTL 0x44`, `COMMAND 0x20`.

These sizes are the interface a driver must meet, as srvinit states it: a host-side
implementation lays these structures out to exactly these sizes. The sizes say nothing about the
fields inside. The field names come from the GPL `sgxinfo.h`; this record does not test the
firmware's own use of the sizes.
