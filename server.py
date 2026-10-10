import http.server
import socketserver
import os
import sys
import webbrowser

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, format, *args):
        # Print clean logs
        print(f"[{self.log_date_time_string()}] {format % args}")

def run_server(port=PORT):
    # Try port or increment if busy
    current_port = port
    for _ in range(10):
        try:
            with socketserver.TCPServer(("", current_port), Handler) as httpd:
                url = f"http://localhost:{current_port}"
                print(f"==================================================")
                print(f" Mathematic @ Rudra (www.mathematic@rudra.com) ")
                print(f" Local Web Server Running Successfully! ")
                print(f" URL: {url}")
                print(f" Directory: {DIRECTORY}")
                print(f" Press Ctrl+C to stop the server.")
                print(f"==================================================")
                # Open browser
                webbrowser.open(url)
                httpd.serve_forever()
                break
        except OSError:
            print(f"Port {current_port} is in use, trying {current_port + 1}...")
            current_port += 1

if __name__ == "__main__":
    port_arg = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run_server(port_arg)
