#
# 1) 주의!!! 반드시, 아래 명령어를 사용하여 psutil패키지를 설치해주세요.
# pip install psutil
#
# 2) setting.txt 내부의 json 양식 값을 true/false로 수정하여
# 출력되는 json 값의 양식을 설정 가능합니다.
# 보너스 과제 정상 동작 확인을 위해 setting.txt의 cpu/RAM 실시간 사용량 표기 여부가 false로 설정되어있습니다.
# 이 점 참고하여 평가해주시기 바랍니다.
#
# 3) get_time_with_ctypes가 week04 디렉토리에 위치해있습니다.
# 혹시나 week05 내부 파일만 사용하게되면 오류가 발생합니다. 전체 Repository를 pull해주시기 부탁드립니다.
#

import sys
import os
import platform
import ctypes
import random
import time
import json
import psutil

BASE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
LOG_SAVE_DIRECTORY = os.path.join(BASE_DIRECTORY, 'SensorData.log')
AVERAGE_LOG_SAVE_DIRECTORY = os.path.join(BASE_DIRECTORY, 'AverageData.log')
COM_SETTING_TXT_DIRECTORY = os.path.join(BASE_DIRECTORY, 'setting.txt')

# week05\Answer\ 에서 두 단계 상위로 올라가, week04\Answer 폴더 경로를 계산
week04_answer_dir = os.path.join(BASE_DIRECTORY, "..", "..", "week04", "Answer")
week04_answer_dir = os.path.abspath(week04_answer_dir)

# 파이썬 모듈 검색 경로에 week04\Answer 경로를 추가
sys.path.append(week04_answer_dir)

import get_time_with_ctypes as my_time


class DummySensor:
    
    def _make_envvalues_get_set_property(key, value_type):
        def getter(self):
            return self.__env_values
        def setter(self, value):
            if not isinstance(value, value_type):
                raise TypeError(f"{key} 범위 값은 {value_type.__name__} 타입이어야 합니다.")
            self.__env_values = value
        return property(getter, setter)
    
    def _make_range_get_set_property(key, value_type):
        def getter(self):
            return self.__ranges[key]
        def setter(self, value):
            min_val, max_val = value
            if not isinstance(min_val, value_type) or not isinstance(max_val, value_type):
                raise TypeError(f"{key} 범위 값은 {value_type.__name__} 타입이어야 합니다.")
            if min_val >= max_val:
                raise ValueError('min은 max보다 작아야 합니다.')
            self.__ranges[key] = (min_val, max_val)
        return property(getter, setter)
    
    def _make_fieldname_get_set_property(value_type):
        def getter(self):
            return self.__fieldnames
        def setter(self, value, del_index=None, del_value=None):
            if del_index is None and del_value is None:
                if not isinstance(value, value_type):
                    raise TypeError(f"{value}는 {value_type.__name__} 타입이어야 합니다.")
                self.__fieldnames.append(value)
            elif del_index is not None:
                if not isinstance(del_index, int):
                    raise TypeError("인덱스는 int 타입이어야 합니다.")
                self.__fieldnames.pop(del_index)
            elif del_value is not None:
                if not isinstance(del_value, value_type):
                    raise TypeError(f"{del_value}는 {value_type.__name__} 타입이어야 합니다.")
                self.__fieldnames.remove(del_value)
        return property(getter, setter)
    
    # __ranges에 대한 getter, setter 설정.
    inter_temp_range = _make_range_get_set_property('inter_temp', int)
    exter_temp_range = _make_range_get_set_property('exter_temp', int)
    inter_humi_range = _make_range_get_set_property('inter_humi', float)
    exter_illum_range = _make_range_get_set_property('exter_illum', int)
    inter_co2_range = _make_range_get_set_property('inter_co2', float)
    inter_oxy_range = _make_range_get_set_property('inter_oxy', float)
    
    field_name = _make_fieldname_get_set_property(str)
    env_values = _make_envvalues_get_set_property('env_values', dict)
    
    __slots__ = ['__fieldnames', '__ranges', '__env_values']
     
    def __init__(self):
        self.__fieldnames = [
            'mars_base_internal_temperature',
            'mars_base_external_temperature',
            'mars_base_internal_humidity',
            'mars_base_external_illuminance',
            'mars_base_internal_co2',
            'mars_base_internal_oxygen'
        ]
   
        self.__ranges = {
            'inter_temp': (18, 30),
            'exter_temp': (0, 21),
            'inter_humi': (0.5, 0.6),
            'exter_illum': (500, 715),
            'inter_co2': (0.0002, 0.001),
            'inter_oxy': (0.04, 0.07)
        }

        self.__env_values = {
            self.__fieldnames[0]: 0,  # 18 ~ 30도
            self.__fieldnames[1]: 0,  # 0 ~ 21도
            self.__fieldnames[2]: 0.0,  # 50 ~ 60%
            self.__fieldnames[3]: 0,  # 500 ~ 715 W/m2
            self.__fieldnames[4]: 0.0,  # 0.02 ~ 0.1%
            self.__fieldnames[5]: 0.0   # 4 ~ 7%
        }
    
    def set_env(self):
        r = self.__ranges 
        self.__env_values['mars_base_internal_temperature'] = random.randrange(*r['inter_temp'])
        self.__env_values['mars_base_external_temperature'] = random.randrange(*r['exter_temp'])
        self.__env_values['mars_base_internal_humidity'] = round(random.uniform(*r['inter_humi']), 2)
        self.__env_values['mars_base_external_illuminance'] = random.randrange(*r['exter_illum'])
        self.__env_values['mars_base_internal_co2'] = round(random.uniform(*r['inter_co2']), 4)
        self.__env_values['mars_base_internal_oxygen'] = round(random.uniform(*r['inter_oxy']), 2)

        nowTime = my_time.stamp_time_with_ctypes()
        isLogExists = os.path.exists(LOG_SAVE_DIRECTORY) 
        
        header = ''
        if not isLogExists:
            try:
                if 'time' not in self.__fieldnames:
                    self.__fieldnames.insert(0, 'time')
                header = ', '.join(self.__fieldnames) + '\n'
            except Exception as e:
                print(f'Unexpected Exception: {type(e).__name__} => {e}')
                print('join문 잘못쓴거같으니 확인해보기. 파일은 안만들어짐.')  
        
        # with open(LOG_SAVE_DIRECTORY, 'a') as file:
        #     file.write(header)
        #     file.write(f'{nowTime}, {self.__env_values["mars_base_internal_temperature"]}, {self.__env_values["mars_base_external_temperature"]}, ' \
        #                f'{self.__env_values["mars_base_internal_humidity"]}, {self.__env_values["mars_base_external_illuminance"]}, ' \
        #                f'{self.__env_values["mars_base_internal_co2"]}, {self.__env_values["mars_base_internal_oxygen"]}\n')
        
    def get_env(self):
        return self.__env_values

