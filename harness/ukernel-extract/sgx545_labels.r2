f stub.insn0 @ 0x0
"CCu assert trap: sets host_ctl.assert_fail to 0xAD002600 and goes on at edm.lock_dpm_clear; no branch reaches it" @ 0x0
f edm.lock_dpm_clear @ 0xb9f8
f dpm.state_clear @ 0xba08
"CCu clears the DPM state (CR_DPM_TASK_STATE) and acknowledges its event in CR_EVENT_HOST_CLEAR" @ 0xba08
f hwperf.log @ 0xcbc8
"CCu HWPerf logger: appends one record to the HWPerf buffer (ta3d_ctl.hwperf_buffer_dev_vaddr), the record at 12 + 100 times the write offset" @ 0xcbc8
f edm.task.boot @ 0xd60
"CCu boot task, entered via PDS #10 (CR_EVENT_OTHER_PDS_EXEC from the init script)" @ 0xd60
f edm.task.pds11 @ 0xdf0
"CCu entered via PDS #11 (copies ta3d_ctl into the secondary attributes), which the boot task starts" @ 0xdf0
f edm.task.init_done @ 0xe20
"CCu PDS #12 task: installs PDS #13, programs CR_EVENT_TIMER and marks host_ctl.init_status complete" @ 0xe20
f edm.event.general @ 0x30
"CCu PDS #13 default target: every event outside the fast paths" @ 0x30
f edm.event.dpm_store @ 0x7050
"CCu PDS #13 target when only CR_EVENT_STATUS.DPM_INIT_END, DPM_CONTROL_STORE or DPM_STATE_STORE are pending" @ 0x7050
f edm.event.dpm_clear @ 0x2cd0
"CCu PDS #13 target when only CR_EVENT_STATUS.DPM_CONTROL_CLEAR is pending" @ 0x2cd0
f edm.event.csw_flush @ 0x5670
"CCu PDS #13 target when only CR_EVENT_STATUS.ISP2_ZLS_CSW_FINISHED, OTPM_INV or TPC_FLUSH are pending" @ 0x5670
f edm.work.dpm_store @ 0x73a0
f edm.work.dpm_clear @ 0x2ea0
f edm.work.csw_flush @ 0x5740
"CCu PDS #14 task for requests 0x4000f, which it clears from ta3d_ctl.requests; it shares the DPM store paths" @ 0x73a0
"CCu PDS #14 task: requests 0x120080" @ 0x2ea0
"CCu PDS #14 task: all other requests" @ 0x5740
f edm.request @ 0xbab0
"CCu posts deferred work: sets request bits in ta3d_ctl.requests and starts PDS #14 when a bit is new" @ 0xbab0
"CCu patched: emitpds control word for PDS #11 (data size 2)" @ 0xd60
"CCu patched: PDS #11 address >> 4" @ 0xd70
"CCu patched: ta3d_ctl device address" @ 0xd78
"CCu patched: emitpds control word for PDS #12 (data size 1)" @ 0xdb0
"CCu patched: PDS #12 address >> 4" @ 0xdc0
"CCu patched: PDS #13 address -> CR_EVENT_OTHER_PDS_EXEC" @ 0xe40
"CCu patched: PDS #13 data size (6) -> CR_EVENT_OTHER_PDS_DATA" @ 0xe50
"CCu patched: emitpds control word for PDS #14 (data size 3)" @ 0xbaf8
"CCu patched: PDS #14 address >> 4" @ 0xbb10
f edm.ccb.fetch @ 0x4c0
"CCu kick event: reads the kernel_ccb command at ccb_ctl.read_offset (32 bytes a command; the kernel CCB is at ta3d_ctl.kernel_ccb_dev_vaddr) and hands its service address, cache control and six data words to the handler" @ 0x4c0
"CCu the command's cache control: bits 0 and 1 invalidate the BIF page tables and directory (0x158a), bit 3 the data cache (CR_CACHE_CTRL)" @ 0x518
"CCu advances ccb_ctl.read_offset by one, modulo 256, then the command's handler runs" @ 0x5f8
"CCu CLEANUP: the cleanup type (RT 1 to PB 5) marks a pending cleanup; the address of the structure to clean up is kept in ta3d_ctl dword 32" @ 0x9d0
"CCu CMD.SET_HWPERF_STATUS: bit 0 of the status resets the HWPerf buffer; the EDM keeps the other bits as its HWPerf status" @ 0xab8
f edm.schedule @ 0xb08
"CCu scheduler: posts request 0x40000 when 3D or transfer work is queued and 0x20000 when TA work is queued" @ 0xb08
"CCu request 0x80, CR_EVENT_STATUS.TA_FINISHED: acknowledged with 0x2000 in CR_EVENT_HOST_CLEAR, handled by edm.ta.finished" @ 0x2f48
"CCu request 0x20000 (TA work queued): edm.ta.pick" @ 0x2f80
f edm.ta.finished @ 0x3030
"CCu TA finished; bits 9 and 10 of the TA state word select the partial-render paths" @ 0x3030
f edm.ta.finished.normal @ 0x3218
"CCu TA done: the TA is idle, the command's ready flag is cleared, the TA transfer-queue sync and the TA status pairs complete, hw_pb_desc.allocated_page_count takes CR_DPM_PAGE_STATUS and CR_EVENT_STATUS.SW_EVENT is raised; with GEOM_FLAGS.LAST_KICK the scene goes to the render" @ 0x3218
"CCu last kick: free the scene with FRAG_FLAGS.NO_RENDER, then queue the render details for the 3D" @ 0x3538
f edm.ta.pick @ 0x37a8
"CCu picks the next TA job from the TA queue by hw_render_context.submitted_commands, CONTEXT_FLAGS.SUSPEND, the command's ready flag, the TA transfer-queue sync, the TA to 3D dependency, the destination and source syncs and a free hw_rt_data.state" @ 0x37a8
f edm.ta.cmd_to_rd @ 0x3d88
"CCu copy cmd_ta words into hw_render_details: frag_flags, the TA to 3D dependency, frame_num, the 3D transfer-queue sync, the destination and source syncs, the depth and stencil RT strides, pds_bgnd, the 3D status pairs; cmd_ta.patches_3d are memory writes (address, value), not register writes" @ 0x3d88
f edm.ta.ccb_advance @ 0x3fe0
"CCu advances the TA CCB read offset by cmd_ta.size, modulo 0x10000, and counts the command off hw_render_context.submitted_commands" @ 0x3fe0
f edm.ta.abort @ 0x4060
"CCu hw_rt_data.state aborted or FRAG_FLAGS.ABORT: complete the TA command without running it" @ 0x4060
f edm.ta.kick @ 0x4748
"CCu TA kick: the BIF, PB, DPM and TA registers from cmd_ta, then CR_VDM_START" @ 0x4748
"CCu GEOM_FLAGS.FIRST_KICK: resets the TA (CR_SOFT_RESET.TA_RESET)" @ 0x48e8
"CCu cmd_ta.ta_registers, dwords 142-169, go to 28 registers in structure order (TE, VDM, MTE, PPP, USE, CR_BIF_TA_REQ_BASE, TA, DPM and others)" @ 0x4ad0
"CCu GEOM_FLAGS.FIRST_KICK or GEOM_FLAGS.NO_DPM_CONTEXT_LOAD: bind the DPM state and control tables, clear the DPM state per RT, clear the OTPM" @ 0x5070
"CCu CR_VDM_START: the TA runs" @ 0x5660
f edm.ta.oom @ 0x5a80
"CCu DPM out of memory: grow the global list or abort the macrotile and start a partial render" @ 0x5a80
f edm.ta.terminated @ 0x6118
"CCu CR_EVENT_STATUS.TA_TERMINATE after an out-of-memory abort: partial (SPM) render" @ 0x6118
"CCu partial render: CR_ISP_START_RENDER" @ 0x6d98
f edm.spm.resume @ 0x6df8
"CCu after a partial render: resume the TA (CR_DPM_OUTOFMEM) and mark the RT status for depth reload" @ 0x6df8
f edm.3d.mem_free @ 0x75a0
"CCu CR_EVENT_STATUS.DPM_3D_MEM_FREE: the 3D's memory is free; the render completes if the PBE has finished" @ 0x75a0
f edm.3d.end_render @ 0x75d8
"CCu CR_EVENT_STATUS.PIXELBE_END_RENDER: a transfer completes, or the PBE is marked finished and the render completes when no deallocation is pending" @ 0x75d8
f edm.isp.vistest @ 0x7668
"CCu ISP breakpoint: accumulate visibility-test results" @ 0x7668
f edm.3d.syncs_done @ 0x7a28
"CCu render done for one RT: its destination sync completes and its RT status word gets bit 0; on the last RT also the TA to 3D dependency, the 3D transfer-queue and source syncs and hw_render_details.status_3d" @ 0x7a28
f edm.3d.scene_done @ 0x7ce8
"CCu last RT: hw_rt_data.state becomes 0x10 (free); the RT data's render details (hw_rt_data.hw_render_details_dev_vaddr), access word and DPM slot are released; CR_EVENT_STATUS.SW_EVENT" @ 0x7ce8
f edm.3d.complete @ 0x7e88
"CCu 3D completion: a partial render posts request 0x80000; otherwise the syncs complete, the render leaves the queue and the 3D is rescheduled" @ 0x7e88
f edm.3d.schedule @ 0x81a8
"CCu 3D pipe scheduler: transfer queue first, then the 3D render queue" @ 0x81a8
f edm.3d.pick @ 0x82e8
"CCu picks the next render from the 3D queue: the ready render details of a context whose destination, transfer-queue and source syncs are complete" @ 0x82e8
f edm.3d.kick @ 0x8958
"CCu 3D kick: the DPM context, the 3D PB, hw_render_details.registers_3d, the background object, then CR_ISP_START_RENDER" @ 0x8958
"CCu hw_render_details.registers_3d, dwords 0-51, go to 52 registers in structure order (BIF_3D, ISP, ZLS, EVENT_PIXEL_PDS, USE filter, TPU and others)" @ 0x8df8
"CCu the background object (hw_rt_data.bgobj_dev_vaddr dwords 0-2, in the 3D address space) holds hw_render_details.pds_bgnd words 0-1 and the RT index's word of hw_render_details.pds_bgnd_list_dev_vaddr" @ 0x9468
"CCu CR_ISP_START_RENDER: the 3D render runs" @ 0x96d0
f edm.transfer.pick @ 0x96e0
f edm.transfer.complete @ 0xa308
f edm.pipe.resume @ 0xad68
"CCu resume: ends one pause (ta3d_ctl.settle_count); the last one clears bits 3:0 of CR_DMS_CTRL" @ 0xad68
f edm.pipe.pause @ 0xade0
"CCu pause: quiesces a busy 3D or TA pipe and counts the pause in ta3d_ctl.settle_count" @ 0xade0
f edm.post_ta @ 0xac90
"CCu posts request 0x20000 (edm.request) when the TA queue is not empty" @ 0xac90
f edm.post_3d @ 0xacf0
"CCu posts request 0x40000 (edm.request) when the transfer or the 3D queue is not empty" @ 0xacf0
f pb.ta_thresholds @ 0xb328
"CCu loads the hw_pb_desc thresholds (TA, ZLS, global, PDS) into the DPM and clears PB_FLAGS.INIT_PAGE_TABLE and PB_FLAGS.THRESHOLD_UPDATE" @ 0xb328
f pb.ta_reload @ 0xb3b0
"CCu reloads the TA free list from its status registers (CR_DPM_TASK_TA_FREE)" @ 0xb3b0
f pb.ta_store @ 0xb468
"CCu TA free-list status -> hw_pb_desc.current_stack_top, dpm_ta_alloc, local_page_count, global_page_count" @ 0xb468
f pb.ta_load @ 0xb510
"CCu hw_pb_desc -> the DPM TA page table base, free list and thresholds (CR_DPM_TASK_TA_FREE)" @ 0xb510
f pb.3d_store @ 0xb6a0
"CCu 3D free-list status -> hw_pb_desc.current_stack_top, dpm_ta_alloc, local_page_count, global_page_count" @ 0xb6a0
f pb.3d_load @ 0xb748
"CCu hw_pb_desc -> the DPM 3D page table base and free list (CR_DPM_TASK_3D_FREE)" @ 0xb748
f pb.init_page_table @ 0xb868
"CCu PB_FLAGS.INIT_PAGE_TABLE: reset the free list from the initial words and link the page table from the pb_block list" @ 0xb868
f dpm.state_store @ 0xba40
"CCu stores the DPM state (CR_DPM_TASK_STATE, CR_EVENT_STATUS.DPM_STATE_STORE)" @ 0xba40
f dpm.state_load @ 0xba78
"CCu loads the DPM state (CR_DPM_TASK_STATE)" @ 0xba78
f dpm.ta_alloc_pause @ 0xbb28
f dpm.ta_alloc_resume @ 0xbb98
f dpm.ctx_store @ 0xbbc0
"CCu stores an RT data's DPM state, control, OTPM and tail pointers for its DPM slot" @ 0xbbc0
f dpm.ctx_load @ 0xbdf0
"CCu loads an RT data's DPM state, control and OTPM" @ 0xbdf0
f bif.map_context @ 0xbf60
"CCu finds or assigns a BIF directory list for the context's page-directory address, for the TA or the 3D; CONTEXT_FLAGS.NEW invalidates the caches" @ 0xbf60
f bif.set_index @ 0xc260
"CCu sets the TA's or the 3D's directory list index in CR_BIF_BANK0 (CR_BIF_BANK0.INDEX_3D for the 3D)" @ 0xc260
f edm.power.done @ 0xc2c0
"CCu power request done; when the EDM is idle the power-management sample count restarts from host_ctl.active_powman_sample_rate" @ 0xc2c0
f bif.edm_index @ 0xc320
"CCu points the EDM's directory list index in CR_BIF_BANK0 at the TA's list, the 3D's or its own list 15" @ 0xc320
f dpm.free_scene @ 0xc3e0
"CCu frees a scene's parameter memory without rendering (CR_DPM_FREE_CONTEXT) and clears the TPC" @ 0xc3e0
f edm.3d.queue_render @ 0xca10
"CCu moves the render details from the context's pending list to its ready list and queues the context on the 3D queue" @ 0xca10
f edm.task.end @ 0xcba0
"CCu flush caches and end the task" @ 0xcba0
