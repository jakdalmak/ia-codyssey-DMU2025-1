#
# 내장 모듈의 기준은? => pip install을 통해 별도로 설치해야하는 라이브러리나 패키지가 아닌 것들!
#

import csv, os

BASE_DIRECTORY = os.path.dirname(os.path.abspath(__file__)) # 본 코드가 실행된 파일이 위치한 디렉토리를 절대경로로 추출
CSV_FILE_PATH = os.path.join(BASE_DIRECTORY, 'Mars_Base_Inventory_List.csv') # csv 파일의 위치를 절대경로로 설정
CSV_SAVE_PATH = os.path.join(BASE_DIRECTORY, 'Mars_Base_Inventory_danger.csv') # csv 파일의 위치를 절대경로로 설정
BIN_SAVE_PATH = os.path.join(BASE_DIRECTORY, 'Mars_Base_Inventory_List.bin')


with open(CSV_FILE_PATH, mode = 'r', encoding = 'UTF-8') as file :
    # csvReader = csv.reader(file) # csvReader는 csv의 각 행의 내역을 리스트로 저장하고있다. ','와 같은 구분자 자동으로 찾아내어 리스트 분할까지 제공.
    # formatList = [format for format in next(csvReader)] # csv의 0번째 줄에는 포맷이 있으므로, 이를 별도 저장. csv 모듈의 reader 객체는 next(read객체명) 형식 사용하여 커서 이동.  

    # dataList = list(csvReader) # 위의 next()로 커서가 이미 넘어갔으므로, 나머지 내역을 list화 하여 이중 리스트[[],[],[]] 형식으로 변환
    
    #
    # 내용을 읽어 리스트 객체 변환
    #
    csvReader = csv.DictReader(file)
    dictDataList = list(csvReader) # 딕셔너리를 내부 데이터로 갖는 리스트 완성. [{},{},...,{}]
    
    # 문제에서 나타난 배열은, array에 대해 이야기하는게 아니다!!!
    # 파이선은 list 역시 배열이라고 취급한다. 동적으로 크기가 늘어나는 배열일 뿐임.
    # 그리고 배열로 옮기려고 해도, 어차피 파이선의 배열(array.array)은 리스트나 딕셔너리 등의 복합 자료형을 저장할 수 없다.
    # 결론 : 그냥 리스트 쓰세요. 지금은...
    
    # dictDataArray = array.array([''], [0] * len(dictDataList))
    # for i in range(0, len(dictDataList)) :
    #     dictDataArray[i] = dictDataList[i]    
    # dictDataArray.sort(reverse=True, key=lambda obj : obj['Flammability'])
    # print(arr for arr in dictDataArray)
    
    # 
    # 높은순 정렬 수행
    # 
    dictDataList.sort(reverse=True, key = lambda dic : dic['Flammability']) 
    
    # 인화성이 0.7 이상인 값들의 집합을 추출.
    # 컴프리헨션 구문 사용.
    over70PerFlamList = [data for data in dictDataList if float(data['Flammability']) >= 0.7]
    
    with open(CSV_SAVE_PATH, 'w', encoding = 'UTF-8', newline = '') as writeFile :
        fieldnames = dictDataList[0].keys() # csv 헤더 값을 설정하기 위한 딕셔너리 내부 키값 추출
        writer = csv.DictWriter(writeFile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(over70PerFlamList)
        
    with open(BIN_SAVE_PATH, 'wb') as writeBinFile :
        fieldnames = dictDataList[0].keys()
        
        writeBinFile.write(len(dictDataList).to_bytes(4, 'little')) # 리스트 내의 딕셔너리 전체 개수를 저장 
        
        for dictionary in dictDataList :
            writeBinFile.write(dictionary[fieldnames[0]].to_bytes(4, 'little'))
            writeBinFile.write()
            
    with open(BIN_SAVE_PATH, 'rb') as readBinFile :
        
   

