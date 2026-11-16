// SPDX-License-Identifier: MIT
/*
 * The library's ioctl wrappers against the in-process mock: discovery, the
 * DEV_QUERY size rules, BOs, VM mappings, contexts, syncobjs and the
 * SUBMIT_JOBS validation rules (reserved bits, the reserved update list, the
 * array strides, the per-file limits). The mock follows the kernel's rules as
 * include/uapi/sgxfive_drm.h states them, so these cases are the rules.
 */
#include <errno.h>
#include <stddef.h>
#include <string.h>

#include "sgxfive.h"
#include "sgxfive_mock.h"
#include "tap.h"

static struct sgxfive_mock *mock;

static struct sgxfive_dev *open_dev(const struct sgxfive_mock_config *cfg)
{
	struct sgxfive_dev *dev = NULL;

	if (mock)
		sgxfive_mock_destroy(mock);
	mock = sgxfive_mock_create(cfg);
	CHECK_EQ(sgxfive_dev_open(sgxfive_mock_backend(mock), NULL, &dev), 0);
	return dev;
}

static void discovery(void)
{
	const struct sgxfive_mock_config other = { .other_driver = "i915" };
	const struct sgxfive_mock_config none = { .no_sgxfive = true };
	struct sgxfive_dev *dev = open_dev(&other);

	CHECK(dev && !strcmp(sgxfive_dev_path(dev), "/dev/dri/renderD129"));
	sgxfive_dev_close(dev);

	sgxfive_mock_destroy(mock);
	mock = sgxfive_mock_create(&none);
	dev = (struct sgxfive_dev *)1;
	CHECK_EQ(sgxfive_dev_open(sgxfive_mock_backend(mock), NULL, &dev), -ENODEV);
	CHECK(dev == NULL);
	CHECK_EQ(sgxfive_dev_open(sgxfive_mock_backend(mock), "/dev/dri/renderD128", &dev),
		 -ENOENT);

	/*
	 * Hosted by gma500, the node reports driver name
	 * "gma500". A gma500 node that answers DEV_QUERY is ours; a plain one
	 * (Poulsbo, or Cedarview without sgxfive) is skipped.
	 */
	sgxfive_mock_destroy(mock);
	mock = sgxfive_mock_create(&(struct sgxfive_mock_config){
		.other_driver = "gma500", .sgxfive_name = "gma500" });
	dev = NULL;
	CHECK_EQ(sgxfive_dev_open(sgxfive_mock_backend(mock), NULL, &dev), 0);
	CHECK(dev && !strcmp(sgxfive_dev_path(dev), "/dev/dri/renderD129"));
	sgxfive_dev_close(dev);
	CHECK_EQ(sgxfive_dev_open(sgxfive_mock_backend(mock), "/dev/dri/renderD128", &dev),
		 -ENODEV);
}

/* An fd the caller opened (IGT's drm_open_driver) is used as is and stays open. */
static void adopt(void)
{
	struct sgxfive_dev *dev = NULL;
	const struct sgxfive_backend *be;
	struct drm_sgxfive_dev_query_gpu_info gpu;
	uint32_t size = sizeof(gpu);
	int fd;

	sgxfive_mock_destroy(mock);
	mock = sgxfive_mock_create(&(struct sgxfive_mock_config){ 0 });
	be = sgxfive_mock_backend(mock);
	fd = be->open(be->priv, "/dev/dri/renderD128");
	CHECK(fd >= 0);
	CHECK_EQ(sgxfive_dev_adopt(be, fd, &dev), 0);
	CHECK_EQ(sgxfive_dev_info(dev)->gpu.core_id, 0x01150000);
	sgxfive_dev_close(dev);
	struct drm_sgxfive_dev_query_args q = {
		.type = DRM_SGXFIVE_DEV_QUERY_GPU_INFO, .size = size,
		.pointer = (uintptr_t)&gpu,
	};
	CHECK_EQ(be->ioctl(be->priv, fd, DRM_IOCTL_SGXFIVE_DEV_QUERY, &q), 0);
	CHECK_EQ(be->close(be->priv, fd), 0);
	/* A node without sgxfive is refused, and its fd too stays the caller's. */
	sgxfive_mock_destroy(mock);
	mock = sgxfive_mock_create(&(struct sgxfive_mock_config){ .no_sgxfive = true,
		.other_driver = "i915" });
	be = sgxfive_mock_backend(mock);
	fd = be->open(be->priv, "/dev/dri/renderD128");
	dev = (struct sgxfive_dev *)1;
	CHECK_EQ(sgxfive_dev_adopt(be, fd, &dev), -ENODEV);
	CHECK(dev == NULL);
	CHECK_EQ(be->close(be->priv, fd), 0);
}

/*
 * The REV1 heap table, as the kernel reports it: the shader heaps are their
 * code-base windows (ten and four of 512 KiB), the kernel heaps reserved.
 */
static void rev1_heaps(const struct sgxfive_info *info)
{
	static const struct { uint64_t base, size; uint32_t flags; } want[] = {
		[DRM_SGXFIVE_HEAP_GENERAL] = { 0x3e000000, 0xb2000000 - 0x1000, 0 },
		[DRM_SGXFIVE_HEAP_TEXTURE] = { 0xf0000000, 0x10000000 - 0x1000, 0 },
		[DRM_SGXFIVE_HEAP_PDS_PIXEL] = { 0x2e000000, 0x02000000 - 0x1000, 0 },
		[DRM_SGXFIVE_HEAP_PDS_VERTEX] = { 0x30400000, 0x01c00000 - 0x1000, 0 },
		[DRM_SGXFIVE_HEAP_USSE_PIXEL] = { 0x37000000, 10 * 0x80000,
						  DRM_SGXFIVE_HEAP_FIXED_WINDOWS },
		[DRM_SGXFIVE_HEAP_USSE_VERTEX] = { 0x3c000000, 4 * 0x80000,
						   DRM_SGXFIVE_HEAP_FIXED_WINDOWS },
		[DRM_SGXFIVE_HEAP_KERNEL_CODE] = { 0x30000000, 0x00080000 - 0x1000,
						   DRM_SGXFIVE_HEAP_RESERVED },
		[DRM_SGXFIVE_HEAP_KERNEL_DATA] = { 0x32000000, 0x05000000 - 0x1000,
						   DRM_SGXFIVE_HEAP_RESERVED },
		[DRM_SGXFIVE_HEAP_PARAMETERS] = { 0x10000000, 0x10000000,
						  DRM_SGXFIVE_HEAP_RESERVED },
		[DRM_SGXFIVE_HEAP_TA_DATA] = { 0x20000000, 0x0d000000, DRM_SGXFIVE_HEAP_RESERVED },
	};

	for (uint32_t i = 0; i < DRM_SGXFIVE_HEAP_COUNT; i++) {
		const struct drm_sgxfive_heap *h = &info->heaps[i];
		int bad = !CHECK_EQ(h->base, want[i].base);

		bad += !CHECK_EQ(h->size, want[i].size);
		bad += !CHECK_EQ(h->flags, want[i].flags);
		bad += !CHECK_EQ(h->page_size_log2, 12);
		if (bad)
			printf("#   heap %u\n", i);
	}
}

