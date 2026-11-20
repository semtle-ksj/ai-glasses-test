"""Serve WASM with the isolation headers needed by pthreads and precompressed assets."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

class GameHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cross-Origin-Opener-Policy','same-origin')
        self.send_header('Cross-Origin-Embedder-Policy','require-corp')
        super().end_headers()

    def send_head(self):
        path=Path(self.translate_path(self.path))
        zipped=path.with_name(path.name+'.gz') if path.name else None
        if zipped and zipped.is_file() and 'gzip' in self.headers.get('Accept-Encoding',''):
            self.send_response(200)
            self.send_header('Content-Type',self.guess_type(str(path)))
            self.send_header('Content-Encoding','gzip')
            self.send_header('Vary','Accept-Encoding')
            self.send_header('Content-Length',str(zipped.stat().st_size))
            self.end_headers()
            return zipped.open('rb')
        return super().send_head()

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--port',type=int,default=51082)
    opts=parser.parse_args()
    root=Path(__file__).resolve().parents[1]/'build/web/dist'
    ThreadingHTTPServer(('127.0.0.1',opts.port),partial(GameHandler,directory=root)).serve_forever()
