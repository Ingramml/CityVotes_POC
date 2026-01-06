#!/usr/bin/env python3
"""
Simple HTTP server for CityVotes Frontend
Serves static files on port 3000
"""

import http.server
import socketserver
import os
import sys

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP Request Handler with CORS headers"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[Frontend] {self.address_string()} - {args[0]}")


def main():
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           CityVotes POC - Frontend Server                    ║
╠══════════════════════════════════════════════════════════════╣
║  Server running at: http://localhost:{PORT}                    ║
║  Serving files from: {DIRECTORY[:40]}...
║                                                              ║
║  Press Ctrl+C to stop the server                             ║
╚══════════════════════════════════════════════════════════════╝
""")

    print("Make sure the backend API is running on port 8000!")
    print("Start backend with: cd backend && python -m uvicorn api.main:app --reload")
    print()

    with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[Frontend] Server stopped.")
            sys.exit(0)


if __name__ == "__main__":
    main()
