#!/bin/bash
set -eu
cd "$(dirname "$0")/.."
project="$PWD/build/canvas"
mkdir -p "$project/src"
compiler=${HMJEC:-$(cat .local/toolchain.txt)}
python3 scripts/prepare.py "$project/src/Game.hmje" --app
python3 web/canvas_source.py "$project/src/Game.hmje"
python3 web/raster_source.py "$project/src/Game.hmje"
sed -e 's|"build/Generated"|"src"|' -e 's|"Resources"|"../../Resources"|' -e 's|"Native"|"../../Native"|' Project.hmjep > "$project/Project.hmjep"
"$compiler" --project "$project" --artifact 중급닌자시험 --target ios-sim-llvm-ir -o "$project/app.ll"
bash web/canvas-compile.sh
python3 web/publish-canvas.py