/*
 * HEAP_INFO's array: each heap cut to a shorter stride or zero-filled up to a
 * longer one; a stride of 0 or above DRM_SGXFIVE_OBJ_ARRAY_MAX_STRIDE is -EINVAL.
 */
static void heap_strides(struct sgxfive_dev *dev)
{
	const uint32_t sz = sizeof(struct drm_sgxfive_heap);
	uint8_t buf[2 * DRM_SGXFIVE_OBJ_ARRAY_MAX_STRIDE + 8];
	struct drm_sgxfive_dev_query_heap_info h;
	uint32_t size = sizeof(h);
	const uint8_t *e;

	memset(buf, 0xa5, sizeof(buf));
	h = (struct drm_sgxfive_dev_query_heap_info){ { 8, 2, (uintptr_t)buf } };
	CHECK_EQ(sgxfive_dev_query(dev, DRM_SGXFIVE_DEV_QUERY_HEAP_INFO, &h, &size), 0);
	CHECK_EQ(h.heaps.count, 2);
	CHECK(!memcmp(buf, &sgxfive_dev_info(dev)->heaps[0], 8));
	CHECK(!memcmp(buf + 8, &sgxfive_dev_info(dev)->heaps[1], 8));
	CHECK_EQ(buf[16], 0xa5);

	memset(buf, 0xa5, sizeof(buf));
	h = (struct drm_sgxfive_dev_query_heap_info){
		{ DRM_SGXFIVE_OBJ_ARRAY_MAX_STRIDE, 2, (uintptr_t)buf } };
	CHECK_EQ(sgxfive_dev_query(dev, DRM_SGXFIVE_DEV_QUERY_HEAP_INFO, &h, &size), 0);
	e = buf + DRM_SGXFIVE_OBJ_ARRAY_MAX_STRIDE;
	CHECK(!memcmp(e, &sgxfive_dev_info(dev)->heaps[1], sz));
	CHECK_EQ(e[sz] | e[DRM_SGXFIVE_OBJ_ARRAY_MAX_STRIDE - 1], 0);
	CHECK_EQ(e[DRM_SGXFIVE_OBJ_ARRAY_MAX_STRIDE], 0xa5);

	h = (struct drm_sgxfive_dev_query_heap_info){
		{ DRM_SGXFIVE_OBJ_ARRAY_MAX_STRIDE + 1, 1, (uintptr_t)buf } };
	CHECK_EQ(sgxfive_dev_query(dev, DRM_SGXFIVE_DEV_QUERY_HEAP_INFO, &h, &size), -EINVAL);
	h = (struct drm_sgxfive_dev_query_heap_info){ { 0, 1, (uintptr_t)buf } };
	CHECK_EQ(sgxfive_dev_query(dev, DRM_SGXFIVE_DEV_QUERY_HEAP_INFO, &h, &size), -EINVAL);
}

static void query(void)
{
	struct sgxfive_dev *dev = open_dev(&(struct sgxfive_mock_config){ 0 });
	const struct sgxfive_info *info = sgxfive_dev_info(dev);
	struct drm_sgxfive_dev_query_gpu_info gpu;
	uint32_t size;

	CHECK_EQ(info->gpu.core_id, 0x01150000);
	CHECK_EQ(info->gpu.quirks, DRM_SGXFIVE_QUIRK_SAMPLE_CACHE);
	CHECK_EQ(info->gpu.host_bridge_rev, 3);
	CHECK_EQ(info->fw.ddk_build, 862890);
	CHECK_EQ(info->job.job_types,
		 DRM_SGXFIVE_JOB_TYPE_TRANSFER_BIT | DRM_SGXFIVE_JOB_TYPE_RENDER_BIT);
	CHECK_EQ(info->job.render_cmd_size, 0x68);
	CHECK_EQ(info->job.transfer_cmd_size, 0xa8);
	CHECK_EQ(info->job.max_updates, 0);
	CHECK_EQ(info->runtime.num_pixel_partitions, 31);
	CHECK_EQ(info->num_heaps, DRM_SGXFIVE_HEAP_COUNT);
	CHECK_EQ(info->heaps[DRM_SGXFIVE_HEAP_GENERAL].base, 0x3e000000);
	CHECK_EQ(info->heaps[DRM_SGXFIVE_HEAP_TEXTURE].base, 0xf0000000);
	CHECK_EQ(info->heaps[DRM_SGXFIVE_HEAP_PDS_PIXEL].base, 0x2e000000);
	CHECK_EQ(info->heaps[DRM_SGXFIVE_HEAP_USSE_PIXEL].base, 0x37000000);
	CHECK_EQ(info->heaps[DRM_SGXFIVE_HEAP_KERNEL_CODE].flags, DRM_SGXFIVE_HEAP_RESERVED);
	CHECK_EQ(info->heaps[DRM_SGXFIVE_HEAP_KERNEL_DATA].base, 0x32000000);
	CHECK(sgxfive_heap(dev, DRM_SGXFIVE_HEAP_GENERAL) != NULL);
	CHECK(sgxfive_heap(dev, DRM_SGXFIVE_HEAP_COUNT) == NULL);
	rev1_heaps(info);

	/* NULL pointer: size only. Short buffer: truncated copy. Unknown type: -EINVAL. */
	size = 0;
	CHECK_EQ(sgxfive_dev_query(dev, DRM_SGXFIVE_DEV_QUERY_GPU_INFO, NULL, &size), 0);
	CHECK_EQ(size, sizeof(gpu));
	memset(&gpu, 0xa5, sizeof(gpu));
	size = 8;
	CHECK_EQ(sgxfive_dev_query(dev, DRM_SGXFIVE_DEV_QUERY_GPU_INFO, &gpu, &size), 0);
	CHECK_EQ(size, 8);
	CHECK_EQ(gpu.core_revision, 0x0001000d);
	CHECK_EQ(gpu.core_id_sw, 0xa5a5a5a5);
	size = sizeof(gpu);
	CHECK_EQ(sgxfive_dev_query(dev, 99, &gpu, &size), -EINVAL);
	heap_strides(dev);
	sgxfive_dev_close(dev);

	dev = open_dev(&(struct sgxfive_mock_config){ .layout = SGXFIVE_MOCK_LAYOUT_HARNESS });
	info = sgxfive_dev_info(dev);
	CHECK_EQ(info->gpu.quirks, 0);
	CHECK_EQ(info->heaps[DRM_SGXFIVE_HEAP_TEXTURE].size, 0);
	CHECK(sgxfive_heap(dev, DRM_SGXFIVE_HEAP_TEXTURE) == NULL);
	CHECK_EQ(info->heaps[DRM_SGXFIVE_HEAP_PDS_PIXEL].base, 0xe4000000);
	CHECK_EQ(info->heaps[DRM_SGXFIVE_HEAP_USSE_PIXEL].base, 0xf4000000);
	sgxfive_dev_close(dev);
}

