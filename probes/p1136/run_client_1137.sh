#!/bin/bash
# run_client_1137.sh TABLE [between]: one fw37 client table through the 11.35 campaign runner (rt/ is a copy of
# the 11.35 built tree's tools). No register is written. Data to ~/src/resgx545-data/usse/<table>/.
cd "$(dirname "$0")/rt" || exit 1
export SGX_TARGET_HOST=jtorra@10.42.0.2 SGX_TARGET_SSH_OPTS="-o HostKeyAlias=cedar -o BatchMode=yes"
export SGX_PROBE_TOOL=./sgxfive-test-1135 SGX_SWEEP_TOOL=./sgxfive-test-1135
export RESGX545_KERNEL_COMMIT=1dd291a61499 PYTHONDONTWRITEBYTECODE=1
export RESGX545_TOOL_SOURCE_SHA256=f5cdccb15a73de6584e33e43c5a2eb1ba5e37de7e43a07c39cb9a8d386c6e74b
[ -n "${2:-}" ] && export SGX_PROBE_BETWEEN='D=$(sudo -n sh -c "ls -d /sys/kernel/debug/dri/*/sgx" | head -n 1); echo 1 | sudo -n tee $D/reset >/dev/null; sleep 3'
exec python3 tools/campaign/campaign.py --target laptop --data "$HOME/src/resgx545-data" --datasets datasets "probes/usse/$1.toml"
