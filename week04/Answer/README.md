## Codyssey DMU 1주차 문제

### 필수 단계1: 이별은 화성, 잊고 있었던 고마운 것들 - 동양미래대 문제 내역

https://jakdalmak-work.notion.site/codyssey-4-7-1cdf6bbbe13c80cf95c3f1681929f616?pvs=4

### 풀이자에게 전달 사항

- 과제 수행 목록 관련

- [x] 미션 컴퓨터에 해당하는 클래스를 생성한다. 클래스의 이름은 MissionComputer로 정의한다.
- [x] 미션 컴퓨터에는 화성 기지의 환경에 대한 값을 저장할 수 있는 사전(Dict) 객체가 env_values라는 속성으로 포함되어야 한다.
- [x] env_values라는 속성 안에는 다음과 같은 내용들이 구현 되어야 한다.
  - 화성 기지 내부 온도 (**mars_base_internal_temperature)**
  - 화성 기지 외부 온도 (**mars_base_external_temperature)**
  - 화성 기지 내부 습도 (**mars_base_internal_humidity)**
  - 회성 기지 외부 광량 (**mars_base_external_illuminance)**
  - 화성 기지 내부 이산화탄소 농도 (**mars_base_internal_co2**)
  - 화성 기지 내부 산소 농도 (**mars_base_internal_oxygen**)
- [x] 문제 3에서 제작한 DummySensor 클래스를 ds라는 이름으로 인스턴스화 시킨다.
- [x] MissionComputer에 get_sensor_data() 메소드를 추가한다.
- [x] get_sensor_data() 메소드에 다음과 같은 세 가지 기능을 추가한다.
  - 센서의 값을 가져와서 env_values에 담는다.
  - env_values의 값을 출력한다. 이때 환경 정보의 값은 json 형태로 화면에 출력한다.
  - 위의 두 가지 동작을 5초에 한번씩 반복한다.
- [x] MissionComputer 클래스를 RunComputer 라는 이름으로 인스턴스화 한다.
- [x] RunComputer 인스턴스의 get_sensor_data() 메소드를 호출해서 지속적으로 환경에 대한 값을 출력 할 수 있도록 한다.
- [x] 전체 코드를 mars_mission_computer.py 파일로 저장한다.

- 추가과제 1 - 5분에 한번씩 각 환경값에 대한 5분 평균 값을 별도로 출력한다.

  - 구현완료! 확인 편리하게 하기위해 AverageData.log라는 명칭으로 5분마다 평균값 데이터 파일 작성되도록 설정하였습니다.

- 추가과제 2 - 특정 키를 입력할 경우 반복적으로 출력되던 화성 기지의 환경에 대한 출력을 멈추고 ‘Sytem stoped….’ 를 출력 할 수 있어야 한다.
  - 구현 실패... 동작하는 코드를 이해를 못하겠음.

### 구현 내역 상세 설명

코드 내 주석으로 생략.

### 풀이 관련 내역

현재 Pass 횟수 : 2 - 완료
