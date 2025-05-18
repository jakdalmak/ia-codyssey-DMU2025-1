import io
import zipfile
import time
import zlib
from itertools import product

def brute_force_zip_in_memory(zip_path, charset='abcdefghijklmnopqrstuvwxyz0123456789', length=6):
    # 1) ZIP 전체를 메모리에 읽어 들입니다.
    with open(zip_path, 'rb') as f:
        zip_bytes = f.read()

    # 2) BytesIO 버퍼를 통해 ZipFile 객체 생성
    buf = io.BytesIO(zip_bytes)
    zf = zipfile.ZipFile(buf)

    # 3) 테스트할 내부 파일 이름을 가져옵니다.
    name = zf.namelist()[0]

    start = time.time()
    attempt = 0

    # 4) 모든 조합을 순회하며 비밀번호 검증
    for combo in product(charset, repeat=length):
        pwd = ''.join(combo)
        attempt += 1

        try:
            # 압축 해제 대신 read(1)로 최소 I/O
            data = zf.open(name, pwd=pwd.encode('utf-8')).read(1)
            # 어쩌다 zlib.error 가 아니라도, 데이터가 비어 있으면 실패로 처리
            if data:
                elapsed = time.time() - start
                print(f'\n[SUCCESS] 비밀번호: {pwd}')
                print(f'총 시도 횟수: {attempt}')
                print(f'총 소요 시간: {elapsed:.2f}초')
                return pwd
        except (RuntimeError, zipfile.BadZipFile, zlib.error):
            # 틀린 비밀번호나 압축 해제 오류일 때만 무시
            pass

        # 진행 상황 출력 (예: 100만 회마다)
        if attempt % 1_000_000 == 0:
            elapsed = time.time() - start
            rate = attempt / elapsed
            print(f'[진행] {attempt}회 시도, {elapsed:.1f}s 경과, 속도 {rate:.0f} ops/sec')

    print('비밀번호를 찾지 못했습니다.')
    return None

if __name__ == '__main__':
    brute_force_zip_in_memory('./week08/Answer/emergency_storage_key.zip')
