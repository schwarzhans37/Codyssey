# -*- coding: utf-8 -*-

# [라이브러리 임포트]
# requests: 웹 서버에 HTTP 요청을 보내고 HTML 응답을 받기 위한 라이브러리.
# BeautifulSoup: requests로 받은 HTML 문서를 파싱(parsing)하여,
#                원하는 데이터를 쉽게 추출할 수 있도록 도와주는 라이브러리.
import requests
from bs4 import BeautifulSoup

def get_kbs_headlines():
    """
    KBS 뉴스 웹사이트의 최종 콘텐츠 페이지에 접속하여 헤드라인 뉴스를 추출하는 함수.
    """
    
    # [1. URL 정의 및 자바스크립트 리다이렉션 처리]
    # 초기 접속 주소('https://news.kbs.co.kr')는 실제 뉴스 내용이 없는 자바스크립트 코드만 반환함.
    # 해당 스크립트는 접속 환경(PC/모바일)을 감지해 최종 뉴스 페이지로 리다이렉션(재이동) 시킴.
    # requests는 자바스크립트를 실행하지 못하므로, 분석을 통해 확인된 최종 PC용 URL로 직접 접속.
    url = 'https://news.kbs.co.kr/news/pc/main/main.html'
    
    # [2. 봇 차단 회피용 헤더 구성]
    # 웹 서버는 비정상적인 프로그램(봇)의 접근을 막기 위해 요청 헤더를 검사할 수 있음.
    # 'User-Agent'는 클라이언트(접속자)의 브라우저, OS 등의 정보를 담고 있음.
    # 이 값을 실제 웹 브라우저의 값처럼 설정하여, 서버가 정상적인 사용자의 접속으로 인식하게 함.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # [3. Request 라이브러리 사용]
        # requests.get() 함수를 통해 지정된 url에 HTTP GET 요청을 전송.
        # headers 인자를 통해 위에서 정의한 User-Agent 정보를 요청에 포함시킴.
        # 서버로부터의 응답은 response 객체에 저장됨.
        response = requests.get(url, headers=headers)
        
        # HTTP 응답 상태 코드가 200(성공)이 아닌 경우, 예외를 발생시켜 에러 처리.
        response.raise_for_status()
        
        # [4. BeautifulSoup의 parsing 절차]
        # response.text : 서버로부터 받은 응답의 HTML 코드 전체 (순수 텍스트).
        # BeautifulSoup(HTML텍스트, '파서종류') : 순수 텍스트인 HTML 코드를
        # 파이썬이 다룰 수 있는 객체(DOM, Document Object Model) 구조로 변환(파싱)함.
        # 이제 'soup' 객체를 통해 HTML 태그에 계층적으로 접근 가능.
        soup = BeautifulSoup(response.text, 'html.parser')
        
        headline_list = []
        
        # [5. BeautifulSoup의 select 절차와 CSS 선택자]
        # soup.select('CSS선택자') : 파싱된 HTML DOM 구조에서
        # 'CSS 선택자' 문법에 일치하는 모든 요소를 리스트 형태로 찾아 반환.
        #
        # ※ CSS 선택자 사용법 예시:
        #   - 'p': 모든 <p> 태그 선택.
        #   - '.title': class가 'title'인 모든 요소 선택.
        #   - 'p.title': <p> 태그 중 class가 'title'인 요소 선택 (현재 코드에서 사용).
        #   - '#main': id가 'main'인 요소 선택.
        #   - 'div a': <div>의 자손인 모든 <a> 태그 선택.
        #   - 'a[href*="news"]': <a> 태그 중 href 속성값에 'news'라는 문자열이 "포함된" 모든 요소 선택.
        #                        특정 링크 패턴을 가진 요소를 찾을 때 매우 유용.
        headlines = soup.select('p.title')

        # select로 찾은 요소들(뉴스 제목 태그)을 순회.
        for headline in headlines:
            # [6. BeautifulSoup의 get_text 절차]
            # headline은 아직 <p class="title">...</p> 형태의 태그 객체임.
            # .get_text() : 태그를 제외하고 안에 있는 순수 텍스트 내용만 추출.
            # .strip() : 추출된 텍스트의 양쪽 끝에 있는 불필요한 공백이나 줄바꿈 문자를 제거.
            title = headline.get_text().strip()
            
            # 비어있지 않은 제목만 리스트에 추가.
            if title:
                headline_list.append(title)
        
        return headline_list

    # requests 라이브러리 사용 중 발생할 수 있는 네트워크 관련 예외(연결 실패 등)를 처리.
    except requests.exceptions.RequestException as e:
        print(f'웹사이트 접근 중 에러 발생: {e}')
        return []

# 이 스크립트 파일이 직접 실행될 때만 아래 코드를 동작시키도록 하는 파이썬의 표준적인 구문.
if __name__ == '__main__':
    kbs_news_headlines = get_kbs_headlines()

    # 함수가 성공적으로 헤드라인 리스트를 반환한 경우.
    if kbs_news_headlines:
        print('KBS 뉴스 헤드라인:')
        # enumerate()를 사용하여 리스트의 인덱스와 값을 함께 가져와 번호를 붙여 출력.
        for index, title in enumerate(kbs_news_headlines, 1):
            print(f'{index}. {title}')
    # 빈 리스트가 반환되는 등 실패한 경우.
    else:
        print('헤드라인 뉴스를 가져오는데 실패했습니다.')