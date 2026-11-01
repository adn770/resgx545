# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# Run the closed OpenVG stack under the harness (fakedrm.so, libpvrFAKEWSEGL.so, xfer) once
# per line of transfer_runs.txt; keep, per run, the bridge-log lines tqcapture.py reads
# (bridge.txt), xfer's output, the MOCK_* variables (env.txt) and each SGX_SUBMITTRANSFER
# snapshot trimmed to what its chain of programs touches (tqcapture.py trim).
# Needs a Linux host with 32-bit gcc (gcc -m32), python3 and the closed Cedarview usr/lib
# (libsrv_um, libsrv_init, libEGL, libIMGegl, libOpenVG and what they load).
set -eu
LIBS=${RESGX545_CDV_LIBS:-$HOME/resgx545-uk/lib}
for lib in libsrv_um.so.1.7.862890 libsrv_init.so.1.7.862890 libEGL.so.1 libOpenVG.so.1; do
    [ -e "$LIBS/$lib" ] || {
        echo "transfer.sh: $LIBS/$lib not found;" \
            "set RESGX545_CDV_LIBS to the usr/lib/ directory of your Cedarview package" >&2
        exit 1
    }
done
here=$PWD
mkdir -p stage/lib
for f in "$LIBS"/*; do ln -sf "$f" stage/lib/; done
ln -sf libsrv_um.so.1.7.862890 stage/lib/libsrv_um.so
ln -sf libsrv_init.so.1.7.862890 stage/lib/libsrv_init.so
gcc -m32 -shared -fPIC fakedrm.c -o fakedrm.so -ldl
gcc -m32 -shared -fPIC fakewsegl.c -o stage/lib/libpvrFAKEWSEGL.so
gcc -m32 loader.c -o loader -ldl
gcc -m32 xfer.c -o xfer -ldl
# srvinit once, for the init info the client stack reads back (fakedrm.c, devinit.bin)
mkdir -p init
ln -sfn "$here/stage/lib" init/lib
SGX_UK_DIR=$here/init LD_LIBRARY_PATH=$here/stage/lib LD_PRELOAD=./fakedrm.so ./loader \
    > init.log 2>&1
cp init/dump/devinitpart2_in.bin stage/devinit.bin
printf '[default]\nWindowSystem=libpvrFAKEWSEGL.so\n' > stage/powervr.ini
grep -v '^[[:space:]]*\(#\|$\)' transfer_runs.txt | while read -r name words; do
    d=$here/run-$name
    rm -rf "$d"
    mkdir -p "$d" "$OUT/$name"
    ln -sfn "$here/stage/lib" "$d/lib"
    cp stage/devinit.bin stage/powervr.ini "$d/"
    envs=
    steps=
    for w in $words; do
        case $w in
            MOCK_*=*) envs="$envs $w" ;;
            *) steps="$steps $w" ;;
        esac
    done
    : > "$OUT/$name/env.txt"
    for e in $envs; do printf '%s\n' "$e" >> "$OUT/$name/env.txt"; done
    # shellcheck disable=SC2086  # the variables and steps are separate words
    env $envs SGX_UK_DIR="$d" LD_LIBRARY_PATH="$here/stage/lib" LD_PRELOAD=./fakedrm.so \
        ./xfer $steps > "$OUT/$name/xfer.out" 2>&1
    grep -E '^====|SUBMITTRANSFER|hCCBMemInfo|SharedCmdCCBOffset|\[respond\] ALLOC' \
        "$d/drm.log" > "$OUT/$name/bridge.txt"
    mkdir -p "$OUT/$name/dump3d"
    for x in "$d"/dump3d/xfer*; do cp -r "$x" "$OUT/$name/dump3d/"; done
    python3 tqcapture.py trim "$OUT/$name"
    echo "$name: $(ls "$OUT/$name/dump3d" | grep -c '_in.bin') transfers"
done