# MissionComputer 클래스 구현
class MissionComputer :
    def __init__(self, sensor):
        """
        week 04 미션 목적의 필드
        """
        
        # sensor 인스턴스와 해당 센서의 키(환경 변수)를 저장 (time 키 제외)
        self.sensor = sensor
        self.sensor_keys = [key for key in sensor.get_env().keys()]

        # 5분 평균 계산을 위한 누적 데이터 (각 센서 값별)
        self._accumulated_data = {key: [] for key in self.sensor_keys}
        self._tick_counter = 0  # 초 단위 틱 카운터
        
        self.env_values = {}  # 화성 기지 환경 정보를 저장하는 딕셔너리
        
        """
        week 05 미션 목적의 필드
        """
        self.computer_info = {} # 컴퓨터 기본 정보를 저장하는 딕셔너리
        self.system_load_percent = {} # 컴퓨터의 현재 CPU 및 메모리 사용량을 저장하는 딕셔너리.
        with open(COM_SETTING_TXT_DIRECTORY, 'r') as settingFile :
            setting_str = settingFile.read() # 1개의 str 객체로 전부 읽어오기
            self.computer_system_print_settings = json.loads(setting_str) # 딕셔너리로 기입
        
    def _dict_to_json_str(self, dictonary):
        # JSON 형태로 변환. 키와 문자열은 " "로 감싸야 json 양식이 충족된다!
        items = []
        for key, value in dictonary.items():
            key_str = f'"{key}"'
            if isinstance(value, str): # value가 str자료형인경우 이를 표기하기위해 쌍따옴표 추가
                value_str = f'"{value}"'
            else:
                value_str = str(value) # str이 아니어도 json은 일단 문자 표기므로 str화 시키기. print해야하므로..
            items.append(f'{key_str}: {value_str}')
        return '{' + ', '.join(items) + '}'
    
    
     # 센서의 최신 값을 가져와 env_values에 저장하고 JSON 형식으로 출력하는 메소드
    def get_sensor_data(self):
        self.sensor.set_env()
        self.env_values = self.sensor.get_env().copy()  # 얕은 복사
        # 누적 데이터에 추가 (time 키 제외)
        for key, value in self.env_values.items():
            if key != 'time':
                self._accumulated_data[key].append(value)
        # JSON 형식으로 출력
        sensor_json = self._dict_to_json_str(self.env_values)
        print(sensor_json)
        # SensorData.log 파일에 CSV 형식으로 로그 저장 (타임스탬프 포함)
        timestamp = my_time.stamp_time_with_ctypes()
        csv_line = f'{timestamp},' + ','.join(str(self.env_values.get(key, "")) for key in self.sensor_keys) + '\n'
        # 파일이 없으면 헤더 작성
        if not os.path.exists(LOG_SAVE_DIRECTORY):
            with open(LOG_SAVE_DIRECTORY, 'w') as f:
                f.write("timestamp," + ",".join(self.sensor_keys) + "\n")
        with open(LOG_SAVE_DIRECTORY, 'a') as f:
            f.write(csv_line)
    
    # 5분 동안 누적된 각 센서 값의 평균을 계산하여 출력하기
    def print_5min_average(self):
        avg_data = {}
        for key, values in self._accumulated_data.items():
            if values:
                avg = sum(values) / len(values)
                if key == 'mars_base_internal_co2':
                    avg_data[key] = round(avg, 4)
                else :
                    avg_data[key] = round(avg, 2)
            else:
                avg_data[key] = None
        avg_json = self._dict_to_json_str(avg_data)
        print('5분 평균:', avg_json)
        # 보너스 과제: AverageData.log 파일에 CSV 형식으로 로그 저장 (타임스탬프 포함)
        timestamp = my_time.stamp_time_with_ctypes()
        csv_line = f'{timestamp},' + ','.join(str(avg_data.get(key, "")) for key in self.sensor_keys) + '\n'
        if not os.path.exists(AVERAGE_LOG_SAVE_DIRECTORY):
            with open(AVERAGE_LOG_SAVE_DIRECTORY, 'w') as f:
                f.write("timestamp," + ",".join(self.sensor_keys) + "\n")
        with open(AVERAGE_LOG_SAVE_DIRECTORY, 'a') as f:
            f.write(csv_line)
        # 누적 데이터 초기화
        for key in self._accumulated_data:
            self._accumulated_data[key] = []
    
    def tick_and_print(self):
        # 1초마다 호출, 5초마다 센서 데이터 출력, 5분마다 평균 출력
        if self._tick_counter % 5 == 0:
            self.get_sensor_data()
        if self._tick_counter > 0 and self._tick_counter % 300 == 0:
            self.print_5min_average()
        self._tick_counter += 1

    def run(self):
        # get_sensor_data()를 5초마다 호출하며 지속적으로 환경 정보를 출력하는 메인 루프

        while True:
            self.tick_and_print()
            time.sleep(1)
    
    """
    여기 아래부터는 5주차 메소드
    
    표준 라이브러리만 사용하여 OS/버전/CPU 타입/코어 수/메모리 크기 등을 반환한다.
    일부 OS는 메모리 추출이 불가능할 수 있음.
    """     
    def get_mission_computer_info(self):
        
        # 1) 운영체제 이름과 버전
        if self.computer_system_print_settings['os_name'] :
            self.computer_info['os_name'] = platform.system()     # "Windows", "Linux", "Darwin", etc.
        
        if self.computer_system_print_settings['os_version'] :
            self.computer_info['os_version'] = platform.release() # 예: "10" (Windows 10), "5.15.0-67-generic" (Ubuntu 커널), etc.

        # 2) CPU 타입, CPU 코어 수
        #    - processor()가 공백을 반환하거나 OS별 차이가 있을 수 있어 
        #      machine()를 함께 확인
        #    - 두 메소드 모두 CPU 정보를 반환
        #    - processor() == CPU 실제 모델명(상세), 일부 os 미지원
        #    - machine() == 현재 머신의 하드웨어 타입(아키텍처 이름)을 반환.
        #    - or 이용하여 processor() 값이 빈 문자열일경우 뒤의 값 사용.(공백 나오는거 본적없긴함..)
        if self.computer_system_print_settings['cpu_type'] :
            self.computer_info['cpu_type'] = (platform.processor() or platform.machine() or '확인 불가. 문의 바랍니다')
        
        if self.computer_system_print_settings['cpu_cores'] :
            self.computer_info['cpu_cores'] = os.cpu_count()

        # 3) 메모리 용량(바이트 단위) - OS별 처리
        # 초기값은 None으로 설정.
        if self.computer_system_print_settings['memory_bytes'] :
            mem_bytes = None
            if platform.system() == 'Windows' :
                # Windows에서는 ctypes를 이용해 WinAPI 호출
                # ctypes에서 CDLL로 C 표준 라이브러리를 불러오듯
                # WinDLL을 이용하면 Window API를 불러올 수 있다.
                kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
                mem_kb = ctypes.c_uint64(0)
                
                # 램의 '정확한 총량'을 제공하는 API..라는데요.
                ret = kernel32.GetPhysicallyInstalledSystemMemory(ctypes.byref(mem_kb))
                if ret != 0:
                    # GetPhysicallyInstalledSystemMemory()는 KB 단위 값을 반환
                    mem_bytes = mem_kb.value * 1024
                else:
                    # 실패 시, 0을 반환.
                    # 메모리(RAM)가 존재하지 않는 파이선 구동 가능 기기는 있을 수 없다.
                    # 특히 본 코드가 실행되어 mem_bytes라는 변수가 존재하고, 0이라는 값이 할당되었다는 사실 자체가
                    # None을 이용하는 것보다 '메모리 값을 읽어오지 못했다'라는 뜻을 전달하는데 더 좋다고 보임.
                    mem_bytes = 0

            elif platform.system() in ('Linux', 'Darwin'):
                # 유닉스 계열: sysconf로 물리 메모리 크기를 추정
                # 유닉스 계열에서 구동되는 파이선은 os 기본 모듈 내에 sysconf라는 명칭의 함수를 지닌다고 함.
                # 나는 윈도우라 모르겠는데..
                if hasattr(os, "sysconf"):
                    try:
                        # 페이지? : 물리 메모리 및 가상 메모리(HDD 등의 저장 공간 활용)에 대한 기본 단위
                        # 즉, 하나의 페이지 크기가 바이트 기준 얼마인지 구하고, 그 값에 대해 물리 페이지 개수를 곱한다.
                        
                        page_size = os.sysconf("SC_PAGE_SIZE")      # 바이트 단위 페이지 크기
                        phys_pages = os.sysconf("SC_PHYS_PAGES")    # 전체 물리 페이지 수
                        mem_bytes = page_size * phys_pages
                    except (ValueError, OSError):
                        mem_bytes = 0
                else:
                    mem_bytes = 0
            else: # 이 else문에서는 mem_bytes 값이 None인 경우에 해당한다.
                raise OSError(
                    '지원하지 않는 OS입니다. 개발자에게 문의해주세요.'
                )
            
            if mem_bytes == 0 :
                raise OSError(
                    '정상적으로 RAM 크기를 확인하지 못했습니다.'
                )

            # 보기 편하게 기가바이트 단위추가
            self.computer_info["memory_bytes"] = mem_bytes
            self.computer_info["memory_gb"] = mem_bytes // (1024 * 1024 * 1024)
        
        if len(self.computer_info) != 0:
            print(self._dict_to_json_str(self.computer_info))
        else : print('표기할 시스템 정보가 없습니다. setting.txt를 확인해주세요.')
    
    """
        psutil 라이브러리를 이용해 CPU/메모리 실시간 사용률을 측정.
        (CPU 사용률, 메모리 사용률을 딕셔너리로 반환)
    """
    def get_mission_computer_load(self):
        
        #
        # 자문자답 Q. CPU 사용률을 고작 1초 간 샘플링한 것으로 상황을 이해 할 수 있을까?
        # 자문자답 A. cpu_percent의 interval 값을 설정하지 않으면 실행 시점을 플래그로 삼아 기간을 지정 가능하다고 함.
        #            ex. 시작하자마자 psutil.cpu_percent(), 30초 뒤에 psutil.cpu_percent()하면 0~30초 간 CPU 사용률 가져오기 가능
        #            
        #            이건 하려면 아마 스레드.. 써야할거같음. 30초 대기를 비동기로 해야 다른 코드 진행될테니까.
        #            아직 스레드 공부 못함(바쁘다) + 문제에 별도의 기준 없음 이라는 느낌쓰로다가 그냥 1초로 퉁치기.
        #            그리고 보통 1초 샘플링으로 실시간 사용률 측정하는게 일반적이라고 함...
        #

        # 참고 : 파이선은 if문 단락 내에서 만들어진 변수여도 같은 메소드 내라면 사용 가능함. 또 뭔 짓을 해놓은거지?
        # CPU 사용률(%) - interval=1.0이면 1초간 샘플링 진행.
        if self.computer_system_print_settings['cpu_usage(%)'] :
            try:
                cpu_usage_percent = psutil.cpu_percent(interval=1.0, percpu=True)
                if isinstance(cpu_usage_percent, list) :
                    print('본 기기의 CPU 스레드 개수 ' + str(len(cpu_usage_percent)))
            except Exception as e:
                raise RuntimeError(f"psutil, CPU 사용률 검출 실패: {e}") from e
            self.system_load_percent['cpu_usage(%)'] = cpu_usage_percent

        # 메모리 사용량(%) - psutil.virtual_memory()를 통해 전체 사용률 확인
        if self.computer_system_print_settings['memory_usage(%)'] :
            try:
                # svmem(total=34282242048, available=11765596160, percent=65.7, used=22516645888, free=11765596160)
                memory_usage_percent = psutil.virtual_memory().percent
            except Exception as e:
                raise RuntimeError(f"psutil, 메모리 사용률 검출 실패 : {e}") from e
            self.system_load_percent['memory_usage(%)'] = memory_usage_percent
        
        if len(self.system_load_percent) != 0 :
            print(self._dict_to_json_str(self.system_load_percent))
        else : print('표기할 시스템 사용량이 없습니다. setting.txt를 확인해주세요.')
    
    """
    # 잘못 이해해서 만든거.. settings.txt는 출력 결과를 보이는 목적이 아니라
    # 출력 결과의 목록을 조정하기위한 일종의 리모콘으로 settings.txt를 활용하는게 목적.
    # 아래 메소드 내용은 무시하기. 그래도 딕셔너리 합칠 때 유의사항 하나는 알았다.
    """
    def write_setting_txt(self, isInfo=True, isLoadPer=True) :
        # 문제는 txt 파일을 요구한다.
        # 로그 파일이 아닌 txt를 요구한다는 것은, 시간을 두고 변환될 수 있는 데이터를 제공하라는게 아니라
        # 그냥 실행 순간의 상태를 제공하라는 것으로 풀이할 수 있으므로 a 대신 w 사용
        # 그게 아니면 지금 가용 가능한 메모리 양, 물리메모리 가상메모리 각각의 공간 등등등 별의 별거 내놓으라고 했겠지..
        with open(COM_SETTING_TXT_DIRECTORY, 'w') as file :
            # 딕셔너리 병합하는 방법론
            # https://code.tutsplus.com/ko/how-to-merge-two-python-dictionaries--cms-26230t
            
            if isInfo and isLoadPer :
                merge_dict = self.computer_info.copy() # 얕은 복사하여 병합 시 원본 데이터 변형 방지
                merge_dict.update(self.system_load_percent)
                file.write('\n'.join(f"{key} : {value}" for key, value in merge_dict.items()))
            elif isInfo :
                file.write('\n'.join(f"{key} : {value}" for key, value in self.computer_info.items()))
            elif isLoadPer :
                file.write('\n'.join(f"{key} : {value}" for key, value in self.system_load_percent.items()))

                



           

