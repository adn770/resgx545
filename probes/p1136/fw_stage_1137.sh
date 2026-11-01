#!/bin/bash
# fw_stage_1137.sh STAGE: one firmware stage of run_1137.py as dataset firmware-tasks/p1137-STAGE (untracked data
# repository), with the health check before and after, the laptop's journalctl -k for the stage (gzipped), the page
# and regs dumps the runner saves, and env.toml.  Never writes a clock-gate register (run_1137.py has no such call).
S=$1
cd "$(dirname "$0")" || exit 1
HERE=$PWD
LAP="ssh -o HostKeyAlias=cedar -o BatchMode=yes -o ConnectTimeout=10 jtorra@10.42.0.2"
DS=$HOME/src/resgx545-data/firmware-tasks/p1137-$S
mkdir -p logs "$DS"
echo "## health before"; bash ../../health1135.sh 2>&1 | tail -8
START=$($LAP 'date +%s')
python3 -I run_1137_logged.py p1137-$S $S 2>&1 | tee logs/p1137-$S.log
RC=${PIPESTATUS[0]}
echo "## runner rc $RC"
$LAP 'sudo -n journalctl -k --since "@'$START'" --no-pager' | gzip -n -6 > "$DS/kernel.log.gz"
$LAP 'D=/sys/kernel/debug/dri/0/sgx; for f in status own_res regs own_arm; do echo "## $f"; sudo -n cat $D/$f 2>&1 | head -400; done' | gzip -n -6 > "$DS/laptop-state-after.txt.gz"
rsync -a --exclude jobs out/p1137-$S/ "$DS/"
[ -d out/p1137-$S/jobs ] && COPYFILE_DISABLE=1 tar -czf "$DS/jobs.tar.gz" -C out/p1137-$S jobs
# a stop dumps regs, status, own_res and dmesg on the LAPTOP under the Mac path it was given: bring them over
LD=$(pwd)/out/p1137-$S
if $LAP "[ -d '$LD' ]"; then $LAP "tar -czf - -C '$LD' ." > "$DS/laptop-stop-dumps.tar.gz"; fi
cp logs/p1137-$S.log "$DS/runner.log"
{ echo "# phase 11.37 firmware stage $S"
  echo "name = \"p1137-$S\""; echo "stage = \"$S\""; echo "date = \"$(date +%Y-%m-%dT%H:%M:%S%z)\""
  echo "kind = \"firmware (EDM) task of ours, the landed verifier\""
  echo "tool = \"tools/fwtask/run_stage.py and fwtask_run.py of ~/src/resgx545 (landed), run_1137.py of this tree\""
  echo "run_1137_logged_sha256 = \"$(shasum -a 256 run_1137_logged.py | cut -d' ' -f1)\""
  echo "run_1137_sha256 = \"$(shasum -a 256 run_1137.py | cut -d' ' -f1)\""
  echo "predictions_sha256 = \"$(shasum -a 256 predictions-1137.toml | cut -d' ' -f1)\""
  echo "manifest_sha256 = \"$(shasum -a 256 manifest-1137.sha256 | cut -d' ' -f1)\""
  echo "fork_tip = \"1dd291a61499\""
  echo "tool_sha256_pixel_client = \"7732b94538cd221f25be85f307d93168413ef57cfae81065a268a73f08902687\""
  echo "tool_source_sha256 = \"f5cdccb15a73de6584e33e43c5a2eb1ba5e37de7e43a07c39cb9a8d386c6e74b\""
  $LAP 'echo "kernel = \"$(uname -r)\""; echo "module_srcversion_installed = \"$(modinfo -F srcversion gma500_gfx)\""; echo "module_srcversion_loaded = \"$(sudo -n cat /sys/module/gma500_gfx/srcversion)\""; echo "firmware_sha256 = \"$(sha256sum /lib/firmware/sgx545_ukernel.fw | cut -d" " -f1)\""'
  echo "[blobs]"; for b in asm/p1137_*.blob; do echo "\"$(basename $b)\" = \"$(shasum -a 256 $b | cut -d' ' -f1)\""; done
} > "$DS/env.toml"
echo "## health after"; bash ../../health1135.sh 2>&1 | tail -8
exit $RC