static void bos(void)
{
	struct sgxfive_dev *dev = open_dev(&(struct sgxfive_mock_config){ 0 });
	struct drm_sgxfive_create_bo_args args = { .size = 4096, ._padding_c = 1 };
	struct sgxfive_bo *bo = NULL, *priv = NULL;
	struct sgxfive_mock_stats st;
	uint32_t *p = NULL;

	CHECK_EQ(sgxfive_bo_create(dev, 5000, DRM_SGXFIVE_BO_ALLOW_CPU_ACCESS, &bo), 0);
	CHECK_EQ(bo->size, 8192);
	CHECK_EQ(sgxfive_bo_mmap(bo, (void **)&p), 0);
	p[2047] = 0x12345678;
	CHECK_EQ(((uint32_t *)bo->map)[2047], 0x12345678);
	CHECK_EQ(sgxfive_bo_create(dev, 0, 0, &priv), -EINVAL);
	CHECK_EQ(sgxfive_bo_create(dev, (1ull << 30) + 4096, 0, &priv), -EINVAL);
	CHECK_EQ(sgxfive_bo_create(dev, 4096, DRM_SGXFIVE_BO_CPU_CACHED, &priv), -EINVAL);
	CHECK_EQ(sgxfive_bo_create(dev, 4096, 1ULL << 40, &priv), -EINVAL);
	CHECK_EQ(sgxfive_dev_ioctl(dev, DRM_IOCTL_SGXFIVE_CREATE_BO, &args), -EINVAL);
	CHECK_EQ(sgxfive_bo_create(dev, 4096, 0, &priv), 0);
	CHECK_EQ(sgxfive_bo_mmap(priv, (void **)&p), -EINVAL);	/* no CPU access */
	sgxfive_mock_get_stats(mock, &st);
	CHECK_EQ(st.bos, 2);
	sgxfive_bo_destroy(priv);
	sgxfive_bo_destroy(bo);
	sgxfive_mock_get_stats(mock, &st);
	CHECK_EQ(st.bos, 0);
	sgxfive_dev_close(dev);
}

static void vms(void)
{
	struct sgxfive_dev *dev = open_dev(&(struct sgxfive_mock_config){ 0 });
	const struct sgxfive_info *info = sgxfive_dev_info(dev);
	const uint64_t kcode = info->heaps[DRM_SGXFIVE_HEAP_KERNEL_CODE].base;
	const struct drm_sgxfive_heap *usse = sgxfive_heap(dev, DRM_SGXFIVE_HEAP_USSE_PIXEL);
	struct sgxfive_vm *vm = NULL;
	struct sgxfive_bo *bo = NULL;
	struct sgxfive_mock_stats st;
	uint64_t a = 0, b = 0;
	uint32_t ctx = 0;

	CHECK_EQ(sgxfive_vm_create(dev, &vm), 0);
	CHECK_EQ(sgxfive_bo_create(dev, 3 * 4096, 0, &bo), 0);
	CHECK_EQ(sgxfive_vm_alloc(vm, DRM_SGXFIVE_HEAP_GENERAL, 8192, 4096, &a), 0);
	CHECK_EQ(a, 0x3e000000);
	CHECK_EQ(sgxfive_vm_alloc(vm, DRM_SGXFIVE_HEAP_GENERAL, 4096, 0x10000, &b), 0);
	CHECK_EQ(b, 0x3e010000);
	CHECK_EQ(sgxfive_vm_alloc(vm, DRM_SGXFIVE_HEAP_KERNEL_CODE, 4096, 4096, &b), -EINVAL);
	CHECK_EQ(sgxfive_vm_alloc(vm, DRM_SGXFIVE_HEAP_GENERAL, 100, 4096, &b), -EINVAL);

	CHECK_EQ(sgxfive_vm_map(vm, a, bo, 0, 8192, 0), 0);
	CHECK_EQ(sgxfive_vm_map(vm, a + 4096, bo, 0, 4096, 0), -EEXIST);
	CHECK_EQ(sgxfive_vm_map(vm, a + 8192, bo, 4096, 4096, DRM_SGXFIVE_VM_MAP_READ_ONLY), 0);
	CHECK_EQ(sgxfive_vm_map(vm, kcode, bo, 0, 4096, 0), -EINVAL);
	CHECK_EQ(sgxfive_vm_map(vm, a + 0x100000 + 8, bo, 0, 4096, 0), -EINVAL);
	CHECK_EQ(sgxfive_vm_map(vm, a + 0x100000, bo, 0, 4 * 4096, 0), -EINVAL); /* > BO */
	CHECK_EQ(sgxfive_vm_map(vm, a + 0x100000, bo, 0, 4096, 1u << 5), -EINVAL);
	CHECK_EQ(sgxfive_vm_map(vm, usse->base + usse->size - 4096, bo, 0, 8192, 0), -EINVAL);
	CHECK_EQ(sgxfive_vm_map(vm, 0x100000000ULL, bo, 0, 4096, 0), -EINVAL);
	CHECK_EQ(sgxfive_vm_map(vm, 0x2e000000 + 0x02000000 - 0x1000, bo, 0, 4096, 0), -EINVAL);
	CHECK_EQ(sgxfive_vm_map(vm, 0x30400000 + 0x01c00000 - 0x1000, bo, 0, 4096, 0), -EINVAL);
	CHECK_EQ(sgxfive_vm_map(vm, 0x2e000000 + 0x02000000 - 0x2000, bo, 0, 4096, 0), 0);
	CHECK_EQ(sgxfive_vm_unmap(vm, 0x2e000000 + 0x02000000 - 0x2000, 4096), 0);
	sgxfive_mock_get_stats(mock, &st);
	CHECK_EQ(st.mappings, 2);
	CHECK_EQ(sgxfive_vm_unmap(vm, a, 4096), -ENOENT);
	CHECK_EQ(sgxfive_vm_unmap(vm, a, 8192), 0);
	CHECK_EQ(sgxfive_vm_unmap(vm, a, 8192), -ENOENT);

	CHECK_EQ(sgxfive_ctx_create(vm, &ctx), 0);
	CHECK(ctx != 0);
	sgxfive_mock_get_stats(mock, &st);
	CHECK_EQ(st.ctxs, 1);
	CHECK_EQ(sgxfive_ctx_destroy(dev, ctx), 0);
	CHECK_EQ(sgxfive_ctx_destroy(dev, ctx), -EINVAL);

	/* A BO stays alive while a VM maps it; destroying the VM releases everything. */
	sgxfive_bo_destroy(bo);
	sgxfive_mock_get_stats(mock, &st);
	CHECK_EQ(st.bos, 1);
	sgxfive_vm_destroy(vm);
	sgxfive_mock_get_stats(mock, &st);
	CHECK_EQ(st.bos + st.vms + st.mappings, 0);
	sgxfive_dev_close(dev);
}

