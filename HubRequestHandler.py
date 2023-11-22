from http.server import SimpleHTTPRequestHandler

class HubRequestHandler(SimpleHTTPRequestHandler): # SimpleHTTPRequestHandler를 상속받아 HubRequestHandler 클래스를 구현
    def do_GET(self):
        pass