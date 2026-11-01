#!/bin/bash
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# run_temps.sh TABLE [between]: one phase 11.35 table (probes/usse/temps-fresh-{a,b,c}.toml, made by
# gen_temps.py) through the campaign runner on the laptop over the cable, with the tool deployed by
# deploy_tool.sh. With a second argument the laptop resets the GPU by debugfs and waits 3 s before every
# job (SGX_PROBE_BETWEEN). The data go to ~/src/resgx545-data, the manifests to $DS. No register is
# written: no kreg, no kregnow, no kpoke.
cd "$(dirname "$0")/../.." || exit 1
export SGX_TARGET_HOST=jtorra@10.42.0.2 SGX_TARGET_SSH_OPTS="-o HostKeyAlias=cedar -o BatchMode=yes"
export SGX_PROBE_TOOL=./sgxfive-test-1135 SGX_SWEEP_TOOL=./sgxfive-test-1135
export RESGX545_KERNEL_COMMIT=${RESGX545_KERNEL_COMMIT:-1dd291a61499} PYTHONDONTWRITEBYTECODE=1
[ -n "${2:-}" ] && export SGX_PROBE_BETWEEN='D=$(sudo -n sh -c "ls -d /sys/kernel/debug/dri/*/sgx" | head -n 1); echo 1 | sudo -n tee $D/reset >/dev/null; sleep 3'
exec python3 tools/campaign/campaign.py --target laptop \
	--data "${DATA:-$HOME/src/resgx545-data}" --datasets "${DS:-datasets}" "$1"