static void raw_ctx(struct sgxfive_dev *dev, uint32_t vm)
{
	struct drm_sgxfive_create_context_args c = { .vm_context_handle = vm };

	c.type = 2;		/* 0 transfer, 1 render */
	CHECK_EQ(sgxfive_dev_ioctl(dev, DRM_IOCTL_SGXFIVE_CREATE_CONTEXT, &c), -EINVAL);
	c.type = 0;
	c.priority = 1;
	CHECK_EQ(sgxfive_dev_ioctl(dev, DRM_IOCTL_SGXFIVE_CREATE_CONTEXT, &c), -EINVAL);
	c.priority = 0;
	c.flags = 1;
	CHECK_EQ(sgxfive_dev_ioctl(dev, DRM_IOCTL_SGXFIVE_CREATE_CONTEXT, &c), -EINVAL);
	c.flags = 0;
	/* A transfer context states no render-target size; the padding is zero. */
	c.max_width = 64;
	CHECK_EQ(sgxfive_dev_ioctl(dev, DRM_IOCTL_SGXFIVE_CREATE_CONTEXT, &c), -EINVAL);
	c.max_width = 0;
	c.max_height = 64;
	CHECK_EQ(sgxfive_dev_ioctl(dev, DRM_IOCTL_SGXFIVE_CREATE_CONTEXT, &c), -EINVAL);
	c.max_height = 0;
	c._padding_1c = 1;
	CHECK_EQ(sgxfive_dev_ioctl(dev, DRM_IOCTL_SGXFIVE_CREATE_CONTEXT, &c), -EINVAL);
	c._padding_1c = 0;
	c.vm_context_handle = 77;
	CHECK_EQ(sgxfive_dev_ioctl(dev, DRM_IOCTL_SGXFIVE_CREATE_CONTEXT, &c), -EINVAL);
}

