#!/bin/bash
set -eu
cd "$(dirname "$0")/.."
w=build/canvas
c=${CHEOLLIAN_PORT:-$HOME/Projects/semtle/semtle-project/cheollian/HmjePort}
llvm=$(em-config LLVM_ROOT)
python3 "$c/web/fix_ir.py" "$w/app.ll" "$w/app32.ll"
python3 web/canvas_entry.py "$w/app32.ll" "$("$llvm/clang" -dumpversion)"
python3 web/relocations.py "$w/app32.ll"
python3 web/abi.py "$w/app32.ll"
python3 web/indices.py "$w/app32.ll"
if [ -x "$llvm/opt" ] && [ -x "$llvm/llc" ]; then
    "$llvm/opt" -passes='function(mem2reg,sroa,simplifycfg),coro-early,cgscc(coro-split),coro-cleanup' "$w/app32.ll" -o "$w/game.bc"
    "$llvm/llc" -O2 -mtriple=wasm32-unknown-emscripten -mattr=+atomics,+bulk-memory,+mutable-globals -filetype=obj "$w/game.bc" -o "$w/game.o"
else
    emcc -O1 -pthread -Wno-override-module -c "$w/app32.ll" -o "$w/game.o"
fi
bash web/canvas-link.sh
