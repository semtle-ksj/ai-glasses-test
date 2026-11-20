#!/usr/bin/env python3
"""Build and run the HMJE game rules tests."""
import pathlib
import subprocess
import sys
import tempfile

from build import compiler

root = pathlib.Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix="ninja-core-") as directory:
    source = pathlib.Path(directory) / "tests.hmje"
    binary = source.with_suffix("")
    subprocess.run([sys.executable, root / "scripts/prepare.py", source, root / "Tests/Core.hmje"], check=True)
    compilation = subprocess.run(
        [compiler(), "--target", "posix-host-exe", source, "-o", binary],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    if compilation.returncode:
        sys.exit(compilation.stdout)
    result = subprocess.check_output([binary], text=True)
    print(result, end="")
    sys.exit(0 if "FAILURES=0" in result.splitlines() else 1)