static void sync_and_submit(void)
{
	struct sgxfive_dev *dev = open_dev(&(struct sgxfive_mock_config){ 0 });
	const uint32_t dummy = DRM_SGXFIVE_SUBMIT_JOB_TRANSFER_DUMMY;
	struct drm_sgxfive_transfer_cmd cmd = { 0 };
	struct drm_sgxfive_mem_update upd = { .device_addr = 0x3e000000, .value = 1 };
	struct drm_sgxfive_sync_op op, ops2[3];
	struct drm_sgxfive_job jobs[2];
	struct sgxfive_mock_stats st;
	struct sgxfive_vm *vm = NULL;
	uint32_t ctx = 0, a = 0, b = 0, t = 0, failed = 99;

	CHECK_EQ(sgxfive_vm_create(dev, &vm), 0);
	raw_ctx(dev, sgxfive_vm_handle(vm));
	CHECK_EQ(sgxfive_ctx_create(vm, &ctx), 0);
	CHECK_EQ(sgxfive_syncobj_create(dev, false, &a), 0);
	CHECK_EQ(sgxfive_syncobj_create(dev, false, &b), 0);
	CHECK_EQ(sgxfive_syncobj_wait(dev, a, 0, 0), -ETIME);

	/* A dummy signals its syncobj. */
	CHECK_EQ(sgxfive_submit_transfer(dev, ctx, dummy, NULL, 0, a), 0);
	CHECK_EQ(sgxfive_syncobj_wait(dev, a, 0, 1000000), 0);

	/* Waiting on a syncobj without a fence is -EINVAL (drm_syncobj_find_fence)... */
	CHECK_EQ(sgxfive_syncobj_destroy(dev, a), 0);
	CHECK_EQ(sgxfive_syncobj_create(dev, false, &a), 0);
	CHECK_EQ(sgxfive_submit_transfer(dev, ctx, dummy, NULL, a, b), -EINVAL);
	CHECK_EQ(sgxfive_syncobj_wait(dev, b, 0, 0), -ETIME);
	/* ...unless an earlier job of the same call signals it. */
	ops2[0] = (struct drm_sgxfive_sync_op){ a, DRM_SGXFIVE_SYNC_OP_FLAG_SIGNAL, 0 };
	ops2[1] = (struct drm_sgxfive_sync_op){ a, DRM_SGXFIVE_SYNC_OP_FLAG_WAIT, 0 };
	ops2[2] = (struct drm_sgxfive_sync_op){ b, DRM_SGXFIVE_SYNC_OP_FLAG_SIGNAL, 0 };
	jobs[0] = (struct drm_sgxfive_job){
		.type = DRM_SGXFIVE_JOB_TYPE_TRANSFER, .context_handle = ctx, .flags = dummy,
		.sync_ops = DRM_SGXFIVE_OBJ_ARRAY(1, &ops2[0]),
	};
	jobs[1] = jobs[0];
	jobs[1].sync_ops = (struct drm_sgxfive_obj_array)DRM_SGXFIVE_OBJ_ARRAY(2, &ops2[1]);
	CHECK_EQ(sgxfive_submit(dev, jobs, 2, &failed), 0);
	CHECK_EQ(sgxfive_syncobj_wait(dev, b, 0, 0), 0);
	sgxfive_mock_get_stats(mock, &st);
	CHECK_EQ(st.dummies_run, 3);

	/* Timeline points. */
	CHECK_EQ(sgxfive_syncobj_create(dev, false, &t), 0);
	op = (struct drm_sgxfive_sync_op){
		.handle = t, .value = 2,
		.flags = DRM_SGXFIVE_SYNC_OP_FLAG_SIGNAL |
			 DRM_SGXFIVE_SYNC_OP_FLAG_HANDLE_TYPE_TIMELINE_SYNCOBJ,
	};
	jobs[0] = (struct drm_sgxfive_job){
		.type = DRM_SGXFIVE_JOB_TYPE_TRANSFER, .context_handle = ctx, .flags = dummy,
		.sync_ops = DRM_SGXFIVE_OBJ_ARRAY(1, &op),
	};
	CHECK_EQ(sgxfive_syncobj_wait(dev, t, 2, 0), -ETIME);
	CHECK_EQ(sgxfive_submit(dev, jobs, 1, &failed), 0);
	CHECK_EQ(sgxfive_syncobj_wait(dev, t, 1, 0), 0);
	CHECK_EQ(sgxfive_syncobj_wait(dev, t, 2, 0), 0);
	CHECK_EQ(sgxfive_syncobj_wait(dev, t, 3, 0), -ETIME);

	/* Validation: one bad job fails the whole call, reporting its index. */
	jobs[0] = (struct drm_sgxfive_job){
		.type = DRM_SGXFIVE_JOB_TYPE_TRANSFER, .context_handle = ctx, .flags = dummy,
	};
	jobs[1] = jobs[0];
	jobs[1].updates = (struct drm_sgxfive_obj_array)DRM_SGXFIVE_OBJ_ARRAY(1, &upd);
	CHECK_EQ(sgxfive_submit(dev, jobs, 2, &failed), -EINVAL);
	CHECK_EQ(failed, 1);
	jobs[1].updates = (struct drm_sgxfive_obj_array){ .stride = sizeof(upd) };
	CHECK_EQ(sgxfive_submit(dev, jobs, 2, &failed), -EINVAL);	/* stride alone */
	jobs[1].updates = (struct drm_sgxfive_obj_array){ 0 };
	jobs[1].flags = 1u << 7;
	CHECK_EQ(sgxfive_submit(dev, jobs, 2, &failed), -EINVAL);
	CHECK_EQ(failed, 1);
	jobs[1].flags = dummy;
	jobs[1].cmd_stream = (uintptr_t)&cmd;
	jobs[1].cmd_stream_len = sizeof(cmd);
	CHECK_EQ(sgxfive_submit(dev, jobs, 2, &failed), -EINVAL);	/* dummy with a stream */
	jobs[1].flags = 0;
	jobs[1].cmd_stream_len = 0x40;
	CHECK_EQ(sgxfive_submit(dev, jobs, 2, &failed), -EINVAL);	/* short stream */
	jobs[1].cmd_stream_len = sizeof(cmd);
	jobs[1].type = 1;
	CHECK_EQ(sgxfive_submit(dev, jobs, 2, &failed), -EINVAL);
	jobs[1].type = 0;
	jobs[1].context_handle = 1234;
	CHECK_EQ(sgxfive_submit(dev, jobs, 2, &failed), -EINVAL);
	jobs[1].context_handle = ctx;
	jobs[1].flags = dummy;
	jobs[1].cmd_stream = 0;
	jobs[1].cmd_stream_len = 0;
	op = (struct drm_sgxfive_sync_op){ .handle = b, .flags = 1u << 8 };
	jobs[1].sync_ops = (struct drm_sgxfive_obj_array)DRM_SGXFIVE_OBJ_ARRAY(1, &op);
	CHECK_EQ(sgxfive_submit(dev, jobs, 2, &failed), -EINVAL);
	op.flags = DRM_SGXFIVE_SYNC_OP_FLAG_SIGNAL;
	op.value = 5;					/* binary syncobj with a point */
	CHECK_EQ(sgxfive_submit(dev, jobs, 2, &failed), -EINVAL);
	op.value = 0;
	op.handle = 999;				/* no such syncobj */
	CHECK_EQ(sgxfive_submit(dev, jobs, 2, &failed), -ENOENT);
	sgxfive_mock_get_stats(mock, &st);
	CHECK_EQ(st.dummies_run, 4);			/* none of the failed calls ran */
	op.handle = b;
	CHECK_EQ(sgxfive_submit(dev, jobs, 2, &failed), 0);
	sgxfive_mock_get_stats(mock, &st);
	CHECK_EQ(st.dummies_run, 6);

	/* A transfer whose PDS addresses lie outside the user heaps is rejected. */
	cmd.event_pixel_pds_exec = 0x30000000;		/* KERNEL_CODE */
	CHECK_EQ(sgxfive_submit_transfer(dev, ctx, 0, &cmd, 0, 0), -EINVAL);
	/*
	 * The kernel checks the page of each address against the user heaps, and
	 * BIF_3D_REQ_BASE's 1 MiB alignment; the render box is the job's own.
	 */
	cmd.bif_3d_req_base = 0x3e000000;
	cmd.pds_exec_base = 0x2e000000;
	cmd.event_pixel_pds_exec = 0x2e000000 + 0x02000000 - 0x1000 + 0x10;	/* past PDS_PIXEL */
	CHECK_EQ(sgxfive_submit_transfer(dev, ctx, 0, &cmd, 0, 0), -EINVAL);
	cmd.event_pixel_pds_exec = 0x2e000000 + 0x02000000 - 0x1000 - 4;
	cmd.bif_3d_req_base = 0x3e080000;
	CHECK_EQ(sgxfive_submit_transfer(dev, ctx, 0, &cmd, 0, 0), -EINVAL);
	cmd.bif_3d_req_base = 0x3e000000;
	cmd.isp_render_box2 = 0xffffffff;
	CHECK_EQ(sgxfive_submit_transfer(dev, ctx, 0, &cmd, 0, 0), 0);	/* runs, and faults */
	/*
	 * The kernel wants an 8-byte aligned command stream, which a struct of dwords on the stack
	 * of an i686 build is not (the type's alignment is 4): the call aligns its own copy. A
	 * context of its own, the one above is lost by the fault.
	 */
	{
		_Alignas(8) unsigned char raw[sizeof(cmd) + 8];
		struct drm_sgxfive_transfer_cmd *odd = (void *)(raw + 4);
		uint32_t ctx2 = 0;

		memcpy(odd, &cmd, sizeof(cmd));
		odd->isp_render_box2 = 0;
		CHECK_EQ((uintptr_t)odd % 8, 4);
		CHECK_EQ(sgxfive_ctx_create(vm, &ctx2), 0);
		CHECK_EQ(sgxfive_submit_transfer(dev, ctx2, 0, odd, 0, 0), 0);
		CHECK_EQ(sgxfive_ctx_destroy(dev, ctx2), 0);
	}
	CHECK_EQ(sgxfive_ctx_destroy(dev, ctx), 0);
	sgxfive_vm_destroy(vm);
	sgxfive_dev_close(dev);
	sgxfive_mock_get_stats(mock, &st);
	CHECK_EQ(st.syncobjs + st.ctxs + st.vms, 0);		/* closing the file frees all */
}

