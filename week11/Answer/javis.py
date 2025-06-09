#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# !!! 반드시 pip install sounddevice soundfile SpeechRecognition 을 진행해주세요.
# 반드시 chcp 65001 명령어를 실행한 뒤 테스트해주세요.

"""
사용 방법 :

javis.py {{command}} {{argument}}

ex. 
javis.py record -d 3.0 => 3초동안 녹음 진행
javis.py list --start 20250602 --end 20250603
javis.py transcribe --keyword 안녕 => CSV 내 키워드 검색

CMD에서 인자와 함께 사용해주세요. IDE의 Run 버튼으로는 동작이 불가능합니다.

사용 가능한 command 목록 : record, list-devices, list, transcribe

record argument : 
  -d, --duration   float 기반 초단위 녹음 설정
  -i, --device     사용할 녹음 장치 인덱스 설정(list-devices로 확인). 미설정 시 기본 장치 사용
  --samplerate     녹음 샘플링 레이트 설정

list-devices argument :
  없음

list argument : 
  --start          시작 일자 YYYYMMDD 또는 YYYY-MM-DD 형식
  --end            종료 일자 YYYYMMDD 또는 YYYY-MM-DD 형식

transcribe argument :
  --keyword        CSV 파일 내에서 검색할 키워드 (선택)
"""

import os
import sys
import argparse
import datetime
import csv
import sounddevice as sd
import soundfile as sf
import numpy as np

# STT 기능을 위해 SpeechRecognition이 필요하지만,
# record/list/list-devices 사용 시 없어도 동작하도록 처리
try:
    import speech_recognition as sr
except ImportError:
    sr = None

# ------------------------------------------------------------------------------
# 상수 및 기본 설정
# ------------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECORDS_DIR = os.path.join(BASE_DIR, 'records')  # 녹음 파일을 저장할 폴더 이름
DEFAULT_SAMPLERATE = 44100     # 표준 샘플링 레이트 (Hz)
DEFAULT_CHANNELS = 1           # 모노 녹음

# ------------------------------------------------------------------------------
# 유틸리티 함수
# ------------------------------------------------------------------------------

def ensure_records_dir():
    '''
    'records' 디렉토리가 존재하지 않으면 생성.
    '''
    if not os.path.isdir(RECORDS_DIR):
        os.makedirs(RECORDS_DIR, exist_ok=True)


def get_timestamp_filename():
    '''
    현재 시각을 기준으로 'YYYYMMDD-HHMMSS.wav' 형식의 파일명을 생성하여 반환한다.
    '''
    now = datetime.datetime.now()
    fname = now.strftime('%Y%m%d-%H%M%S') + '.wav'
    return fname


def list_input_devices():
    '''
    시스템에 연결된 모든 오디오 장치를 출력하고, 기본 입력 장치를 표시한다.
    '''
    print('=== 연결된 오디오 장치 ===')
    devices = sd.query_devices()
    default_input = sd.default.device[0]
    for idx, dev in enumerate(devices):
        kind = 'Input' if dev['max_input_channels'] > 0 else 'Output'
        default_mark = ''
        if idx == default_input and kind == 'Input':
            default_mark = '  <-- default input'
        print(f'{idx:>2}: {dev["name"]}  (max_in={dev["max_input_channels"]}, '
              f'max_out={dev["max_output_channels"]}) {kind}{default_mark}')
    print('================================\n')


def parse_date_string(date_str):
    '''
    YYYYMMDD 또는 YYYY-MM-DD 형태의 문자열을 datetime.date 객체로 변환한다.
    '''
    for fmt in ('%Y%m%d', '%Y-%m-%d'):
        try:
            return datetime.datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise argparse.ArgumentTypeError(
        f"잘못된 날짜 형식: '{date_str}'. 'YYYYMMDD' 또는 'YYYY-MM-DD' 형태여야 합니다."
    )

# ------------------------------------------------------------------------------
# 녹음 기능 구현
# ------------------------------------------------------------------------------

def record_audio(duration: float, device_idx: int = None,
                 samplerate: int = DEFAULT_SAMPLERATE):
    '''
    마이크로부터 duration(초)만큼 녹음하여 WAV 파일로 저장한다.

    Args:
        duration (float): 녹음 시간(초)
        device_idx (int, optional): 사용할 오디오 입력 장치 인덱스. None이면 기본 장치.
        samplerate (int): 샘플링 레이트 (Hz)
    '''
    ensure_records_dir()
    filename = os.path.join(RECORDS_DIR, get_timestamp_filename())
    channels = DEFAULT_CHANNELS

    if device_idx is not None:
        sd.default.device = (device_idx, None)
    else:
        device_idx = sd.default.device[0]

    print(f'\n[녹음 시작] 장치 인덱스: {device_idx}, 샘플레이트: '
          f'{samplerate} Hz, 채널: {channels}, 시간: {duration:.1f}초')
    print('녹음 중... Ctrl+C를 눌러서 강제 종료할 수도 있습니다.\n')

    try:
        recording = sd.rec(int(duration * samplerate),
                           samplerate=samplerate,
                           channels=channels,
                           dtype='int16')
        sd.wait()
    except KeyboardInterrupt:
        print('\n[녹음 중단] 사용자가 강제 종료했습니다.')
        if 'recording' in locals() and recording is not None:
            if recording.shape[0] > 0:
                sf.write(filename, recording, samplerate)
                print(f"[저장 완료] 일부 녹음된 데이터를 '{filename}'에 저장했습니다.")
        return

    sf.write(filename, recording, samplerate)
    print(f"[녹음 완료] '{filename}'에 저장되었습니다.\n")

