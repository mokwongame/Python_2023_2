from http.server import SimpleHTTPRequestHandler
import time

class HubRequestHandler(SimpleHTTPRequestHandler): # SimpleHTTPRequestHandler를 상속받아 HubRequestHandler 클래스를 구현
    def do_GET(self):
        print(self.path)
        if self.path == '/': self.writeHome() # 홈
        elif self.path == '/meas_one_volt': self.writeMeasOneVolt()
        else: self.writeNotFound() # 페이지가 없음
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
    def writeNotFound(self):
        self.writeHead(404) # 404: not found
        html = '<html><head>'
        html += '<meta http-equiv="content-type" content="text/html" charset="UTF-8">'
        html += '<title>페이지 없음</title>'
        html += '</head><body>'
        html += f'<div><h3>{self.path}에 대한 페이지는 존재하지 않습니다.</h3></div>'
        html += '</body></html>'
        self.writeHtml(html)
    def writeMeasOneVolt(self):
        self.writeHead(200) # 200: 성공
        nTime = time.time()
        bResult = self.server.gateway.insertOneVoltTable() # gateway == PythonHub의 인스턴스
        if bResult: sResult = '성공'
        else: sResult = '실패'
        html = '<html><head>'
        html += '<meta http-equiv="content-type" content="text/html" charset="UTF-8">'
        html += '<title>전압 한 번 측정</title>'
        html += '</head><body>'
        html += f'<div><h5>측정 시간: {time.ctime(nTime)}</h5></div>'
        html += f'<div>전압 측정이 {sResult}했습니다.</div>'
        html += '</body></html>'
        self.writeHtml(html)



    