try:
    ds = DummySensor()
    ds.set_env()
    runComputer = MissionComputer(ds)

    runComputer.get_mission_computer_info()
    runComputer.get_mission_computer_load()
    # runComputer.write_setting_txt()
except Exception as e:
    print(f'Unexpected Exception: {type(e).__name__} => {e}')
    sys.exit(1)

# 아래 값들을 다른 main.py에서 사용할 경우...
# 이렇게 저장하면 일반적인 경우라면 스냅샷이 되어버림.
# 그래서 보통은...
# import mars_mission_computer as comSys
# comSys.runComputer.computer_info 와 같이 runComputer 객체에 대해 직접적으로 접근해야함.

# 하지만!!! 지금 computer_info, system_load_percent에 대한 값의 할당은
# 1) 본 코드가 실행 될 때 마다
# 2) MissionComputer() class 내부의 dict 들에 대해 '업데이트'하여 사용하고있다.
# 즉, 딕셔너리 주소를 먼저 할당하고 사용중이므로, main.py에서 아래와 같이 사용하여

# comSys.system_load_percent {{A}}
# comSys.get_mission_computer_load()
# comSys.system_load_percent {{B}}

# 와 같이 진행해도 B는 A와 다른 값(새로 업데이트된 값)을 나타낸다.
# 아래 코드는 객체 내의 딕셔너리를 깊은 복사 했으니까 같은 주소 나타내기 때문.

computer_info = runComputer.computer_info
system_load_percent = runComputer.system_load_percent

# 위에 네 줄 요약 : 
# 겁나 길게 써놨는데, 걍 결론은 만약 본 .py 파일을 import하는 main.py에서 
# computer_info, system_load_percent에 대해 접근 시
# comSys.runComputer.변수명 으로 접근하면 귀찮으니까
# comSys.변수명으로 접근하도록 구현했고 이래도 문제 없다는 말입니다. 
