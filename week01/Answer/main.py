# 
# 파이썬 개발도구로 VS code 선택
#
    


print('Hello Mars') # 정상 출력 확인


def checkComputer() :
    logValue = ''
    logName = 'mission_computer_main.log'
    directory = 'week01\Answer\\'
    badKeywordList = ['fail', 'unstable', 'explosion'] # 실패를 의미하거나 문제가 될만한 단어들 작성... event가 왜 다 INFO인거지
    
    try : # error 캐치 목적의 try 문
        logFile = open(directory + logName, 'rt', encoding = 'UTF-8') # 텍스트 파일이므로 t, 파일 자체의 수정이 아닌 파이썬 내 읽기 용도므로 r
        report = open(directory + 'log_analysis.md', 'wt', encoding='UTF-8') # 보고서 파일을 UTF-8로 만들기
        report.write('## error issued by ...\n') # 보고서 파일 서두 부문 작성
        
        while True : 
            line = logFile.readline() # 파일을 한 줄씩 읽어온다.
            logValue += line
            
            for badKeyword in badKeywordList :
                if badKeyword in line:
                    report.write(line)
        
            if line == '' :
                break
        
        print(logValue) if len(logValue) != 0 else print('내용 없음') # print하고자 하는 파일이 내용이 없을 경우 명확하게 알기 위한 명시
        
                
        logFile.close() 
        report.close() # 종료. 아래부터는 에러 캐치 내역
    except NameError as e :
        print(' :: 파일 위치 변수 명칭을 확인해주세요.')
        exit()
    except FileNotFoundError as e : 
        print(e.__class__ + ' :: 파일이 없거나, 설정된 경로와 다르거나, 이름이 달라 확인할 수 없습니다.')
        exit()
    except IsADirectoryError as e : 
        print(e.__class__ + ' :: 디렉토리는 파일이 아니므로 열 수 없습니다.')
        exit()
    except PermissionError as e : 
        print(e.__class__ + ' :: 본 계정은 해당 파일에 대한 접근권한이 없으므로, 파일을 열 수 없습니다.')
        exit()
    except MemoryError as e : 
        print(e.__class__ + ' :: 한 번에 처리하기에 너무 큰 파일입니다.')
        exit()
    except EOFError as e : 
        print(e.__class__ + ' :: 이미 파일의 마지막 부분이므로 더이상 읽을 수 없습니다.')
        exit()
            
            
            
checkComputer()