# 
# 파이썬에는 CPython, JPython, Pypy 등의 다양한 파이썬이 존재한다. 필자는 Cpython을 설치했으며, 3.9.12 버전임을 알림.
# 파이썬 개발도구로 VS code 선택하였음. 기능적 사유보다는 편의성 위함.
#
    


print('Hello Mars') # 정상 출력 확인


def checkComputer() :
    logValue = ''
    logName = 'mission_computer_main.log'
    directory = 'week01\Answer\\'
    badKeywordList = ['fail', 'unstable', 'explosion'] # 실패를 의미하거나 문제가 될만한 단어들 작성... event가 왜 다 INFO인거지
    reversedLogList = []
    
    try : ### error 캐치 목적의 try 문
        logFile = open(directory + logName, 'rt', encoding = 'UTF-8') # 텍스트 파일이므로 t, 파일 자체의 수정이 아닌 파이썬 내 읽기 용도므로 r
        report = open(directory + 'log_analysis.md', 'wt', encoding = 'UTF-8') # 보고서 파일을 UTF-8로 만들기
        report.write('## error issued by ...\n') # 보고서 파일 서두 부문 작성
        
        logFile.readline() # 첫 줄 건너뛰기 위함
        while True : 
            line = logFile.readline() # 파일을 한 줄씩 읽어온다.
            
            if line == '' :
                break
            
            logValue += line
            
            # 추가과제1을 위한 수행 - 메시지 역순정렬 스택
            reversedLogList.append(logMessage(line))
            
            for badKeyword in badKeywordList :
                if badKeyword in line:
                    report.write(line) # 추가과제2 수행 - 문제가 되는 부분 찾아 파일로 저장
        
        
        print(logValue) if len(logValue) != 0 else print('내용 없음') # print하고자 하는 파일이 내용이 없을 경우 명확하게 알기 위한 명시
        
        
        # 추가과제1 수행 - 메시지 역순정렬 출력
        reversedLogList.sort(reverse=True, key=lambda obj: obj.allMessages) # 리스트 내부의 객체 필드에 접근하기위해 람다 사용
        for instance in reversedLogList :
            print(instance.allMessages, end='')
        
        
        ### 종료구문
        logFile.close() 
        report.close() # 종료. 아래부터는 에러 캐치 내역
    except NameError as e :
        print(' :: 해당 명칭의 변수가 존재하는지 확인해주세요.')
        exit()
    except FileNotFoundError as e : 
        print(e.__class__.__name__ + ' :: 파일이 없거나, 설정된 경로와 다르거나, 이름이 달라 확인할 수 없습니다.')
        exit()
    except IsADirectoryError as e : 
        print(e.__class__.__name__ + ' :: 디렉토리는 파일이 아니므로 열 수 없습니다.')
        exit()
    except PermissionError as e : 
        print(e.__class__.__name__ + ' :: 본 계정은 해당 파일에 대한 접근권한이 없으므로, 파일을 열 수 없습니다.')
        exit()
    except MemoryError as e : 
        print(e.__class__.__name__ + ' :: 한 번에 처리하기에 너무 큰 파일입니다.')
        exit()
    except AttributeError as e : 
        print(e.__class__.__name__ + ' :: 객체 내에 존재하지 않는 속성입니다.')
        exit()
    except EOFError as e : 
        print(e.__class__.__name__ + ' :: 이미 파일의 마지막 부분이므로 더이상 읽을 수 없습니다.')
        exit()
    except Exception as e:
        print(f"Unexpected Exception: {type(e).__name__} => {e}")  
        exit()

    
class logMessage :
    def __init__(self, line) :
        lineTimeStamp = line.split(',')[0] # line을 split한 결과 내부의 타임스탬프 양식을 추출.
        line_YMD = lineTimeStamp.split(' ')[0].split('-') # '-'를 구분자로 하는 연월일 데이터 소유
        line_HMS = lineTimeStamp.split(' ')[1].split(':') # ':'을 구분자로하는 시분초 데이터 소유
        
        self.timeStamp = tuple(line_YMD + line_HMS)# 튜플로 값 저장
        self.allMessages = line # 타임스탬프, 이벤트, 메시지 내역 총괄 str 모두 저장
        print(self.timeStamp)
        print(self.allMessages.rstrip('\n'))
            
checkComputer()