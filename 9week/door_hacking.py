import os
import zipfile
import itertools
import time
from datetime import datetime
import multiprocessing
import zlib

# 스크립트 위치 기준으로 파일 경로 설정
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ZIP_PATH = os.path.join(BASE_DIR, 'emergency_storage_key.zip')  # 대상 ZIP 파일
PASSWORD_FILE = os.path.join(BASE_DIR, 'password.txt')       # 결과 저장 파일

# 암호 후보 생성용 설정
CHARSET = '0123456789abcdefghijklmnopqrstuvwxyz'  # 사용 가능한 문자 집합
LENGTH = 6                                     # 비밀번호 길이
LOG_INTERVAL = 100_000                         # 로그 출력 간격(시도 횟수)
PREFIX_LENGTH = 2                              # 병렬 처리 시 접두사 길이


def log_status(start_time: float, attempts: int) -> None:
    """
    진행 상태를 출력합니다.
    - 시작 시점부터 경과 시간 계산
    - 현재 시도 횟수 출력
    """
    elapsed = time.time() - start_time
    elapsed_str = str(datetime.utcfromtimestamp(elapsed).time())
    print(f"[{datetime.now()}] 시도 #{attempts}: 경과 {elapsed_str}")

def generate_candidates(prefix: str = ''):
    """
    가능한 비밀번호 조합을 생성합니다.
    :param prefix: 사전 지정 접두사 (병렬 처리용)
    :yield: 문자열 비밀번호 후보
    """
    remaining = LENGTH - len(prefix)
    for chars in itertools.product(CHARSET, repeat=remaining):
        yield prefix + ''.join(chars)

def unlock_zip() -> str | None:
    """
    단일 프로세스로 ZIP 파일 암호를 브루트포스로 해제합니다.
    :return: 성공 시 비밀번호, 실패 시 None
    """
    start_time = time.time()
    attempts = 0

    try:
        zf = zipfile.ZipFile(ZIP_PATH)
    except FileNotFoundError:
        raise
    except Exception as e:
        print(f'Error: ZIP 파일 열기 실패 ({e})')
        return None

    with zf:
        for pwd in generate_candidates():
            attempts += 1
            try:
                zf.extractall(pwd=bytes(pwd, 'utf-8'))
                return pwd  # 성공
            except (RuntimeError, zipfile.BadZipFile, zlib.error):
                pass  # 잘못된 비밀번호 예외 무시

            if attempts % LOG_INTERVAL == 0:
                log_status(start_time, attempts)

    return None

def _attempt_prefix(prefix: str) -> str | None:
    """
    주어진 접두사를 기준으로 가능한 모든 조합을 시도합니다.
    :param prefix: 비밀번호 앞부분 문자열
    :return: 성공 시 전체 비밀번호, 실패 시 None
    """
    try:
        zf = zipfile.ZipFile(ZIP_PATH)
    except Exception:
        return None

    with zf:
        for pwd in generate_candidates(prefix):
            try:
                zf.extractall(pwd=bytes(pwd, 'utf-8'))
                return pwd
            except (RuntimeError, zipfile.BadZipFile, zlib.error):
                continue

    return None

def unlock_zip_parallel() -> str | None:
    prefixes = [''.join(p) for p in itertools.product(CHARSET, repeat=PREFIX_LENGTH)]
    total = len(prefixes)
    with multiprocessing.Pool() as pool:
        for count, result in enumerate(pool.imap_unordered(_attempt_prefix, prefixes), start=1):
            # 50개 prefix마다 한 번씩 로그 출력
            if count % 50 == 0 or result:
                print(f'🔄 Prefixs processed: {count}/{total}')
            if result:
                pool.terminate()
                return result
    return None

def main() -> None:
    """
    프로그램 엔트리 포인트
    - 병렬 모드 실행, 실패 시 단일 모드 재시도
    - 결과를 password.txt에 저장
    """
    print('🔐 암호 해제 시작 (병렬 모드)')
    try:
        password = unlock_zip_parallel()
    except FileNotFoundError:
        print(f'Error: ZIP 파일이 없습니다 ({ZIP_PATH})')
        return
    except PermissionError:
        print('Error: 파일 권한 오류')
        return

    if not password:
        print('⚠️ 병렬 모드 실패, 단일 모드로 재시도 중...')
        password = unlock_zip()

    if password:
        with open(PASSWORD_FILE, 'w') as f:
            f.write(password)
        print(f'✅ 성공! 암호: "{password}" (저장: {PASSWORD_FILE})')
    else:
        print('❌ 실패: 암호를 찾지 못했습니다.')

if __name__ == '__main__':
    main()
