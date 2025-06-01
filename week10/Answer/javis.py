#
# !!! 반드시 pip install sounddevice soundfile 을 진행해주세요.
#

# 반드시 chcp 65001 명령어를 실행한 뒤 테스트해주세요.


"""
사용 방법 :

javis.py {{command}} {{argument}}

ex. 
javis.py record -d 3.0 => 3초동안 녹음 진행
javis.py list --start 20250602 --end 20250603

와 같이 CMD에서 인자와 함께 사용해주세요. IDE의 Run 버튼으로는 동작이 불가능합니다.

사용 가능한 command 목록 : record, list-devices, list 

record argument : 
-d --duration == float 기반 초단위 녹음 설정
-i -device == 사용할 녹음 장치 인덱스 설정(command : list-devices로 인덱스 확인 가능). 미설정 시 기본 장치 사용
--samplerate == 녹음 샘플링 레이트 설정

list-devices argument :
없음.

list argument : 
--start == 시작 일자 YYYYMMDD 또는 YYYY-MM-DD 형식 기입
--end == 종료 일자 YYYYMMDD 또는 YYYY-MM-DD 형식 기입

"""



import os
import sys
import argparse
import datetime
import sounddevice as sd
import soundfile as sf
import numpy as np



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
    # 예: 20250601-235959.wav
    fname = now.strftime('%Y%m%d-%H%M%S') + '.wav'
    return fname


def list_input_devices():
    '''
    시스템에 연결된 모든 오디오 장치를 출력하고, 기본 입력 장치를 표시한다.
    '''
    print('=== 연결된 오디오 장치 ===')
    devices = sd.query_devices()
    default_input = sd.default.device[0]  # (input, output) 형태
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

    # 녹음 장치 설정
    if device_idx is not None:
        sd.default.device = (device_idx, None)  # (input_device, output_device)
    else:
        device_idx = sd.default.device[0]  # 기본 입력 장치 인덱스

    print(f'\n[녹음 시작] 장치 인덱스: {device_idx}, 샘플레이트: '
          f'{samplerate} Hz, 채널: {channels}, 시간: {duration:.1f}초')
    print('녹음 중... Ctrl+C를 눌러서 강제 종료할 수도 있습니다.\n')

    try:
        # duration 초 동안 녹음 (NumPy array 반환)
        recording = sd.rec(int(duration * samplerate),
                           samplerate=samplerate,
                           channels=channels,
                           dtype='int16')
        sd.wait()  # 녹음 완료될 때까지 대기
    except KeyboardInterrupt:
        # 사용자가 Ctrl+C 눌렀을 때
        print('\n[녹음 중단] 사용자가 강제 종료했습니다.')
        # 기록된 데이터가 있으면 저장
        if 'recording' in locals() and recording is not None:
            # 녹음된 길이가 0이 아닌 경우에만 저장
            if recording.shape[0] > 0:
                sf.write(filename, recording, samplerate)
                print(f"[저장 완료] 일부 녹음된 데이터를 '{filename}'에 저장했습니다.")
        return

    # 녹음이 정상적으로 끝난 경우 바로 저장
    sf.write(filename, recording, samplerate)
    print(f"[녹음 완료] '{filename}'에 저장되었습니다.\n")


# ------------------------------------------------------------------------------
# 보너스 과제: 날짜 범위 내의 파일 목록 조회 기능
# ------------------------------------------------------------------------------

def list_recordings(start_date: datetime.date, end_date: datetime.date):
    '''
    records 폴더 내에 있는 파일 중 파일명(YYYYMMDD-HHMMSS.wav)에 포함된 날짜가
    start_date ~ end_date 사이에 속하는 파일을 찾아서 출력한다.

    Args:
        start_date (datetime.date): 조회 시작 날짜 (포함)
        end_date (datetime.date): 조회 종료 날짜 (포함)
    '''
    ensure_records_dir()
    all_files = os.listdir(RECORDS_DIR)
    matched_files = []

    for fname in sorted(all_files):
        # 파일명이 'YYYYMMDD-HHMMSS.wav' 형태인지 확인
        if not fname.lower().endswith('.wav'):
            continue
        date_part = fname.split('-')[0]  # 'YYYYMMDD'
        try:
            file_date = datetime.datetime.strptime(date_part, '%Y%m%d').date()
        except ValueError:
            continue

        if start_date <= file_date <= end_date:
            matched_files.append(fname)

    if matched_files:
        print(f'\n[{start_date} ~ {end_date}] 범위에 속하는 녹음 파일 목록:')
        for f in matched_files:
            print(f'  - {f}')
        print(f'\n총 {len(matched_files)}개 파일이 검색되었습니다.\n')
    else:
        print(f'\n[{start_date} ~ {end_date}] 범위에 속하는 녹음 파일이 없습니다.\n')


