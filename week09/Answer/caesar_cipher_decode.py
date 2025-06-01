import os

BASE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
PASSWORD_TXT_DIRECTORY = os.path.join(BASE_DIRECTORY, 'password.txt')
RESULT_TXT_DIRECTORY = os.path.join(BASE_DIRECTORY, 'result.txt')

EXPECTED_WORD_DICT = {'i', 'mars', 'moon'} # 실제로는 set으로 구현하지만 '문맥' 상 사전으로 명명함


# !!! ASCII 코드 십진법 범위 순환구조 설명 !!!
#        base   = ord('a')      # 97
#        letter = 'x'           # ord('x') == 120
#        n      = 5             # 오른쪽으로 5칸 이동
#        offset = (ord(letter) - base + n) % 26
#               = (120 - 97 + 5) % 26
#               = (28) % 26
#               = 2
#        print(chr(base + offset))  # chr(97 + 2) == 'c'


def caesar_cipher_decode(target_text) :
    count = 1
    str_no_space_list = list(target_text.strip())
    
    caesar_decode_str_list = []
    # print(str_no_space_list)

    lower_base = ord('a') # 97
    upper_base = ord('A') # 65
    
    while count < 27 : # 영어 26개므로, 25번 바뀌어봐야 한 바퀴 돈 것.
        tempChrList = []
        for i in range(0, len(str_no_space_list)) :
            
            # 공백은 ASCII 10진법으로 다룰 수 없음.
            # 공백을 만나면 그냥 기입하고 continue로 넘어가기
            if str_no_space_list[i] == ' ' :
                tempChrList.append(str_no_space_list[i])
                continue
            
            try : 
                # 지금 다루는 문자가 소문자/대문자 확인하여 이를 기반으로 진행.
                if str_no_space_list[i].islower() :
                    integerASCII = (ord(str_no_space_list[i]) - lower_base + count) % 26 # 아스키 코드 10진값 확인
                    tempChrList.append(chr(lower_base + integerASCII))
                elif str_no_space_list[i].isupper() :
                    integerASCII = (ord(str_no_space_list[i]) - upper_base + count) % 26 # 아스키 코드 10진값 확인
                    tempChrList.append(chr(upper_base + integerASCII))
                else :
                    print('문자 디코딩 불가: 영문자 외 문자가 포함되어 있습니다. 카이사르 암호화 대상은 영문 대/소문자 여야합니다.')
                    os._exit(1)
            except ValueError : 
                print('ValueError 에러 발생 : 암호문은 아스키코드로 변환 가능한 문자여야합니다.')
                os.exit(1)
        caesar_decode_str = ''.join(tempChrList)
        
        caesar_decode_str_list.append(caesar_decode_str)
        
        print(str(count) + ' 번째 시도 : ' + str(caesar_decode_str))
        
        check_word_by_dict = check_and_recommand_by_dictionary(caesar_decode_str)
        if check_word_by_dict != '' :
            print(str(count) + ' 번째 시도에서 검출된 내역에 따라 반복문 종료. 해당 문장을 암호문으로 권장드립니다. : ' + check_word_by_dict)
            break
        
        count += 1
        
    return caesar_decode_str_list


def caesar_chipher_result_save(caesar_decode_str_list, result_index) :
    print(caesar_decode_str_list[result_index])
    
    try :
        with open(RESULT_TXT_DIRECTORY, 'w') as file : 
            file.write(''.join(caesar_decode_str_list[result_index]))
    except FileNotFoundError as e :
        print('대상 파일이 존재하지않습니다. 대상 파일이 본 코드와 동일한 경로에 위치해있는지 확인해주세요.\n{e}')
        os._exit(1)
    except PermissionError as e :
        print('대상 파일에 접근하기위한 권한이 부족합니다. 권한을 확인해주세요.\n{e}')
        os._exit(1)
    except Exception as e :
        print(f"Unexpected Exception: {type(e).__name__} => {e}")
        os._exit(1)

def check_and_recommand_by_dictionary(caesar_decode_str) :
    # 1자리, 4자리, 4자리. 총 9자리로 이루어진 문장에서 나올 수 있는 단어 유추
    # 어디서든 나올수 있는 1자리는 제외하기? == 9자리 str에 대해 contain 검증하는 경우
    # 1자리 짜리 문자도 사전에 포함? == 각 자리별 단어 또는 문자로 구분하기위한 '공백'이 매우 중요해짐.
    
    # => 카이사르 디코드 시 공백을 남겨두는 식으로 구현해두었으므로, 1자리짜리 문자도 사전에 포함 가능.
    
    splited_caesar_decode_str = caesar_decode_str.split(' ')
    
    for caesar_decode_word in splited_caesar_decode_str : 
        if caesar_decode_word.lower() in EXPECTED_WORD_DICT : # # 공백 단위로 구분된 대상 문장의 단어 단위로 체크. 
            # 확인 시에는 대소문자 상관없도록 모두 소문자화. 
            # set은 불변객체므로 모두 소문자로 기입할 것을 유의할 것
            return caesar_decode_word
    return '' 

def main() :
    try :
        with open(PASSWORD_TXT_DIRECTORY, 'r', encoding='UTF-8') as file : 
            original_password = file.readline()
            # print(original_password) # 잘 읽어와지는지 검증
            
            caesar_decode_str_list = caesar_cipher_decode(original_password)
            
            print('\n 위의 카이사르 암호의 복호화 내역 중 암호로 유추되는 회수를 기입해주세요.')
            
            idx = int(input()) - 1
            if not 0 <= idx < len(caesar_decode_str_list):
                print('유효하지 않은 선택입니다.')
                return
                
            caesar_chipher_result_save(caesar_decode_str_list, idx)
    except FileNotFoundError as e :
        print('대상 파일이 존재하지않습니다. 대상 파일이 본 코드와 동일한 경로에 위치해있는지 확인해주세요.\n{e}')
        os._exit(1)
    except PermissionError as e :
        print('대상 파일에 접근하기위한 권한이 부족합니다. 권한을 확인해주세요.\n{e}')
        os._exit(1)
    except Exception as e :
        print(f"Unexpected Exception: {type(e).__name__} => {e}")
        os._exit(1)
    
if __name__ == '__main__' :
    main()