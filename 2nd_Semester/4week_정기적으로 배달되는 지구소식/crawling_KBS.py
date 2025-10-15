# -*- coding: utf-8 -*-

"""
crawling_KBS.py (최종 제출본)

[메인 과제]
- KBS 뉴스 헤드라인을 수집하는 객체 지향 크롤러 실행

[보너스 과제]
- 네이버 뉴스 메인 페이지의 정적 영역(주요뉴스, 속보 등) 헤드라인을 수집
"""

import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# ==============================================================================
# 1. 메인 과제: KBS 뉴스 크롤러 클래스 (변경 없음)
# ==============================================================================
class KBSNewsCrawler:
    """
    KBS 뉴스 웹사이트를 크롤링하여 주요 헤드라인과 링크를 추출하는 클래스.
    """
    def __init__(self):
        self.root_url = 'https://news.kbs.co.kr'
        self.target_url = 'https://news.kbs.co.kr/news/pc/main/main.html'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.selectors = [
            'p.title',
            'div.headline-title > a',
        ]

    def fetch_html(self):
        try:
            response = requests.get(self.target_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f'[ERROR] KBS 페이지 로딩 실패: {e}', file=sys.stderr)
            return None

    def parse_headlines(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        headlines_data = []
        seen_titles = set()

        for selector in self.selectors:
            elements = soup.select(selector)
            for el in elements:
                title = ' '.join(el.get_text().split())
                if len(title) < 5 or title in seen_titles:
                    continue
                link_node = el if el.name == 'a' else el.find_parent('a')
                if link_node and link_node.has_attr('href'):
                    link = urljoin(self.root_url, link_node['href'])
                else:
                    link = 'N/A'
                seen_titles.add(title)
                headlines_data.append({'title': title, 'link': link})
            if headlines_data:
                print(f"[INFO] KBS: '{selector}' 셀렉터로 {len(headlines_data)}개 헤드라인 발견.")
                break
        return headlines_data

    def run(self):
        print(f'[INFO] KBS 크롤링 시작: {self.target_url}')
        html = self.fetch_html()
        return self.parse_headlines(html) if html else []

# ==============================================================================
# 2. 보너스 과제: 네이버 뉴스 크롤러 클래스 (셀렉터 수정됨)
# ==============================================================================
class NaverNewsCrawler:
    """
    네이버 뉴스 메인에서 정적 영역 기사를 크롤링하는 클래스.
    """
    def __init__(self):
        self.root_url = 'https://news.naver.com'
        self.target_url = 'https://news.naver.com/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # [!!! 핵심 수정 부분 !!!]
        # 직접 제공해주신 '페이지 소스'를 기반으로 가장 정확한 셀렉터 목록을 재구성.
        self.selectors = [
            # 1순위: 언론사별 메인 뉴스 제목 (strong 태그)
            'strong.cnf_news_title',
            # 2순위: 언론사별 목록 뉴스 (a 태그)
            'a.cnf_news',
            # 3순위: 상단 속보 뉴스 (a 태그)
            'a.cjs_nf_a'
        ]

    def fetch_html(self):
        try:
            response = requests.get(self.target_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f'[ERROR] Naver 페이지 로딩 실패: {e}', file=sys.stderr)
            return None

    def parse_headlines(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        headlines_data = []
        seen_titles = set()
        
        # 이제 여러 종류의 헤드라인을 모두 수집하기 위해 break 없이 순회
        all_elements = []
        for selector in self.selectors:
            elements = soup.select(selector)
            if elements:
                print(f"[INFO] Naver: '{selector}' 셀렉터로 {len(elements)}개 요소 발견.")
                all_elements.extend(elements)
        
        for el in all_elements:
            title = ' '.join(el.get_text().split())
            if not title or len(title) < 5 or title in seen_titles:
                continue
            
            # strong 태그를 선택했더라도 부모 a 태그에서 링크를 찾아야 함
            link_node = el if el.name == 'a' else el.find_parent('a')
            if link_node and link_node.has_attr('href'):
                link = urljoin(self.root_url, link_node['href'])
            else:
                continue # 링크가 없는 경우는 기사로 취급하지 않음

            seen_titles.add(title)
            headlines_data.append({'title': title, 'link': link})
            
        return headlines_data

    def run(self):
        print(f'[INFO] Naver 크롤링 시작: {self.target_url}')
        html = self.fetch_html()
        return self.parse_headlines(html) if html else []

# ==============================================================================
# 3. 결과 출력 및 메인 실행 로직
# ==============================================================================
def display_results(title, headlines):
    """수집된 헤드라인 데이터를 보기 좋게 출력하는 공통 함수."""
    print(f'\n=== {title} ===')
    if not headlines:
        print('-> 헤드라인을 찾지 못했습니다.')
        return
    for i, data in enumerate(headlines, 1):
        print(f"{i:02d}. {data['title']}")
        print(f"   ㄴ 링크: {data['link']}")

if __name__ == '__main__':
    # --- 메인 과제 수행 ---
    kbs_crawler = KBSNewsCrawler()
    kbs_results = kbs_crawler.run()
    display_results("KBS 주요 헤드라인 (메인 과제)", kbs_results)

    print("\n" + "-"*60 + "\n") # 과제 구분을 위한 라인

    # --- 보너스 과제 수행 ---
    naver_crawler = NaverNewsCrawler()
    naver_results = naver_crawler.run()
    display_results("네이버 뉴스 헤드라인 (보너스 과제)", naver_results)