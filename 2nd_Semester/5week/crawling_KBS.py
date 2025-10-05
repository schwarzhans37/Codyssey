import os
import sys
import time
from typing import List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

try:
    from webdriver_manager.chrome import ChromeDriverManager
    USE_WDM = True
except Exception:
    USE_WDM = False

NAVER_HOME = 'https://www.naver.com/'
NAVER_LOGIN = 'https://nid.naver.com/nidlogin.login'
NAVER_MAIL  = 'https://mail.naver.com/'
DEBUG = False

# --------------------------
# 브라우저 빌더
# --------------------------
def build_driver(headless: bool = False) -> webdriver.Chrome:
    opts = Options()
    if headless:
        opts.add_argument('--headless=new')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--disable-software-rasterizer')
    opts.add_argument('--window-size=1280,900')
    opts.add_experimental_option('excludeSwitches', ['enable-automation'])
    opts.add_experimental_option('useAutomationExtension', False)

    if USE_WDM:
        service = Service(ChromeDriverManager().install())
    else:
        service = Service()

    driver = webdriver.Chrome(service=service, options=opts)
    try:
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': "Object.defineProperty(navigator,'webdriver',{get:()=>undefined});"
        })
    except Exception:
        pass
    return driver

# --------------------------
# 로그인 전/후 콘텐츠 샘플
# --------------------------
def get_home_teasers(driver: webdriver.Chrome, limit: int = 10) -> List[str]:
    driver.get(NAVER_HOME)
    wait = WebDriverWait(driver, 10)
    texts: List[str] = []
    try:
        cards = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, 'a[aria-label*="뉴스"], a[aria-label*="기사"], a[href*="news.naver.com"]')
            )
        )
        for a in cards:
            t = a.text.strip()
            if t and len(t) >= 6:
                texts.append(t)
                if len(texts) >= limit:
                    return texts
    except Exception:
        pass
    try:
        for el in driver.find_elements(By.CSS_SELECTOR, 'h3, h4, strong'):
            t = el.text.strip()
            if t and len(t) >= 6:
                texts.append(t)
                if len(texts) >= limit:
                    break
    except Exception:
        pass
    seen = set(); out = []
    for t in texts:
        if t not in seen:
            seen.add(t); out.append(t)
    return out[:limit]

# --------------------------
# 로그인
# --------------------------
def login_naver(driver: webdriver.Chrome, user: str, pw: str) -> bool:
    driver.get(NAVER_LOGIN)
    wait = WebDriverWait(driver, 12)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input#id')))
    try:
        id_box = driver.find_element(By.CSS_SELECTOR, 'input#id')
        pw_box = driver.find_element(By.CSS_SELECTOR, 'input#pw')
    except Exception:
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        found = False
        for f in iframes:
            driver.switch_to.frame(f)
            try:
                id_box = driver.find_element(By.CSS_SELECTOR, 'input#id')
                pw_box = driver.find_element(By.CSS_SELECTOR, 'input#pw')
                found = True
                break
            except Exception:
                driver.switch_to.default_content()
        if not found:
            raise RuntimeError('로그인 입력창을 찾지 못했습니다.')
    id_box.clear(); id_box.send_keys(user)
    pw_box.clear(); pw_box.send_keys(pw)
    pw_box.send_keys(Keys.ENTER)
    time.sleep(1.2)
    try:
        WebDriverWait(driver, 15).until(
            EC.any_of(
                EC.url_contains('www.naver.com'),
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="mail.naver.com"], a[href*="mail"]'))
            )
        )
        return True
    except Exception:
        print('추가 인증(캡차/OTP 등)이 필요합니다. 인증 완료 후 콘솔에 Enter.')
        input('… 인증 완료했으면 Enter: ')
        try:
            WebDriverWait(driver, 8).until(
                EC.any_of(
                    EC.url_contains('www.naver.com'),
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="mail.naver.com"], a[href*="mail"]'))
                )
            )
            return True
        except Exception:
            return False
    finally:
        try:
            driver.switch_to.default_content()
        except Exception:
            pass

