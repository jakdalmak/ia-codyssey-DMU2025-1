#
# 내장 모듈의 기준은? => pip install을 통해 별도로 설치해야하는 라이브러리나 패키지가 아닌 것들!
# 텍스트 파일 vs 이진 파일 차이점 : 사람이 읽을 수 있는 문자로 저장 vs 0과 1의 이진수 형식으로 저장
# 
#

import os, sys, csv, struct

BASE_DIRECTORY = os.path.dirname(os.path.abspath(__file__)) # 본 코드가 실행된 파일이 위치한 디렉토리를 절대경로로 추출
CSV_FILE_PATH = os.path.join(BASE_DIRECTORY, 'Mars_Base_Inventory_List.csv') # csv 파일의 위치를 절대경로로 설정
CSV_SAVE_PATH = os.path.join(BASE_DIRECTORY, 'Mars_Base_Inventory_danger.csv') # csv 파일의 위치를 절대경로로 설정
BIN_SAVE_PATH = os.path.join(BASE_DIRECTORY, 'Mars_Base_Inventory_List.bin')


def csvRead() :
    with open(CSV_FILE_PATH, mode = 'r', encoding = 'UTF-8') as file :

        # 내용을 읽어 리스트 객체 변환
        csvReader = csv.DictReader(file)
        dictDataList = list(csvReader) # 딕셔너리를 내부 데이터로 갖는 리스트 완성. [{},{},...,{}]
        
        print('\n\n == csv 파일 읽어 출력 ==')
        for data in dictDataList : 
            print(data)
        
        # 높은순 정렬 수행
        dictDataList.sort(reverse=True, key = lambda dic : dic['Flammability']) 
        return dictDataList
    
