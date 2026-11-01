#!/bin/bash
# build1135.sh: move the laptop's ~/src/linux-sgx to the series tip (a clean detached checkout: it stops if
# the tree is not clean, no reset, no stash) and build the module in the sgx-build root with M=drivers/gpu/drm/gma500
# (incremental). Prints the built srcversion and the vermagic. Installing (install1135.sh) needs recheck.pass; a build
# may run beside the check (BUILD_BEFORE_CHECK=1): the qemu of the check uses one core.
set -u
H=$(cd "$(dirname "$0")" && pwd)
TIP=$(cut -d' ' -f3 "$H/commits.txt")
[ "$(cat "$H/recheck.pass" 2>/dev/null)" = "$TIP" ] || [ -n "${BUILD_BEFORE_CHECK:-}" ] || { echo "recheck.pass does not hold the tip: nothing built"; exit 1; }
SSH="ssh -o HostKeyAlias=cedar -o BatchMode=yes jtorra@10.42.0.2"
git -C "$H/fork" bundle create - 3d9b8bdefe94..p1135 | $SSH "cd src/linux-sgx && git bundle unbundle /dev/stdin >/dev/null" || exit 1
$SSH 'bash -s' <<REMOTE
set -u
cd ~/src/linux-sgx || exit 1
dirty=\$(git status --porcelain --untracked-files=no | head -n 3)
[ -z "\$dirty" ] || { echo "tree not clean: \$dirty: stop (no reset, no stash)"; exit 1; }
git checkout -q --detach $TIP || { echo "checkout failed: stop"; exit 1; }
git log -1 --format='tree at %h %s'
time SGX_KERNEL_TREE=src/linux-sgx sgx-build kernel make ARCH=i386 -j4 M=drivers/gpu/drm/gma500 2>&1 | tail -n 8
KO=\$HOME/src/linux-sgx/drivers/gpu/drm/gma500/gma500_gfx.ko
ls -la \$KO
echo "built srcversion: \$(modinfo -F srcversion \$KO)"
echo "vermagic: \$(modinfo -F vermagic \$KO)"
REMOTE
