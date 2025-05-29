#!/usr/bin/env python3
'''
javis.py
────────
1) 시스템 마이크 녹음 → records/<YYYYMMDD-HHMMSS>.wav 저장
   · `python javis.py -d 10`  → 10초 녹음
   · `python javis.py`        → 'q' 입력(엔터 포함)까지 녹음
2) **보너스 기능**  : 날짜 범위의 녹음 파일 목록 출력
   · `python javis.py --list 20240501 20240515`
'''

from __future__ import annotations

import argparse
import datetime as _dt
import pathlib
import queue
import sys
import threading
import wave
from typing import Final, List, Optional

# ── 외부 라이브러리 (녹음 전용) ────────────────────────────────────────────────
try:
    import sounddevice as _sd  # type: ignore
except ModuleNotFoundError:  # 녹음 안 할 땐 없어도 무방
    _sd = None  # type: ignore
# ──────────────────────────────────────────────────────────────────────────────

RECORDS_DIR: Final = pathlib.Path('records')
SAMPLE_RATE: Final = 44_100
CHANNELS:   Final = 1
BLOCK_SIZE: Final = 1_024

_AUDIO_Q: queue.Queue[bytes] = queue.Queue()


# ───────────────────────────── 보조 함수 ───────────────────────────────────────
def _ensure_records_dir() -> None:
    RECORDS_DIR.mkdir(parents=True, exist_ok=True)


def _timestamp_filename() -> pathlib.Path:
    now = _dt.datetime.now().strftime('%Y%m%d-%H%M%S')
    return RECORDS_DIR / f'{now}.wav'


def _parse_filename_datetime(path: pathlib.Path) -> Optional[_dt.datetime]:
    '''
    파일 이름이 YYYYMMDD-HHMMSS.wav 형식이면 datetime 객체를 반환,
    아니면 None.
    '''
    try:
        stem = path.stem  # 'YYYYMMDD-HHMMSS'
        return _dt.datetime.strptime(stem, '%Y%m%d-%H%M%S')
    except ValueError:
        return None


def _stdin_watcher(stop_event: threading.Event) -> None:
    '''표준 입력에서 q(엔터) 감지 → stop_event set'''
    for line in sys.stdin:
        if line.strip().lower() == 'q':
            stop_event.set()
            break


# ───────────────────────────── 녹음 관련 ───────────────────────────────────────
def record_audio(duration: Optional[int]) -> pathlib.Path:
    '''
    duration 지정 → 고정 길이 녹음,
    None → 'q' 입력까지 무한 녹음
    '''
    if _sd is None:
        raise RuntimeError('녹음을 위해 sounddevice를 설치해 줘! (pip install sounddevice)')

    if duration is not None and duration <= 0:
        raise ValueError('duration은 1 이상이어야 해!')

    _ensure_records_dir()
    outfile = _timestamp_filename()

    stop_event = threading.Event()
    if duration is None:
        threading.Thread(target=_stdin_watcher, args=(stop_event,), daemon=True).start()
        print("녹음 중… 종료하려면 q + 엔터!")

    def _callback(indata, frames, time, status):  # type: ignore
        if status:
            print(f'⚠️  {status}', file=sys.stderr)
        _AUDIO_Q.put(bytes(indata))

    with _sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype='int16',
        blocksize=BLOCK_SIZE,
        callback=_callback,
    ):
        print('🎙️  녹음 시작!')
        if duration is not None:
            _sd.sleep(int(duration * 1000))
        else:
            while not stop_event.is_set():
                _sd.sleep(200)

    print('🛑  녹음 종료, 저장 중…')
    with wave.open(str(outfile), 'wb') as wav_f:
        wav_f.setnchannels(CHANNELS)
        wav_f.setsampwidth(2)
        wav_f.setframerate(SAMPLE_RATE)
        while not _AUDIO_Q.empty():
            wav_f.writeframes(_AUDIO_Q.get_nowait())

    print(f'💾  저장 완료: {outfile.resolve()}')
    return outfile


# ──────────────────────────── 보너스 기능 ───────────────────────────────────────
def list_recordings(start_str: str, end_str: str) -> List[pathlib.Path]:
    '''
    records 폴더에서 날짜 범위 [start, end] 에 포함되는 파일 목록 반환
    날짜 형식은 YYYYMMDD
    '''
    try:
        date_start = _dt.datetime.strptime(start_str, '%Y%m%d')
        date_end   = _dt.datetime.strptime(end_str,   '%Y%m%d') + _dt.timedelta(days=1)
    except ValueError as exc:
        raise ValueError('날짜 형식은 YYYYMMDD 로 입력해 줘!') from exc

    if date_start >= date_end:
        raise ValueError('시작일은 종료일보다 앞서야 해!')

    if not RECORDS_DIR.exists():
        print('(records 폴더가 아직 없어요)')
        return []

    result: List[pathlib.Path] = []
    for wav_path in RECORDS_DIR.glob('*.wav'):
        ts = _parse_filename_datetime(wav_path)
        if ts and date_start <= ts < date_end:
            result.append(wav_path)

    result.sort()
    return result


def _print_file_list(files: List[pathlib.Path]) -> None:
    if not files:
        print('해당 범위에 녹음 파일이 없어요!')
    else:
        print(f'📂 찾은 파일 {len(files)}개:')
        for p in files:
            size_kb = p.stat().st_size // 1024
            print(f'  • {p.name:20}  ({size_kb:,} KB)')


# ───────────────────────────── CLI 파싱 ────────────────────────────────────────
def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='시스템 마이크 녹음 및 녹음 파일 관리 유틸리티',
    )
    parser.add_argument(
        '-d', '--duration',
        type=int,
        metavar='SEC',
        help='녹음 시간(초). 미지정 시 q 입력까지 무제한 녹음',
    )
    parser.add_argument(
        '--list',
        nargs=2,
        metavar=('START', 'END'),
        help='날짜 범위의 파일 목록 출력 (형식: YYYYMMDD YYYYMMDD)',
    )
    return parser.parse_args(argv)


# ────────────────────────────── main ──────────────────────────────────────────
def main() -> None:
    args = parse_args()

    # 1. 날짜 목록 모드
    if args.list is not None:
        start, end = args.list
        try:
            files = list_recordings(start, end)
            _print_file_list(files)
        except Exception as exc:  # pylint: disable=broad-except
            print(f'⚠️  오류: {exc}', file=sys.stderr)
            sys.exit(1)
        return

    # 2. 녹음 모드
    try:
        record_audio(args.duration)
    except Exception as exc:  # pylint: disable=broad-except
        print(f'⚠️  오류: {exc}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
