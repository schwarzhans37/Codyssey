import http.server
import socketserver
import datetime
import json
import urllib.request

# 서버의 포트 번호를 상수로 정의
PORT = 8080

class MyHttpRequestHandler(http.server.BaseHTTPRequestHandler):
    """
    HTTP 요청을 처리하는 커스텀 핸들러 클래스.
    BaseHTTPRequestHandler를 상속받아 GET 요청을 처리합니다.
    """
    def do_GET(self):
        """
        클라이언트로부터 GET 요청을 받았을 때 호출되는 메서드.
        """
        # 7-1) 접속 시간 기록
        access_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 7-2) 접속한 클라이언트의 IP 주소 기록
        client_ip = self.client_address[0]
        
        # 7. 서버 쪽에 접속 정보 출력
        print(f'접속 시간: {access_time}')
        print(f'클라이언트 IP 주소: {client_ip}')

        # 보너스 과제: 접속 IP 기반 위치 정보 확인
        self.get_location_from_ip(client_ip)
        print('-' * 40)

        # 요청 경로가 루트('/')일 경우 index.html을 제공
        if self.path == '/':
            try:
                # 6. index.html 파일의 내용을 읽기
                with open('index.html', 'rb') as file:
                    content = file.read()
                
                # 4. 성공 응답 (200) 헤더 전송
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                # 6. 읽어온 파일 내용을 클라이언트에게 전송
                self.wfile.write(content)

            except FileNotFoundError:
                # 파일을 찾을 수 없을 때 404 에러 응답
                self.send_error(404, 'File Not Found: index.html')
        else:
            # 다른 경로 요청 시 404 에러 응답
            self.send_error(404, f'File Not Found: {self.path}')

    def get_location_from_ip(self, ip_address):
        """
        IP 주소를 기반으로 위치 정보를 조회하고 출력하는 함수. (보너스 과제)
        """
        # 로컬호스트 등 사설 IP의 경우 조회하지 않음
        if ip_address == '127.0.0.1' or ip_address.startswith('192.168.'):
            print('위치 정보: 로컬 또는 사설 IP 주소입니다.')
            return

        # 외부 API를 사용하여 위치 정보 조회 (별도 라이브러리 없이 기본 기능만 사용)
        try:
            api_url = f'http://ip-api.com/json/{ip_address}'
            with urllib.request.urlopen(api_url) as response:
                data = json.loads(response.read().decode())
                
                if data['status'] == 'success':
                    country = data.get('country', 'N/A')
                    city = data.get('city', 'N/A')
                    isp = data.get('isp', 'N/A')
                    print(f'위치 정보: {country}, {city}')
                    print(f'ISP 정보: {isp}')
                else:
                    print('위치 정보를 조회하지 못했습니다.')

        except Exception as e:
            print(f'위치 정보 조회 중 오류 발생: {e}')
            

def run_server():
    """
    서버를 실행하는 함수.
    """
    # 1. HTTP 통신을 담당할 서버 객체 생성
    # 3. 8080 포트 사용
    with socketserver.TCPServer(('', PORT), MyHttpRequestHandler) as httpd:
        print(f'서버가 {PORT} 포트에서 실행 중입니다...')
        print('웹 브라우저에서 http://localhost:8080 으로 접속하세요.')
        
        # 서버가 종료될 때까지 계속 요청을 처리
        httpd.serve_forever()

if __name__ == '__main__':
    run_server()