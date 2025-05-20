import os
import zipfile
import itertools
import string
import time
import contextlib
import multiprocessing
import queue 
import zlib   


def print_progress(total, progress_q, found_event):
    last_update = time.time()
    counts = {}

    # found_event 가 set 되면 즉시 빠져나오도록 while 조건 수정
    while not found_event.is_set():
        try:
            pid, cnt = progress_q.get(timeout=0.5)
            counts[pid] = cnt
        except queue.Empty:   # ← multiprocessing.queues.Empty → queue.Empty
            pass

        if time.time() - last_update >= 1:
            tried = sum(counts.values())
            print(f"\r⏳ 진행 중... {tried:,}/{total:,} 시도", end="", flush=True)
            last_update = time.time()


def try_password_range(start, end, zip_path, chars,
                       progress_q, found_q, found_event, pid):
    with zipfile.ZipFile(zip_path, 'r') as zf:
        for offset, tpl in enumerate(
                itertools.islice(itertools.product(chars, repeat=6),
                                 start, end)):
            if found_event.is_set():
                break

            pwd = ''.join(tpl)
            try:
                with contextlib.redirect_stderr(None):
                    zf.extractall(pwd=pwd.encode())

                # 성공 시
                found_q.put(pwd)
                found_event.set()
                break

            # zlib.error 를 추가해서 압축 해제 실패 예외도 잡아야 함
            except (RuntimeError, zipfile.BadZipFile, zlib.error):
                pass

            idx = start + offset + 1
            if idx % 1000 == 0:
                progress_q.put((pid, idx))


def unlock_zip():
    start_time = time.time()
    zip_path = 'emergency_storage_key.zip'
    pw_file = 'password.txt'

    # 1) ZIP 파일 존재 체크
    if not os.path.isfile(zip_path):
        print(f"❌ 압축 파일이 없어요: {zip_path}")
        return
    print(f"✅ 압축 파일 확인됨: {zip_path}")

    chars = string.ascii_lowercase + string.digits
    total = len(chars) ** 6
    cpu = multiprocessing.cpu_count()

    print(f"🔎 총 {total:,}개 조합 시도 (코어 {cpu}개 사용)")

    mgr = multiprocessing.Manager()
    progress_q = mgr.Queue()
    found_q = mgr.Queue()
    found_event = multiprocessing.Event()

    # 워커별 범위 나누기
    chunk = total // cpu
    ranges = [(i * chunk, (i + 1) * chunk) for i in range(cpu)]
    ranges[-1] = (ranges[-1][0], total)

    workers = []
    for i, (s, e) in enumerate(ranges):
        p = multiprocessing.Process(
            target=try_password_range,
            args=(s, e, zip_path, chars,
                  progress_q, found_q, found_event, i)
        )
        p.start()
        workers.append(p)

    # 진행 상황 표시 프로세스
    prog_proc = multiprocessing.Process(
        target=print_progress,
        args=(total, progress_q, found_event)
    )
    prog_proc.start()

    # ——— 대기: 찾거나 모든 워커 종료 시 ———
    while True:
        if found_event.is_set():
            break
        if all(not p.is_alive() for p in workers):
            break
        time.sleep(0.1)

    # 남은 워커들 강제 종료
    for p in workers:
        if p.is_alive():
            p.terminate()
    prog_proc.terminate()

    # 종료 시간 출력
    elapsed = time.time() - start_time
    print(f"\n⏰ 소요 시간: {elapsed:.2f}초")

    # 2) 성공 여부 확인 & 파일 기록
    if not found_q.empty():
        password = found_q.get()
        with open(pw_file, 'w') as f:
            f.write(password)
        print(f"🔓 암호 찾음! password.txt 에 저장됨: {password}")
    else:
        print("❌ 암호를 못 찾았어요…")

if __name__ == '__main__':
    unlock_zip()
