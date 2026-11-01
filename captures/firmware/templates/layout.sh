# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# Run srvinit under the harness at the base and the moved layout; keep each run's dump and log.
# Needs a Linux host with 32-bit gcc (gcc -m32) and the closed Cedarview libraries.
set -eu
LIBS=${RESGX545_CDV_LIBS:-$HOME/resgx545-uk/lib}
for lib in libsrv_um libsrv_init; do
    [ -e "$LIBS/$lib.so.1.7.862890" ] || {
        echo "layout.sh: $LIBS/$lib.so.1.7.862890 not found;" \
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
    echo "$name: $(ls "$OUT/$name" | wc -l) files"
}
run layout_base
run layout_moved MOCK_HEAP_START=0x5000 MOCK_PDPADDR=0x2345000 MOCK_HEAP_BASE_2=0xE8100000 \
    MOCK_HEAP_BASE_3=0xF0100000 MOCK_HEAP_BASE_4=0xF4100000 MOCK_HEAP_BASE_5=0xFC100000 \
    MOCK_HEAP_BASE_6=0xE4100000
