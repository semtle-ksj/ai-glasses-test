"""Switch the local static site to a complete content-versioned browser build."""
import hashlib
import os
from pathlib import Path
import shutil
import tempfile

build = Path(__file__).resolve().parents[1] / "build"
source = build / "canvas/dist"
public = build / "web/dist"
public.mkdir(parents=True, exist_ok=True)
shutil.copyfile(Path(__file__).with_name("_headers"), public / "_headers")
shutil.copyfile(Path(__file__).with_name("share-cover.jpg"), public / "share-cover.jpg")
digest = hashlib.sha256()
for asset in sorted(source.rglob("*")):
    if asset.is_file():
        digest.update(asset.relative_to(source).as_posix().encode())
        digest.update(asset.read_bytes())
version = "canvas-" + digest.hexdigest()[:12]
if not (public / version).exists():
    with tempfile.TemporaryDirectory(dir=public) as temporary:
        staging = Path(temporary) / version
        shutil.copytree(source, staging)
        staging.rename(public / version)
html = (source / "index.html").read_text().replace("<title>", f'<base href="./{version}/"><title>')
with tempfile.NamedTemporaryFile(mode="w", dir=public, delete=False) as index:
    index.write(html)
os.chmod(index.name, 0o644)
os.replace(index.name, public / "index.html")
