#!/bin/bash
set -eu
cd "$(dirname "$0")/.."
w=build/canvas
out=$w/dist
mkdir -p "$out/fonts"
c=${CHEOLLIAN_PORT:-$HOME/Projects/semtle/semtle-project/cheollian/HmjePort}
tool=$(dirname "$(realpath "${HMJEC:-$(cat .local/toolchain.txt)}")")/../platforms/tools/targets
emcc -O2 -pthread -c "$tool/async_host_runtime.c" -o "$w/async.o"
emcc -O2 -pthread -c web/platform.c -o "$w/platform.o"
emcc -O2 -pthread "$w/game.o" "$w/platform.o" "$w/async.o" "$c/build/web/shim.o" "$c/build/web/w32.o" "$c/build/web/cc.o" \
 --no-entry -Wl,--wrap=clock_gettime -sALLOW_MEMORY_GROWTH -sINITIAL_MEMORY=33554432 -sSTACK_SIZE=4194304 \
 -sEXPORTED_FUNCTIONS=_hmje_app_main,_game_init,_game_frame,_game_key,_game_pointer,_game_bake,_malloc,_free -sDEFAULT_LIBRARY_FUNCS_TO_INCLUDE=\$UTF8ToString \
 -sEXPORTED_RUNTIME_METHODS=HEAPU8,HEAPF32,HEAPF64,UTF8ToString -sENVIRONMENT=web,worker --js-library web/canvas-library.js --preload-file Resources/fonts@/bundle/fonts --pre-js web/canvas-host.js -o "$out/app.js"
cp Resources/fonts/OFL.txt "$out/fonts/"
rm -f "$out/fonts"/NotoSansKR{,-Bold}.ttf{,.gz}
cp web/canvas.html "$out/index.html"
cp web/share.{js,css} web/share-art.jpg web/share-qr.png "$out/"
for file in "$out"/app.{js,wasm,data}; do gzip -9 -c "$file" > "$file.gz"; done
