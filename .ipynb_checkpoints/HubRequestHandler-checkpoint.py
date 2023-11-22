from http.server import SimpleHTTPRequestHandler

class HubRequestHandler(SimpleHTTPRequestHandler): # SimpleHTTPRequestHandler를 상속받아 HubRequestHandler 클래스를 구현
    def do_GET(self):
        print(self.path)
        if self.path == '/': self.writeHome() # 홈
    def writeHead(self, nStatus): # response의 header
        self.send_response(nStatus)
        self.send_header('content-type', 'text/html') # 속성(attribute), 값 순으로 입력
        self.end_headers()
    def writeHtml(self, html):
        self.wfile.write(html.encode()) # html(유니코드) -> 바이트로 변경(encode() 함수 역할)
    def writeHome(self): # 홈용 HTLM을 쓰기
        self.writeHead(200) # 200: 성공
        html = '<html><head>'
        html += '<meta http-equiv="content-type" content="text/html" charset="UTF-8">'
        html += '<title>Python Web Server</title>'
        html += '</head><body>'
        html += '<div><p><h1>Hello, world!</hl></p>'
        html += '<p><h6>작성자: 조용희</h6></p></div>'
        html += '<div><img src="https://upload.wikimedia.org/wikipedia/commons/e/ee/Mokwon-university.jpg"></div>'
        html += '</body></html>'
        self.writeHtml(html)





