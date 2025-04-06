import random
import os
import sys
import time
import get_time_with_ctypes as my_time

BASE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
LOG_SAVE_DIRECTORY = os.path.join(BASE_DIRECTORY, 'SensorData.log')
AVERAGE_LOG_SAVE_DIRECTORY = os.path.join(BASE_DIRECTORY, 'AverageData.log')

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
        # sensor 인스턴스와 해당 센서의 키(환경 변수)를 저장 (time 키 제외)
        self.sensor = sensor
        self.sensor_keys = [key for key in sensor.get_env().keys()]

        # 5분 평균 계산을 위한 누적 데이터 (각 센서 값별)
        self._accumulated_data = {key: [] for key in self.sensor_keys}
        self._tick_counter = 0  # 초 단위 틱 카운터
        
        self.env_values = {}  # 화성 기지 환경 정보를 저장하는 사전
    
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

def set_sensor():
    ds = DummySensor()
    ds.set_env()
    return ds

def main():
    ds = set_sensor()
    # MissionComputer 인스턴스를 RunComputer로 명명하여 생성
    RunComputer = MissionComputer(ds)
    RunComputer.run()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'Unexpected Exception: {type(e).__name__} => {e}')
        sys.exit(1)