# --------------------------
# 로그인 후 개인화 영역 샘플
# --------------------------
def crawl_logged_only_content(driver: webdriver.Chrome, limit: int = 10) -> List[str]:
    driver.get(NAVER_HOME)
    time.sleep(1.0)
    texts: List[str] = []
    selectors = [
        'a[href*="news.naver.com"], a[aria-label*="뉴스"]',
        'h3, h4, strong'
    ]
    for sel in selectors:
        try:
            for el in driver.find_elements(By.CSS_SELECTOR, sel):
                t = el.text.strip()
                if t and len(t) >= 6:
                    texts.append(t)
                    if len(texts) >= limit:
                        break
        except Exception:
            continue
        if len(texts) >= limit:
            break
    seen = set(); out = []
    for t in texts:
        if t not in seen:
            seen.add(t); out.append(t)
    return out[:limit]

# --------------------------
# 메일 제목 수집 (수정된 함수)
# --------------------------
def get_mail_subjects(driver: webdriver.Chrome, limit: int = 20) -> List[str]:
    """네이버 메일 페이지에서 메일 제목 목록을 수집합니다."""
    driver.get(NAVER_MAIL)
    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body')))
    time.sleep(1.5)

    def scrape_titles_from_context() -> List[str]:
        """현재 브라우저 컨텍스트(메인 페이지 또는 iframe)에서 제목을 스크랩합니다."""
        titles = []
        # 사용자께서 제공한 스크린샷과 HTML 구조를 기반으로 가장 정확한 선택자를 사용합니다.
        # 'li.mail_item'은 각 메일 항목을 의미하며, 그 안의 'a.mail_title_link'가 제목 링크입니다.
        # 이 조합은 UI의 다른 텍스트 요소를 배제하고 제목만 정확히 타겟팅합니다.
        selectors = [
            'li.mail_item a.mail_title_link',
            'li.mail-item a.mail_title_link',
            'strong.mail_title'
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elements:
                    title = el.text.strip()
                    if title:
                        titles.append(title)
                if titles:
                    return titles
            except Exception:
                continue
        return titles

    subjects = scrape_titles_from_context()

    if not subjects:
        try:
            iframes = driver.find_elements(By.TAG_NAME, 'iframe')
            for frame in iframes:
                try:
                    driver.switch_to.frame(frame)
                    subjects = scrape_titles_from_context()
                    driver.switch_to.default_content()
                    if subjects:
                        break
                except Exception:
                    try:
                        driver.switch_to.default_content()
                    except Exception:
                        pass
        except Exception:
            pass

    unique_subjects = []
    seen_titles = set()
    for title in subjects:
        if title not in seen_titles:
            unique_subjects.append(title)
            seen_titles.add(title)
        if len(unique_subjects) >= limit:
            break
            
    return unique_subjects

# --------------------------
# 메인
# --------------------------
def main():
    user = os.environ.get('NAVER_ID', '').strip()
    pw   = os.environ.get('NAVER_PW', '').strip()
    if not user or not pw:
        print('환경변수 NAVER_ID / NAVER_PW 를 설정하세요.')
        sys.exit(1)

    driver = build_driver(headless=False)
    try:
        anon_samples = get_home_teasers(driver, limit=8)
        print('=== 로그인 전(샘플) ===')
        if anon_samples:
            for i, t in enumerate(anon_samples, 1):
                print(f'{i:02d}. {t}')
        else:
            print('로그인 전 샘플 수집 실패')

        ok = login_naver(driver, user, pw)
        if not ok:
            print('로그인 실패(캡차/2FA 미통과 또는 요소 변경).')
            sys.exit(2)
        time.sleep(1.0)

        logged_samples = crawl_logged_only_content(driver, limit=8)
        print('\n=== 로그인 후(샘플) ===')
        if logged_samples:
            for i, t in enumerate(logged_samples, 1):
                print(f'{i:02d}. {t}')
        else:
            print('로그인 후 샘플 수집 실패')

        subjects = get_mail_subjects(driver, limit=20)
        print('\n=== 네이버 메일 제목들 ===')
        if subjects:
            for i, s in enumerate(subjects, 1):
                print(f'{i:02d}. {s}')
        else:
            print('메일 제목을 찾지 못했습니다(보안/로딩/셀렉터 변경).')

    finally:
        if DEBUG:
            input('\n[DEBUG] 브라우저 닫으려면 Enter: ')
        driver.quit()

if __name__ == '__main__':
    main()