# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# Run srvinit under the harness at the REV1 layout and with only the page directory moved;
# keep each run's dump and log and its decoded init info.
set -eu
LIBS=${RESGX545_CDV_LIBS:-$HOME/resgx545-uk/lib}
for lib in libsrv_um libsrv_init; do
    [ -e "$LIBS/$lib.so.1.7.862890" ] || {
        echo "init-payload.sh: $LIBS/$lib.so.1.7.862890 not found;" \
            "set RESGX545_CDV_LIBS to the usr/lib/ directory of your Cedarview package" >&2
        exit 1
    }
done
gcc -m32 -shared -fPIC fakedrm.c -o fakedrm.so -ldl
gcc -m32 loader.c -o loader -ldl
run() {
    name=$1
    shift
    stage=$PWD/stage-$name
    rm -rf "$stage"
    mkdir -p "$stage/lib"
    for lib in libsrv_um libsrv_init; do
        ln -sf "$LIBS/$lib.so.1.7.862890" "$stage/lib/$lib.so.1.7.862890"
        ln -sf "$lib.so.1.7.862890" "$stage/lib/$lib.so"
    done
    env SGX_UK_DIR="$stage" "$@" LD_LIBRARY_PATH="$stage/lib" LD_PRELOAD=./fakedrm.so \
        ./loader > "$OUT/$name.log" 2>&1
    mkdir -p "$OUT/$name"
    cp "$stage"/dump/* "$stage/drm.log" "$OUT/$name/"
    python3 initinfo.py "$OUT/$name/devinitpart2_in.bin" > "$OUT/$name/initinfo.txt"
    echo "$name: $(ls "$OUT/$name" | wc -l) files"
}
# sgx545-ce sgxconfig.h, the *_REV1 bases: kernel code, kernel data, pixel and vertex
# shaders, PDS pixel code and data
run layout_rev1 MOCK_HEAP_BASE_2=0x30000000 MOCK_HEAP_BASE_3=0x32000000 \
    MOCK_HEAP_BASE_4=0x37000000 MOCK_HEAP_BASE_5=0x3C000000 MOCK_HEAP_BASE_6=0x2E000000
run layout_pd_only MOCK_PDPADDR=0x2345000