# ------------------------------------------------------------------------------
# 녹음 파일 조회 기능
# ------------------------------------------------------------------------------

def list_recordings(start_date: datetime.date, end_date: datetime.date):
    '''
    records 폴더 내 WAV 파일을 날짜 범위로 필터링하여 출력한다.
    '''
    ensure_records_dir()
    all_files = os.listdir(RECORDS_DIR)
    matched_files = []

    for fname in sorted(all_files):
        if not fname.lower().endswith('.wav'):
            continue
        date_part = fname.split('-')[0]
        try:
            file_date = datetime.datetime.strptime(date_part, '%Y%m%d').date()
        except ValueError:
            continue
        if start_date <= file_date <= end_date:
            matched_files.append(fname)

    if matched_files:
        print(f"\n[{start_date} ~ {end_date}] 범위에 속하는 녹음 파일 목록:")
        for f in matched_files:
            print(f'  - {f}')
        print(f"\n총 {len(matched_files)}개 파일이 검색되었습니다.\n")
    else:
        print(f"\n[{start_date} ~ {end_date}] 범위에 속하는 녹음 파일이 없습니다.\n")

# ------------------------------------------------------------------------------
# STT 및 CSV 저장 기능
# ------------------------------------------------------------------------------

def transcribe_file(wav_path: str):
    '''
    WAV 파일을 읽어 STT 후 동일 이름 CSV로 저장한다.
    '''
    if sr is None:
        print('speech_recognition 모듈이 설치되지 않았습니다. pip install SpeechRecognition 후 다시 시도해주세요.')
        return
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as src:
        audio = recognizer.record(src)
    try:
        text = recognizer.recognize_google(audio, language='ko-KR')
    except sr.UnknownValueError:
        text = ''
    except sr.RequestError as e:
        print(f'STT 요청 오류: {e}')
        return

    csv_name = os.path.splitext(os.path.basename(wav_path))[0] + '.csv'
    csv_path = os.path.join(RECORDS_DIR, csv_name)
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['time', 'text'])
        writer.writerow([0.0, text])
    print(f"[STT] '{wav_path}' -> '{csv_name}' 저장 완료")


def transcribe_all():
    '''
    records 폴더 내 모든 WAV 파일에 대해 STT 처리
    '''
    ensure_records_dir()
    for fname in sorted(os.listdir(RECORDS_DIR)):
        if fname.lower().endswith('.wav'):
            transcribe_file(os.path.join(RECORDS_DIR, fname))


def search_keyword(keyword: str):
    '''
    CSV 파일에서 키워드를 검색하여 결과를 출력
    '''
    ensure_records_dir()
    found = False
    for fname in sorted(os.listdir(RECORDS_DIR)):
        if not fname.lower().endswith('.csv'):
            continue
        csv_path = os.path.join(RECORDS_DIR, fname)
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if keyword in row['text']:
                    print(f"{fname} @ {row['time']}s -> {row['text']}")
                    found = True
    if not found:
        print(f"키워드 '{keyword}' 결과 없음")

# ------------------------------------------------------------------------------
# 메인: argparse로 명령어 파싱
# ------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='시스템 마이크로 녹음하고, 녹음 파일을 날짜별로 조회 및 STT/검색 기능 제공',
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(
        dest='command', required=True, help='사용 가능한 명령어'
    )

    rec_parser = subparsers.add_parser('record', help='녹음 후 WAV 저장')
    rec_parser.add_argument('-d', '--duration', type=float, required=True,
                            help='녹음 시간(초 단위)')
    rec_parser.add_argument('-i', '--device', type=int, default=None,
                            help='녹음에 사용할 입력 장치 인덱스')
    rec_parser.add_argument('--samplerate', type=int, default=DEFAULT_SAMPLERATE,
                            help='샘플링 레이트(Hz)')

    subparsers.add_parser('list-devices', help='오디오 장치 목록 출력')

    list_parser = subparsers.add_parser('list', help='날짜 범위 녹음 파일 조회')
    list_parser.add_argument('--start', type=parse_date_string, required=True,
                             help='시작 날짜 YYYYMMDD 또는 YYYY-MM-DD')
    list_parser.add_argument('--end',       type=parse_date_string, required=True,
                             help='종료 날짜 YYYYMMDD 또는 YYYY-MM-DD')

    trans_parser = subparsers.add_parser('transcribe', help='STT 실행 및 CSV 저장/검색')
    trans_parser.add_argument('--keyword', type=str, default=None,
                              help='CSV 내 검색할 키워드 (선택)')

    args = parser.parse_args()

    if args.command == 'list-devices':
        list_input_devices()
    elif args.command == 'record':
        record_audio(duration=args.duration,
                     device_idx=args.device,
                     samplerate=args.samplerate)
    elif args.command == 'list':
        if args.start > args.end:
            print('오류: 시작 날짜가 종료 날짜보다 이후일 수 없습니다.')
            sys.exit(1)
        list_recordings(start_date=args.start, end_date=args.end)
    elif args.command == 'transcribe':
        if sr is None:
            print('speech_recognition 모듈이 설치되지 않았습니다. pip install SpeechRecognition 후 다시 시도해주세요.')
            sys.exit(1)
        if args.keyword:
            search_keyword(keyword=args.keyword)
        else:
            transcribe_all()
    else:
        parser.print_help()

    sys.exit(0)


if __name__ == '__main__':
    print(f"BASE_DIR = {BASE_DIR}")
    print(f"RECORDS_DIR = {RECORDS_DIR}")
    main()