# ------------------------------------------------------------------------------
# 메인: argparse로 명령어 파싱
# ------------------------------------------------------------------------------

def main():
    # 커맨드 라인에서 받은 인자를 파싱하는 표준 라이브러리.
    # ArgumentParser.description == 파일에 대한 --help 호출 시 표기하는 설명문
    parser = argparse.ArgumentParser(
        description='시스템 마이크로 녹음하고, 녹음 파일을 날짜별로 조회하는 도구',
        formatter_class=argparse.RawTextHelpFormatter # 도움말 텍스트의 서식을 설정.
    )
    
    # add_subparsers == 이 파일 실행 시, command로 받은 명령어 인자에 따라 다양한 동작 가능함을 설정.
    # 전달받은 인자는 python 내부적으로 command라는 명칭으로 저장
    # ex. javis.py 
    subparsers = parser.add_subparsers(
        dest='command', required=True, help='사용 가능한 명령어'
    )

    # -----------------------------
    # command, 'record' 명령어: 녹음하기
    # -----------------------------
    rec_parser = subparsers.add_parser(
        'record', help='마이크로 음성을 녹음하고 WAV 파일로 저장'
    )
    
    # 파이선에서 command에 대한 argument 명칭 변수가 설정되는 기준은
    # 첫번째로 설정된 --를 기준으로 --를 제외하고 남아있는 -를 _로 변경한 것 기준이다.
    # ex. 만약 --duration-time 식이었다면 파이선에서 접근 시도 시 
    # args = parser.parse_args()
    # ...
    # args.duration_time 과 같은 식으로 할당된 인자값에 접근 가능
    rec_parser.add_argument(
        '-d', '--duration',
        type=float,
        required=True,
        help='녹음 시간(초 단위, 예: 5.0)'
    )
    rec_parser.add_argument(
        '-i', '--device',
        type=int,
        default=None,
        help='녹음에 사용할 오디오 입력 장치 인덱스(미지정 시 기본 장치 사용).\n'
             '장치 인덱스는 \'list-devices\' 명령으로 확인 가능'
    )
    rec_parser.add_argument(
        '--samplerate',
        type=int,
        default=DEFAULT_SAMPLERATE,
        help=f'샘플링 레이트 (기본: {DEFAULT_SAMPLERATE} Hz)'
    )

    # 'list-devices' 명령어: 연결된 오디오 장치 보기
    subparsers.add_parser(
        'list-devices', help='시스템에 연결된 오디오 장치 목록 출력 (녹음 장치 인덱스 확인용)'
    )

    # -----------------------------
    # 'list' 명령어: 날짜 범위 내 녹음 파일 조회 (보너스)
    # -----------------------------
    list_parser = subparsers.add_parser(
        'list', help='특정 날짜 범위 내의 녹음 파일 목록을 보여줍니다.'
    )
    list_parser.add_argument(
        '--start',
        type=parse_date_string,
        required=True,
        help='조회 시작 날짜. \'YYYYMMDD\' 또는 \'YYYY-MM-DD\' 형식'
    )
    list_parser.add_argument(
        '--end',
        type=parse_date_string,
        required=True,
        help='조회 종료 날짜. \'YYYYMMDD\' 또는 \'YYYY-MM-DD\' 형식'
    )

    args = parser.parse_args()

    if args.command == 'list-devices':
        # 오디오 장치 목록 출력
        list_input_devices()
        sys.exit(0)

    elif args.command == 'record':
        # 녹음 수행
        record_audio(duration=args.duration,
                     device_idx=args.device,
                     samplerate=args.samplerate)
        sys.exit(0)

    elif args.command == 'list':
        # 날짜 범위 내 파일 조회
        if args.start > args.end:
            print('오류: 시작 날짜가 종료 날짜보다 이후일 수 없습니다.')
            sys.exit(1)
        list_recordings(start_date=args.start, end_date=args.end)
        sys.exit(0)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    print("BASE_DIR =", BASE_DIR)
    print("RECORDS_DIR =", RECORDS_DIR)
    main()
