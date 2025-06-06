## Codyssey DMU 2주차 문제

### 필수 단계1: 이별은 화성, 잊고 있었던 고마운 것들 - 동양미래대 문제 내역

https://jakdalmak-work.notion.site/Codyssey-2-1b9f6bbbe13c8039b6e1d160ee13e1ff?pvs=4

### 풀이자에게 전달 사항

main.py와 같은 디렉토리 내에 Mars_Base_Inventory_List.csv가 위치해야합니다.

- 과제 수행 목록 관련

```
텍스트파일 vs 이진 파일 차이점/장단점은 본 파일 내에 설명되어있습니다.
csv 파일 읽고 출력 구현 완료
읽은 내역 리스트 객체 변환 구현 완료.
배열 내용 인화성 기준 내림차순 정렬 구현 완료
인화성 지수 0.7 이상 목록 독립 및 별도 출력 구현 완료
인화성지수 0.7 이상 목록 csv 포맷 저장 구현 완료
파일 예외처리 구현 완료
```

- 추가과제 1 - 인화성 순서 정렬 배열 내역 이진파일 저장
  구현 완료. binarySave() 메소드 참조해주세요.

- 추가과제 2 - 저장된 이진파일 읽어들여 내용 출력
  구현 완료. binaryRead() 메소드 참조해주세요.

- 기타 사항
  사용한 기본 모듈 목록 - os, csv, struct
  pickle 모듈 사용하는 대신, 직접 바이트 파일 읽고 쓰기 구현 시도.

### 텍스트 파일 vs 이진 파일

- 차이점

```
# 텍스트 파일 :
사람이 읽을 수 있는 문자로 저장되며, 인코딩이 사용됨(UTF-8 등)
로그, 설정파일, csv 등 사람이 직접 읽고 수정 가능한 파일에서 주로 사용됨
파일 단위 또는 줄 단위로 처리됨(read(), readLine() 등)

# 이진 파일 :
사람이 읽기 힘든 이진수(0과 1) 데이터로 저장됨.
이미지, 오디오, 영상 및 직렬화 객체 등의 파일 표현을 위해 사용됨.
바이트 단위로 처리됨(read(바이트크기), write(바이트크기) 등)
```

- 장점

```
# 텍스트 파일 :
사람이 쉽게 읽고 수정할 수 있다.
디버깅이 쉽다(눈으로 확인 가능하기 때문)
자유로운 포맷으로 저장 가능하다(JSON, CSV, XML 등)
이식성이 높다(UTF-8 인코딩 기준, OS 및 사용 언어에 상관없이 파일을 열 수 있다.)

# 이진 파일 :
저장 공간이 작다
처리속도가 빠르다(정수, 실수 값은 디코딩 필요가 없기 때문)
복잡한 구조에 사용 가능하다(이미지, 오디오, 영상, 직렬화 객체 등을 저장할 수 있는 이유)
개발자가 직접 구조를 설계할 수 있다(바이트 파일을 쓰고 읽는 방법을 개발자가 직접 설정 -> 효율적인 읽기/쓰기 기능 및 암호화 설계가능)
```

- 단점

```
# 텍스트 파일 :
저장 공간이 크다(숫자 123와 같은 값들도 '문자'로 기준하여 1바이트씩 필요. 1, 2, 3과 같이 각각의 문자로 판정하기 때문)
처리 속도가 느리다(읽어올 때 파싱, 변환, 형변환 등의 작업을 수행해야한다)
보안성이 낮다(사람이 쉽게 열고 확인 가능한 만큼, 민감정보 노출 가능성이 있다.)

# 이진 파일 :
사람이 읽기 어렵다(이진수 기반 저장이므로, 강제로 열 경우 깨져있는 모습만 확인 가능)
수정이 어렵다(바이트 단위로 저장되며, 개발자가 설계한 포맷 하에 저장되므로 수정시 매우 복잡한 과정 거쳐야 할 수 있음)
포맷을 명확히 설정해야 한다(구조 정의를 제대로 하지 않거나, 잘못 한 경우 이상한 값을 읽거나 읽지 못할 수 있다.)
이식성/호환성 문제가 있다(엔디안 및 데이터 정렬 등의 바이트파일 저장 방식에 따라 시스템 별 차이가 있을 수 있다.)
```

### 풀이 관련 내역

현재 Pass 횟수 : 2 - 완료
