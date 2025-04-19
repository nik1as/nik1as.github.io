#!/usr/bin/env python3

import sys
from urllib.parse import urljoin
from http.server import HTTPServer, BaseHTTPRequestHandler

if len(sys.argv) - 1 != 2:
    print(f"Usage: {sys.argv[0]} <port> <url>")
    sys.exit()


class Redirect(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(302)
        self.send_header("Location", urljoin(sys.argv[2], self.path))
        self.end_headers()


HTTPServer(("", int(sys.argv[1])), Redirect).serve_forever()
