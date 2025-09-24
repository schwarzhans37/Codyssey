#!/usr/bin/env python3
'''
javis.py
────────
① 녹음
    python javis.py               # q + 엔터까지 무한 녹음
    python javis.py -d 5          # 5초 녹음
② 날짜 범위 목록 보기
    python javis.py --list 20240501 20240531
③ STT → CSV (보너스+새 과제)
    python javis.py --stt 20240501 20240531
       ↳ records/YYYYMMDD-HHMMSS.csv 생성
'''

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import pathlib
import queue
import sys
import threading
import wave
from typing import Final, List, Optional, Tuple

# ── 외부 라이브러리 ───────────────────────────────────────────────────────────
#  1) 녹음용
try:
    import sounddevice as _sd  # type: ignore
except ModuleNotFoundError:
    _sd = None  # type: ignore
#  2) STT용  (pip install SpeechRecognition)
try:
    import speech_recognition as sr  # type: ignore
except ModuleNotFoundError:
    sr = None  # type: ignore
# ──────────────────────────────────────────────────────────────────────────────

# ── 상수 ───────────────────────────────────────────────────────────────────────
RECORDS_DIR: Final = pathlib.Path('records')
SAMPLE_RATE:  Final = 44_100
CHANNELS:     Final = 1
BLOCK_SIZE:   Final = 1_024
CHUNK_SEC:    Final = 10  # STT 시 10초 단위로 자름
_AUDIO_Q:     queue.Queue[bytes] = queue.Queue()
# ──────────────────────────────────────────────────────────────────────────────


# ──────────────── 공통 유틸 ───────────────────────────────────────────────────
def _ensure_records_dir() -> None:
    RECORDS_DIR.mkdir(parents=True, exist_ok=True)


def _timestamp_filename() -> pathlib.Path:
    now = _dt.datetime.now().strftime('%Y%m%d-%H%M%S')
    return RECORDS_DIR / f'{now}.wav'


def _parse_filename_datetime(path: pathlib.Path) -> Optional[_dt.datetime]:
    try:
        return _dt.datetime.strptime(path.stem, '%Y%m%d-%H%M%S')
    except ValueError:
        return None
# ──────────────────────────────────────────────────────────────────────────────


# ──────────────── 녹음 기능 ───────────────────────────────────────────────────
def _stdin_watcher(stop_event: threading.Event) -> None:
    for line in sys.stdin:
        if line.strip().lower() == 'q':
            stop_event.set()
            break


def record_audio(duration: Optional[int]) -> pathlib.Path:
    if _sd is None:
        raise RuntimeError('pip install sounddevice 로 녹음 라이브러리를 먼저 설치해 줘!')

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
# ──────────────────────────────────────────────────────────────────────────────


# ──────────────── 날짜 범위 기능 ──────────────────────────────────────────────
def _date_range(start_str: str, end_str: str) -> Tuple[_dt.datetime, _dt.datetime]:
    try:
        d0 = _dt.datetime.strptime(start_str, '%Y%m%d')
        d1 = _dt.datetime.strptime(end_str, '%Y%m%d') + _dt.timedelta(days=1)
    except ValueError as exc:
        raise ValueError('날짜는 YYYYMMDD 형식!') from exc
    if d0 >= d1:
        raise ValueError('시작일은 종료일보다 앞서야 해!')
    return d0, d1


def files_in_range(start_str: str, end_str: str) -> List[pathlib.Path]:
    d0, d1 = _date_range(start_str, end_str)
    if not RECORDS_DIR.exists():
        return []
    wavs = [
        p for p in RECORDS_DIR.glob('*.wav')
        if (ts := _parse_filename_datetime(p)) and d0 <= ts < d1
    ]
    wavs.sort()
    return wavs


def print_file_list(wavs: List[pathlib.Path]) -> None:
    if not wavs:
        print('해당 범위에 WAV가 없어요!')
        return
    print(f'📂 WAV 파일 {len(wavs)}개:')
    for p in wavs:
        print(f'  • {p.name:20}  ({p.stat().st_size // 1024:,} KB)')
# ──────────────────────────────────────────────────────────────────────────────


# ──────────────── STT → CSV 기능 ─────────────────────────────────────────────
def _wav_duration_sec(path: pathlib.Path) -> float:
    with wave.open(str(path), 'rb') as w:
        return w.getnframes() / w.getframerate()


def _write_csv(path: pathlib.Path, rows: List[Tuple[float, str]]) -> None:
    csv_path = path.with_suffix('.csv')
    with csv_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(('time_sec', 'text'))
        writer.writerows(rows)
    print(f'📝 CSV 저장: {csv_path.name}')


def stt_for_file(wav_path: pathlib.Path) -> None:
    if sr is None:
        raise RuntimeError(
            'STT 기능을 쓰려면 pip install SpeechRecognition 로 설치해 줘!'
        )

    recognizer = sr.Recognizer()
    duration = _wav_duration_sec(wav_path)
    rows: List[Tuple[float, str]] = []

    with sr.AudioFile(str(wav_path)) as source:
        offset = 0.0
        while offset < duration:
            audio = recognizer.record(source, duration=CHUNK_SEC)
            try:
                txt = recognizer.recognize_google(audio, language='ko-KR')
                rows.append((offset, txt))
            except sr.UnknownValueError:
                pass  # 인식 실패 구간은 건너뜀
            except sr.RequestError as exc:
                print(f'⚠️  Google STT 요청 오류: {exc}', file=sys.stderr)
                break
            offset += CHUNK_SEC

    if rows:
        _write_csv(wav_path, rows)
    else:
        print(f'😢 인식된 텍스트가 없어서 CSV를 만들지 않았어요: {wav_path.name}')


def stt_for_range(start: str, end: str) -> None:
    wavs = files_in_range(start, end)
    if not wavs:
        print('변환할 WAV가 없어요!')
        return
    print_file_list(wavs)
    for p in wavs:
        stt_for_file(p)
# ──────────────────────────────────────────────────────────────────────────────


# ──────────────── CLI ────────────────────────────────────────────────────────
def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='녹음 • 파일 목록 • STT 변환 유틸리티',
    )
    parser.add_argument(
        '-d', '--duration',
        type=int,
        metavar='SEC',
        help='녹음 시간(초). 없으면 q + 엔터까지 무제한 녹음',
    )
    parser.add_argument(
        '--list',
        nargs=2,
        metavar=('START', 'END'),
        help='날짜 범위 WAV 목록 (YYYYMMDD YYYYMMDD)',
    )
    parser.add_argument(
        '--stt',
        nargs=2,
        metavar=('START', 'END'),
        help='날짜 범위 WAV → CSV 변환 (YYYYMMDD YYYYMMDD)',
    )
    return parser.parse_args(argv)
# ──────────────────────────────────────────────────────────────────────────────


def main() -> None:
    args = parse_args()

    # 1) STT 모드
    if args.stt is not None:
        start, end = args.stt
        try:
            stt_for_range(start, end)
        except Exception as exc:  # pylint: disable=broad-except
            print(f'⚠️  STT 오류: {exc}', file=sys.stderr)
            sys.exit(1)
        return

    # 2) 목록 모드
    if args.list is not None:
        start, end = args.list
        try:
            print_file_list(files_in_range(start, end))
        except Exception as exc:  # pylint: disable=broad-except
            print(f'⚠️  오류: {exc}', file=sys.stderr)
            sys.exit(1)
        return

    # 3) 녹음 모드
    try:
        record_audio(args.duration)
    except Exception as exc:  # pylint: disable=broad-except
        print(f'⚠️  녹음 오류: {exc}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
