#!/bin/bash
set -eu
cd "$(dirname "$0")/.."
c=${CHEOLLIAN_PORT:-$HOME/Projects/semtle/semtle-project/cheollian/HmjePort}
w=build/web
out=$w/dist
mkdir -p "$out"
emcc -pthread -O2 -c web/platform.c -o "$w/platform.o"
objs=()
for o in shim cc vault push w32 web_host; do objs+=("$c/build/web/$o.o"); done
targets=$(dirname "$(realpath "${HMJEC:-$(cat .local/toolchain.txt)}")")/../platforms/tools/targets
emcc -O2 -pthread -c "$targets/async_host_runtime.c" -o "$w/async.o"
emcc -O1 -pthread "$w/async.o" "${GAME_OBJECT:-$w/small.o}" "$w/platform.o" "${objs[@]}" -Wl,--wrap=clock_gettime -o "$out/app.js" \
 -sPROXY_TO_PTHREAD -sOFFSCREENCANVAS_SUPPORT=1 '-sOFFSCREENCANVASES_TO_PTHREAD=#hmje-dummy' \
 -sFULL_ES3 -sUSE_WEBGL2 -sMIN_WEBGL_VERSION=2 -sMAX_WEBGL_VERSION=2 -sALLOW_MEMORY_GROWTH \
 -sINITIAL_MEMORY=67108864 -sMAXIMUM_MEMORY=2147483648 -sPTHREAD_POOL_SIZE=3 -sSTACK_SIZE=2097152 \
 -sDEFAULT_PTHREAD_STACK_SIZE=2097152 -sENVIRONMENT=web,worker -sEXPORTED_RUNTIME_METHODS=HEAPU8,HEAPF32,UTF8ToString \
 --pre-js web/host.js --preload-file Resources@/bundle
cp web/index.html "$out/"

for asset in app.wasm app.js app.data; do gzip -9 -c "$out/$asset" > "$out/$asset.gz"; done