/* SUBMIT_JOBS with the jobs at a stride other than the struct's. */
static int submit_raw(struct sgxfive_dev *dev, const void *jobs, uint32_t stride, uint32_t n,
		      uint32_t *failed)
{
	struct drm_sgxfive_submit_jobs_args a = { { stride, n, (uintptr_t)jobs } };
	int ret = sgxfive_dev_ioctl(dev, DRM_IOCTL_SGXFIVE_SUBMIT_JOBS, &a);

	*failed = a.jobs.count;
	return ret;
}

/*
 * Array strides: a shorter element is zero-extended, a longer one needs a zero
 * tail, a stride of 0 or above DRM_SGXFIVE_OBJ_ARRAY_MAX_STRIDE is -EINVAL; at
 * most max_jobs jobs and max_sync_ops sync ops, and at least one job.
 */
static void arrays(void)
{
	struct sgxfive_dev *dev = open_dev(&(struct sgxfive_mock_config){ 0 });
	const struct drm_sgxfive_dev_query_job_info *ji = &sgxfive_dev_info(dev)->job;
	const uint32_t dummy = DRM_SGXFIVE_SUBMIT_JOB_TRANSFER_DUMMY;
	const uint32_t big = DRM_SGXFIVE_OBJ_ARRAY_MAX_STRIDE;
	const size_t js = sizeof(struct drm_sgxfive_job);
	static uint8_t buf[17 * DRM_SGXFIVE_OBJ_ARRAY_MAX_STRIDE];
	struct drm_sgxfive_job job, many[17];
	struct drm_sgxfive_sync_op ops[17];
	struct sgxfive_mock_stats st;
	struct sgxfive_vm *vm = NULL;
	uint32_t ctx = 0, s = 0, failed = 99, run;

	CHECK_EQ(ji->max_jobs, 16);
	CHECK_EQ(ji->max_sync_ops, 16);
	CHECK_EQ(sgxfive_vm_create(dev, &vm), 0);
	CHECK_EQ(sgxfive_ctx_create(vm, &ctx), 0);
	CHECK_EQ(sgxfive_syncobj_create(dev, false, &s), 0);
	job = (struct drm_sgxfive_job){
		.type = DRM_SGXFIVE_JOB_TYPE_TRANSFER, .context_handle = ctx, .flags = dummy,
	};

	/* Two jobs of 16 bytes: the type, context, flags and stream length; the rest 0. */
	memset(buf, 0, sizeof(buf));
	memcpy(buf, &job, 16);
	memcpy(buf + 16, &job, 16);
	CHECK_EQ(submit_raw(dev, buf, 16, 2, &failed), 0);
	sgxfive_mock_get_stats(mock, &st);
	CHECK_EQ(st.dummies_run, 2);
	/* The largest stride, with a zero tail; then a byte of the second job's tail set. */
	memset(buf, 0, sizeof(buf));
	memcpy(buf, &job, js);
	memcpy(buf + big, &job, js);
	CHECK_EQ(submit_raw(dev, buf, big, 2, &failed), 0);
	buf[2 * big - 1] = 1;
	CHECK_EQ(submit_raw(dev, buf, big, 2, &failed), -EINVAL);
	CHECK_EQ(failed, 1);
	buf[2 * big - 1] = 0;
	CHECK_EQ(submit_raw(dev, buf, big + 8, 1, &failed), -EINVAL);
	CHECK_EQ(submit_raw(dev, buf, 0, 1, &failed), -EINVAL);
	sgxfive_mock_get_stats(mock, &st);
	CHECK_EQ(st.dummies_run, 4);

	/* Job counts: none is -EINVAL, and so are more than max_jobs. */
	for (int i = 0; i < 17; i++)
		many[i] = job;
	CHECK_EQ(sgxfive_submit(dev, many, 0, &failed), -EINVAL);
	CHECK_EQ(sgxfive_submit(dev, many, 17, &failed), -EINVAL);
	CHECK_EQ(sgxfive_submit(dev, many, 16, &failed), 0);
	sgxfive_mock_get_stats(mock, &st);
	run = st.dummies_run;
	CHECK_EQ(run, 20);

	/* Sync ops of 8 bytes, the handle and flags, signal a binary syncobj. */
	memset(buf, 0, sizeof(buf));
	((uint32_t *)buf)[0] = s;
	((uint32_t *)buf)[1] = DRM_SGXFIVE_SYNC_OP_FLAG_SIGNAL;
	job.sync_ops = (struct drm_sgxfive_obj_array){ 8, 1, (uintptr_t)buf };
	CHECK_EQ(sgxfive_submit(dev, &job, 1, &failed), 0);
	CHECK_EQ(sgxfive_syncobj_wait(dev, s, 0, 0), 0);
	job.sync_ops.stride = big + 1;
	CHECK_EQ(sgxfive_submit(dev, &job, 1, &failed), -EINVAL);
	job.sync_ops.stride = 0;
	CHECK_EQ(sgxfive_submit(dev, &job, 1, &failed), -EINVAL);
	job.sync_ops.stride = 24;			/* longer, a non-zero tail */
	((uint32_t *)buf)[4] = 1;
	CHECK_EQ(sgxfive_submit(dev, &job, 1, &failed), -EINVAL);
	/* At most max_sync_ops; a timeline signal may name point 0. */
	for (int i = 0; i < 17; i++)
		ops[i] = (struct drm_sgxfive_sync_op){ s, DRM_SGXFIVE_SYNC_OP_FLAG_SIGNAL, 0 };
	job.sync_ops = (struct drm_sgxfive_obj_array)DRM_SGXFIVE_OBJ_ARRAY(17, ops);
	CHECK_EQ(sgxfive_submit(dev, &job, 1, &failed), -EINVAL);
	job.sync_ops.count = 16;
	CHECK_EQ(sgxfive_submit(dev, &job, 1, &failed), 0);
	ops[0].flags |= DRM_SGXFIVE_SYNC_OP_FLAG_HANDLE_TYPE_TIMELINE_SYNCOBJ;
	job.sync_ops.count = 1;
	CHECK_EQ(sgxfive_submit(dev, &job, 1, &failed), 0);
	sgxfive_mock_get_stats(mock, &st);
	CHECK_EQ(st.dummies_run, run + 3);

	sgxfive_vm_destroy(vm);
	sgxfive_dev_close(dev);
}