def over70Flam(dictDataList) :
    
    # 인화성이 0.7 이상인 값들의 집합을 추출.
    # 컴프리헨션 구문 사용. 쓰니까 편하다.
    over70PerFlamList = [data for data in dictDataList if float(data['Flammability']) >= 0.7]
    
    with open(CSV_SAVE_PATH, 'w', encoding = 'UTF-8', newline = '') as writeFile :
        fieldnames = dictDataList[0].keys() # csv 헤더 값을 설정하기 위한 딕셔너리 내부 키값 추출
        writer = csv.DictWriter(writeFile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(over70PerFlamList)
    
    print('\n\n == 인화성 0.7 이상 목록 출력 ==')
    for over70 in over70PerFlamList :
        print(over70)
    
    return over70PerFlamList

def binarySave(over70PerFlamList) : 
    with open(BIN_SAVE_PATH, 'wb') as writeBinFile :
            fieldnames = over70PerFlamList[0].keys()
            
            writeBinFile.write(len(over70PerFlamList).to_bytes(4, 'little')) # 리스트 내의 딕셔너리 전체 개수를 저장 
            
            for dictionary in over70PerFlamList :
                for field in fieldnames:
                    key_bytes = field.encode('utf-8')
                    value = dictionary[field]

                    # key 저장 - key 자료형은 str 고정이므로 별도의 표기목적 바이트 설정하지 않음!!
                    writeBinFile.write(len(key_bytes).to_bytes(1, 'little'))
                    writeBinFile.write(key_bytes)

                    # value 저장
                    # 문자열인 경우
                    if isinstance(value, str): #isinstance() 메소드 이용하여 변수 자료형 확인
                        writeBinFile.write(b'\x01') # str임을 나타내기위한 표기목적 1바이트
                        val_bytes = value.encode('utf-8')
                        writeBinFile.write(len(val_bytes).to_bytes(1, 'little'))
                        writeBinFile.write(val_bytes)

                    # 숫자 (int/float) 처리
                    elif isinstance(value, int):
                        writeBinFile.write(b'\x02') # int임을 나타내기위한 표기목적 1바이트
                        writeBinFile.write((4).to_bytes(1, 'little'))  # 길이 고정: 4바이트
                        writeBinFile.write(value.to_bytes(4, 'little'))

                    elif isinstance(value, float): 
                        writeBinFile.write(b'\x03') # float임을 나타내기위한 표기목적 1바이트

                        # float 형의 처리를 위해서는 struct가 필요하다.
                        writeBinFile.write((4).to_bytes(1, 'little'))  # 4바이트 float
                        writeBinFile.write(struct.pack('f', value))


def binaryRead(dicCount) :
    dictDataList = []
    
    with open(BIN_SAVE_PATH, "rb") as f:
        listLen = int.from_bytes(f.read(4), 'little') # 읽어올 리스트 내부의 딕셔너리 개수 가져오기
        
        for _ in range(listLen):  # 딕셔너리 개수만큼 반복해야 모든 딕셔너리를 리스트 내에 불러올 수 있다.
            restored_dict = {}

            for _ in range(dicCount): # 딕셔너리의 키 개수는 5개로 고정되어있음.
                value = None # 값 초기화 명시 목적의 None 표기
                
                # key값 읽기
                keyLen = int.from_bytes(f.read(1), 'little')
                key = f.read(keyLen).decode('utf-8')
                
                # value값 자료형 읽기
                valueTypeCode = f.read(1) # 1바이트 단위 읽어옴
                if valueTypeCode == b'\x01' : # str
                    val_len = int.from_bytes(f.read(1), 'little')
                    value = f.read(val_len).decode('utf-8')
                elif valueTypeCode == b'\x02' : # int
                    value = int.from_bytes(f.read(4), 'little')
                elif valueTypeCode == b'\x03' : # float
                    # IEEE 754로 구현된 실수형은 정수나 str에 비해 구조가 복잡하다
                    # ex. 0.99999999999999 == 1과 같은 문제 등
                    # 이를 바이트로 저장하기 위한 내역의 구현은 매우 복잡하고 어렵다고 함.
                    # 이미 안전성과 효율성이 보장된 기본 모듈인 struct의 힘을 빌려 pack, unpack을 수행한다!
                    value = struct.unpack('<f', f.read(4))[0]  # < == endian이 little임을 명시, f == float 형 읽기임을 명시

                restored_dict[key] = value

            dictDataList.append(restored_dict)

    print('\n\n == 이진파일 읽어 출력 ==')
    for data in dictDataList :
        print(data)

def main() :
    try :
        dictDataList = csvRead()
        flamList = over70Flam(dictDataList)
        binarySave(flamList)
        binaryRead(len(dictDataList[0].keys()))
    # 파일 입출력 관련 예외처리
    except FileNotFoundError as e : 
        print(e.__class__.__name__ + ' :: 파일이 없거나, 설정된 경로와 다르거나, 이름이 달라 확인할 수 없습니다.')
        sys.exit(1)
    except PermissionError as e : 
        print(e.__class__.__name__ + ' :: 본 계정은 해당 파일에 대한 접근권한이 없으므로, 파일을 열 수 없습니다.')
        sys.exit(1)
    except IsADirectoryError as e : 
        print(e.__class__.__name__ + ' :: 디렉토리는 파일이 아니므로 열 수 없습니다.')
        sys.exit(1)
    except IOError as e : 
        print(e.__class__.__name__ + ' :: 입출력 오류발생. ')
        sys.exit(1)
    except MemoryError as e : 
        print(e.__class__.__name__ + ' :: 한 번에 처리하기에 너무 큰 파일입니다.')
        sys.exit(1)
    except EOFError as e : 
        print(e.__class__.__name__ + ' :: 이미 파일의 마지막 부분이므로 더이상 읽을 수 없습니다.')
        sys.exit(1)
        
    # csv 파일 관련 예외처리
    except csv.Error as e :
        print(e.__class__.__name__ + ' :: 행들의 필드 개수가 서로 다릅니다. csv.DictReader()를 사용해주세요.')
        sys.exit(1)
    except UnicodeDecodeError as e :
        print(e.__class__.__name__ + ' :: 인코딩 방식이 불일치하거나 읽어오고자하는 바이트 길이가 잘못되었습니다.')
        sys.exit(1)    
    except KeyError as e :
        print(e.__class__.__name__ + ' :: 존재하지 않는 헤더로 파일 읽기를 시도 중입니다.')
        sys.exit(1)
        
    # 이진 파일 관련 예외처리
    except struct.error	 as e :
        print(e.__class__.__name__ + ' :: float형의 unpack을 위한 바이트 크기가 부족합니다.')
        sys.exit(1)
    except OverflowError as e :
        print(e.__class__.__name__ + ' :: 할당된 바이트보다 큰 크기의 변수를 저장하려하고 있습니다.')
        sys.exit(1)
    except TypeError as e :
        print(e.__class__.__name__ + ' :: write() 또는 기타 메소드 등에서 매개변수로 잘못된 타입을 제공 중입니다.')
        sys.exit(1)
    except KeyError as e :
        print(e.__class__.__name__ + ' :: 존재하지 않는 헤더로 파일 읽기를 시도 중입니다.')
        sys.exit(1)
    
    # 기타 예외 처리
    except Exception as e:
        print(f"Unexpected Exception: {type(e).__name__} => {e}")  
        sys.exit(1)
    
main()