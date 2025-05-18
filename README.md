import zipfile
import time

def unlock_zip():
charset = 'abcdefghijklmnopqrstuvwxyz0123456789'
attempt_count = 0
start_time = time.time()

    print(f'암호 해제 시작... 시작 시간: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))}')

    try:
        with zipfile.ZipFile('emergency_storage_key.zip', 'r') as zf:
            for c1 in charset:
                for c2 in charset:
                    for c3 in charset:
                        for c4 in charset:
                            for c5 in charset:
                                for c6 in charset:
                                    password = c1 + c2 + c3 + c4 + c5 + c6
                                    attempt_count += 1

                                    if attempt_count % 5000000 == 0:
                                        elapsed = time.time() - start_time
                                        print(
                                            f'[{attempt_count}회차] 시도 중... 경과 시간: {elapsed:.2f}초'
                                        )

                                    try:
                                        zf.extractall(pwd=password.encode('utf-8'))
                                        with open('password.txt', 'w') as f:
                                            f.write(password)
                                        elapsed = time.time() - start_time
                                        print(f'성공! 비밀번호: {password}')
                                        print(f'총 시도 횟수(=그동안의 반복 횟수): {attempt_count}')
                                        print(f'총 소요 시간(=진행 시간)): {elapsed:.2f}초')
                                        return
                                    except Exception:
                                        continue
        print('실패: 비밀번호를 찾을 수 없습니다.')
    except FileNotFoundError:
        print('오류: zip 파일이 존재하지 않습니다.')
    except zipfile.BadZipFile:
        print('오류: 올바른 zip 파일이 아닙니다.')
    except Exception as e:
        print(f'예상치 못한 오류 발생: {e}')

if **name** == '**main**':
unlock_zip()