/*
 * A bad wait on a later job fails the call before anything is queued: an
 * unknown syncobj is -ENOENT, one without a fence -EINVAL; jobs.count is the
 * failing job. A wait is also met by an earlier job of the call that signals
 * the same handle as the same type (a timeline at the wait's point or later).
 */
static void whole_call(void)
{
	struct sgxfive_dev *dev = open_dev(&(struct sgxfive_mock_config){ 0 });
	const uint32_t dummy = DRM_SGXFIVE_SUBMIT_JOB_TRANSFER_DUMMY;
	struct drm_sgxfive_sync_op sig, wait;
	struct drm_sgxfive_job jobs[3];
	struct sgxfive_mock_stats st;
	struct sgxfive_vm *vm = NULL;
	uint32_t ctx = 0, a = 0, b = 0, failed = 99;

	CHECK_EQ(sgxfive_vm_create(dev, &vm), 0);
	CHECK_EQ(sgxfive_ctx_create(vm, &ctx), 0);
	CHECK_EQ(sgxfive_syncobj_create(dev, false, &a), 0);
	CHECK_EQ(sgxfive_syncobj_create(dev, false, &b), 0);
	sig = (struct drm_sgxfive_sync_op){ a, DRM_SGXFIVE_SYNC_OP_FLAG_SIGNAL, 0 };
	wait = (struct drm_sgxfive_sync_op){ b, DRM_SGXFIVE_SYNC_OP_FLAG_WAIT, 0 };
	for (int i = 0; i < 3; i++)
		jobs[i] = (struct drm_sgxfive_job){
			.type = DRM_SGXFIVE_JOB_TYPE_TRANSFER, .context_handle = ctx,
			.flags = dummy,
		};
	jobs[0].sync_ops = (struct drm_sgxfive_obj_array)DRM_SGXFIVE_OBJ_ARRAY(1, &sig);
	jobs[2].sync_ops = (struct drm_sgxfive_obj_array)DRM_SGXFIVE_OBJ_ARRAY(1, &wait);
	CHECK_EQ(sgxfive_submit(dev, jobs, 3, &failed), -EINVAL);	/* b has no fence */
	CHECK_EQ(failed, 2);
	wait.handle = 999;
	CHECK_EQ(sgxfive_submit(dev, jobs, 3, &failed), -ENOENT);
	CHECK_EQ(failed, 2);
	sgxfive_mock_get_stats(mock, &st);
	CHECK_EQ(st.dummies_run, 0);
	CHECK_EQ(sgxfive_syncobj_wait(dev, a, 0, 0), -ETIME);	/* job 0 never ran */
	/* A signal of the same job does not count, nor one of another handle type. */
	{
		struct drm_sgxfive_sync_op own[2] = {
			{ a, DRM_SGXFIVE_SYNC_OP_FLAG_SIGNAL, 0 },
			{ a, DRM_SGXFIVE_SYNC_OP_FLAG_WAIT, 0 },
		};

		jobs[2].sync_ops = (struct drm_sgxfive_obj_array)DRM_SGXFIVE_OBJ_ARRAY(2, own);
		CHECK_EQ(sgxfive_submit(dev, &jobs[2], 1, &failed), -EINVAL);
		jobs[2].sync_ops = (struct drm_sgxfive_obj_array)DRM_SGXFIVE_OBJ_ARRAY(1, &wait);
	}
	wait = (struct drm_sgxfive_sync_op){
		a, DRM_SGXFIVE_SYNC_OP_FLAG_WAIT |
		   DRM_SGXFIVE_SYNC_OP_FLAG_HANDLE_TYPE_TIMELINE_SYNCOBJ, 1 };
	CHECK_EQ(sgxfive_submit(dev, jobs, 3, &failed), -EINVAL);	/* binary signal */
	CHECK_EQ(failed, 2);
	sig = (struct drm_sgxfive_sync_op){
		a, DRM_SGXFIVE_SYNC_OP_FLAG_SIGNAL |
		   DRM_SGXFIVE_SYNC_OP_FLAG_HANDLE_TYPE_TIMELINE_SYNCOBJ, 2 };
	wait.value = 3;						/* beyond the signalled point */
	CHECK_EQ(sgxfive_submit(dev, jobs, 3, &failed), -EINVAL);
	wait = (struct drm_sgxfive_sync_op){ a, DRM_SGXFIVE_SYNC_OP_FLAG_WAIT, 0 };
	CHECK_EQ(sgxfive_submit(dev, jobs, 3, &failed), -EINVAL);	/* timeline signal */
	sgxfive_mock_get_stats(mock, &st);
	CHECK_EQ(st.dummies_run, 0);
	wait = (struct drm_sgxfive_sync_op){
		a, DRM_SGXFIVE_SYNC_OP_FLAG_WAIT |
		   DRM_SGXFIVE_SYNC_OP_FLAG_HANDLE_TYPE_TIMELINE_SYNCOBJ, 2 };
	CHECK_EQ(sgxfive_submit(dev, jobs, 3, &failed), 0);	/* the point job 0 signals */
	sig = (struct drm_sgxfive_sync_op){ b, DRM_SGXFIVE_SYNC_OP_FLAG_SIGNAL, 0 };
	wait = (struct drm_sgxfive_sync_op){ b, DRM_SGXFIVE_SYNC_OP_FLAG_WAIT, 0 };
	CHECK_EQ(sgxfive_submit(dev, jobs, 3, &failed), 0);	/* binary, signalled by job 0 */
	sgxfive_mock_get_stats(mock, &st);
	CHECK_EQ(st.dummies_run, 6);

	sgxfive_vm_destroy(vm);
	sgxfive_dev_close(dev);
}

