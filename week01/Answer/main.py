# 
# 파이썬에는 CPython, JPython, Pypy 등의 다양한 파이썬이 존재한다. 필자는 Cpython을 설치했으며, 3.9.12 버전임을 알림.
# 파이썬 개발도구로 VS code 선택하였음. 기능적 사유보다는 편의성 위함.
#

logFileName = 'mission_computer_main.log' # 로그파일 명칭 설정
directory = __file__[:-7] # 작업 영역 및 실행 파일 위치에 구애받지 않도록 현재 main.py가 위치한 경로를 직접적으로 따오기

#
# 로그메시지를 split하여 각 내용을 저장해두기 위한 class
#
class logMessage :
    def __init__(self, line) :
        logLine = line.split(',')
        self.timeStamp = logLine[0]  # line을 split한 결과 내부의 타임스탬프 양식을 추출.
        self.event = logLine[1]
        self.message = logLine[2]
    
    # isPrint라는 항목 설정해둬서, 필요할 경우 읽어온 내용 즉시 프린트 가능하게 설정
    # 반복문 안에서 따로 print 귀찮아.. 여따가 해놓기.
    def printMessage(self, isPrint=None) :
        lineRebuilded = ', '.join([self.timeStamp, self.event, self.message])
        if isPrint == True :
            print(lineRebuilded, end='')
        return lineRebuilded


# 로그 파일을 읽고, 객체형식으로 리스트 내에 저장.
def readAndPrintLogFile(lineInstanceList) :
    with open(directory + logFileName, 'rt', encoding = 'UTF-8') as logFile : # 텍스트 파일이므로 t, 파일 자체의 수정이 아닌 파이썬 내 읽기 용도므로 r
        print('\n\n=== 읽어온 로그 파일 내역 출력 ===\n')
        while True : 
            line = logFile.readline() # 전체 내역을 리스트 형식으로 읽어오기
            if line == '' :
                break
            print(line, end='') # 로그파일 내역 한 줄 씩 출력
            lineInstanceList.append(logMessage(line))
        return lineInstanceList

# 로그파일 역순정렬 및 출력
# 출력문 확인이 어려울 경우, reverseSorted_logFile.txt 참조 요망.
def reversSortedLogPrint(lineInstanceList) :
    print('\n\n=== 로그파일의 출력 결과를 역순으로 정렬후 출력 ===\n')
    lineInstanceList.sort(reverse=True, key=lambda obj : obj.timeStamp)
    
    with open(directory + 'reverseSorted_logFile.txt', 'wt', encoding = 'UTF-8') as reverseLogFile : 
        for logInstance in lineInstanceList : 
            reverseLogFile.write(logInstance.printMessage(True))

# 문제의 소지가 되는 내역을 별도로 추출(추가과제2)하고 이를 기반으로 보고서를 작성(메인과제)한다. 
def writeReport(lineInstanceList) :
    badKeywordList = ['fail', 'unstable', 'explosion'] # 실패를 의미하거나 문제가 될만한 단어들 작성... event가 왜 다 INFO인거지
    badLineStrList = [] # str이 저장되는 리스트임을 유의.
    
    with open(directory + 'log_analysis.md', 'wt', encoding = 'UTF-8') as report : # 보고서 파일을 UTF-8로 만들기
        for badKeyword in badKeywordList :
            for line in lineInstanceList :
                if badKeyword in line.message:
                    badLineStrList.append(line.printMessage())
                
        report.write('## 로그 기반 분석\n') # 파일 서두 부문 작성
        report.write(' * 로그 확인 결과, 화성을 향해 발사된 우주선은 정상적으로 착륙하여 미션에 성공하였음.\n')
        report.write(' * 그러나, 미션 성공 약 5분 후, 산소 탱크에 이상징후가 발생했음을 아래 로그들로 확인 가능/\n')
        report.write('```\n')
        for badLine in badLineStrList :
            report.write(badLine)
        report.write('```\n')
        report.write(' * 최종적으로 산소탱크 폭발에 의해 화성기지에 심각한 피해 발생.\n')
        report.write(' * 어째서 일어났는지에 대한 내역은 로그를 통해 확인 불가.\n')
        
        report.write('## 분석 사견\n') # 파일 서두 부문 작성
        report.write(' * 산소 탱크의 폭발 등, 문제가 될 수 있는 로그의 event가 모두 INFO로 처리되고 있는 시스템 상태로 보아, 관리 미숙으로 인한 인재일 가능성이 있음.\n')





def main() :
    lineInstanceList = []
    
    try : 
        print('Hello Mars') # 정상 출력 확인
        print(__file__)
        
        # 로그 파일 내역 읽어오고 출력도 수행
        lineInstanceList = readAndPrintLogFile(lineInstanceList)
        writeReport(lineInstanceList)
        reversSortedLogPrint(lineInstanceList)
        
    except NameError as e :
        print(e.__class__.__name__ + ' :: 해당 명칭의 변수가 존재하는지 확인해주세요.')
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


if __name__ == '__main__' :
    main()