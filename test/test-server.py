import http.server

class Handler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        for i in ['GET', 'POST', 'PATCH', 'DELETE', 'HEAD', 'PUT']:
            setattr(self, f'do_{i}', lambda : self.resp())
        super().__init__(*args, **kwargs)

    def resp(self):
        self.send_response(200)
        self.end_headers()

    def handle(self):
        super().handle()
        print(f"PATH: \n\t{self.command} {self.path}")
        print(f"HEADERS: \n")
        for i in self.headers:
            print(f"\t{i}: {self.headers[i]}")
        print()

        if 'Content-Length' in self.headers and (content_len := int(self.headers['Content-Length'])) > 0:
            body = self.rfile.read(content_len)
            print(f"BODY: \n\t{str(body, encoding='utf-8')}")
        print('-' * 60)
        print("\n")

    def do_GET(self):
        self.send_response(200, "Hello world")

if __name__ == "__main__":
    server_address = ('', 8080)
    httpd = http.server.HTTPServer(server_address, Handler)
    httpd.serve_forever()