/*
 * Per open file: at most DRM_SGXFIVE_FILE_MAX_VM_CONTEXTS VM contexts and
 * DRM_SGXFIVE_FILE_MAX_CONTEXTS contexts at a time, -ENOSPC beyond; another
 * open file has its own.
 */
static void file_limits(void)
{
	struct sgxfive_dev *dev = open_dev(&(struct sgxfive_mock_config){ 0 }), *dev2 = NULL;
	static struct sgxfive_vm *vms[DRM_SGXFIVE_FILE_MAX_VM_CONTEXTS + 1];
	static uint32_t ctxs[DRM_SGXFIVE_FILE_MAX_CONTEXTS + 1];
	struct sgxfive_vm *extra = NULL;
	uint32_t i, n = 0;

	for (i = 0; i < DRM_SGXFIVE_FILE_MAX_VM_CONTEXTS; i++)
		n += !sgxfive_vm_create(dev, &vms[i]);
	CHECK_EQ(n, DRM_SGXFIVE_FILE_MAX_VM_CONTEXTS);
	CHECK_EQ(sgxfive_vm_create(dev, &extra), -ENOSPC);
	CHECK_EQ(sgxfive_dev_open(sgxfive_mock_backend(mock), NULL, &dev2), 0);
	CHECK_EQ(sgxfive_vm_create(dev2, &extra), 0);
	sgxfive_vm_destroy(extra);
	sgxfive_dev_close(dev2);
	sgxfive_vm_destroy(vms[0]);
	CHECK_EQ(sgxfive_vm_create(dev, &vms[0]), 0);

	for (i = n = 0; i < DRM_SGXFIVE_FILE_MAX_CONTEXTS; i++)
		n += !sgxfive_ctx_create(vms[i % 2], &ctxs[i]);
	CHECK_EQ(n, DRM_SGXFIVE_FILE_MAX_CONTEXTS);
	CHECK_EQ(sgxfive_ctx_create(vms[2], &ctxs[i]), -ENOSPC);
	CHECK_EQ(sgxfive_ctx_destroy(dev, ctxs[0]), 0);
	CHECK_EQ(sgxfive_ctx_create(vms[2], &ctxs[0]), 0);

	for (i = 0; i < DRM_SGXFIVE_FILE_MAX_VM_CONTEXTS; i++)
		sgxfive_vm_destroy(vms[i]);
	sgxfive_dev_close(dev);
}

/*
 * The kernel's debugfs vm_pde_addr, vm_pde_size and vm_pde_layout (Q109): a VM_MAP at the
 * address takes the large-page path only for exactly 4 MiB and a size code and layout the
 * kernel makes a region for (codes 1-4 any layout, 0 and 5 dense or pt4k, 6 and 7 dense);
 * anything else at the address is -EINVAL, elsewhere every map is as ever. The mock checks
 * these and maps the buffer as ever: it does not model the large page.
 */
static void vm_pde_knobs(void)
{
	static const struct { uint32_t code, layout; int want; } pairs[] = {
		{ 0, 0, 0 }, { 0, 1, 0 }, { 0, 2, -EINVAL }, { 0, 3, -EINVAL },
		{ 1, 3, 0 }, { 3, 2, 0 }, { 4, 3, 0 },
		{ 5, 1, 0 }, { 5, 2, -EINVAL }, { 5, 3, -EINVAL },
		{ 6, 0, 0 }, { 6, 1, -EINVAL }, { 7, 0, 0 }, { 7, 3, -EINVAL },
	};
	const uint64_t at = 0x60000000;

	for (unsigned int i = 0; i < sizeof(pairs) / sizeof(pairs[0]); i++) {
		struct sgxfive_dev *dev = open_dev(&(struct sgxfive_mock_config){
			.vm_pde_addr = (uint32_t)at, .vm_pde_size = pairs[i].code,
			.vm_pde_layout = pairs[i].layout });
		struct sgxfive_vm *vm = NULL;
		struct sgxfive_bo *bo = NULL;

		CHECK_EQ(sgxfive_vm_create(dev, &vm), 0);
		CHECK_EQ(sgxfive_bo_create(dev, 0x800000, 0, &bo), 0);
		CHECK_EQ(sgxfive_vm_map(vm, at, bo, 0, 0x400000, 0), pairs[i].want);
		/* elsewhere, and the next slot, as ever */
		CHECK_EQ(sgxfive_vm_map(vm, at + 0x400000, bo, 0x400000, 0x400000, 0), 0);
		if (!pairs[i].want)
			CHECK_EQ(sgxfive_vm_unmap(vm, at, 0x400000), 0);
		/* at the address, only 4 MiB */
		CHECK_EQ(sgxfive_vm_map(vm, at, bo, 0, 0x1000, 0), -EINVAL);
		CHECK_EQ(sgxfive_vm_map(vm, at, bo, 0, 0x3ff000, 0), -EINVAL);
		CHECK_EQ(sgxfive_vm_map(vm, at - 0x1000, bo, 0, 0x1000, 0), 0);
		sgxfive_bo_destroy(bo);
		sgxfive_vm_destroy(vm);
		sgxfive_dev_close(dev);
	}
	/* off (address 0): whatever the code and layout */
	{
		struct sgxfive_dev *dev = open_dev(&(struct sgxfive_mock_config){
			.vm_pde_size = 5, .vm_pde_layout = 2 });
		struct sgxfive_vm *vm = NULL;
		struct sgxfive_bo *bo = NULL;

		CHECK_EQ(sgxfive_vm_create(dev, &vm), 0);
		CHECK_EQ(sgxfive_bo_create(dev, 0x400000, 0, &bo), 0);
		CHECK_EQ(sgxfive_vm_map(vm, at, bo, 0, 0x1000, 0), 0);
		sgxfive_bo_destroy(bo);
		sgxfive_vm_destroy(vm);
		sgxfive_dev_close(dev);
	}
}

int main(void)
{
	discovery();
	adopt();
	query();
	bos();
	vms();
	vm_pde_knobs();
	sync_and_submit();
	arrays();
	whole_call();
	file_limits();
	sgxfive_mock_destroy(mock);
	return tap_done();
}
