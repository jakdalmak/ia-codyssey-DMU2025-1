#
# 코드에 대한 상세 설명은 ReadME.md를 참조해주세요.
#

import random, os, sys, get_time_with_ctypes as my_time

BASE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
LOG_SAVE_DIRECTORY = os.path.join(BASE_DIRECTORY, 'SensorData.log')

class DummySensor :
    
    def _make_range_get_set_property(key, value_type):
        def getter(self):
            return self._ranges[key]
        def setter(self, value):
            min_val, max_val = value # value는 튜플이나 리스트 등 묶여있는거 기준으로 설정하였음.
            if not isinstance(min_val, value_type) or not isinstance(max_val, value_type):
                raise TypeError(f"{key} 범위 값은 {value_type.__name__} 타입이어야 합니다.")
            if min_val >= max_val:
                raise ValueError("min은 max보다 작아야 합니다.")
            self._ranges[key] = (min_val, max_val)
        return property(getter, setter) # Property라는 데코레이터 객체 이용. 데코레이터는 일종의 어노테이션.. 같은느낌???

    # getter, setter를 설정해둔다.
    # property 설정은 클래스 단위에서 시행되어야하므로 아래와 같이 class 메소드들의 외부에서 수행.
    # 이 값에 대해 클래스 내부에서는 self. 이용하여 접근하고, 클래스 외부에서는 클래스명. 이용하여 접근
    inter_temp_range = _make_range_get_set_property("inter_temp", int)
    exter_temp_range = _make_range_get_set_property("exter_temp", int)
    inter_humi_range = _make_range_get_set_property("inter_humi", float)
    exter_illum_range = _make_range_get_set_property("exter_illum", int)
    inter_co2_range = _make_range_get_set_property("inter_co2", float)
    inter_oxy_range = _make_range_get_set_property("inter_oxy", float)
        
    
    
    def __init__(self) :
        # __slots__를 통해 DummySensor에 의도되지 않은 필드 변수 설정되는 것 방지.
        # ex. DummySensor.imTroll = 'hahaha' 와 같이 의도되지 않은 필드 추가되는 것 방지 가능.
        __slots__ = ['_fieldnames', '_ranges', '_env_values']
        
        # 필드명 변경되거나 관리되는 경우 위한 리스트화
        # 하드코딩해두면 나중에 겁나 불편하니까...
        self._fieldnames = [
            'mars_base_internal_temperature',
            'mars_base_external_temperature',
            'mars_base_internal_humidity',
            'mars_base_external_illuminance',
            'mars_base_internal_co2',
            'mars_base_internal_oxygen'
        ]
        
        # range 값 설정. 동일한 목적의 변수들에 대한 값끼리 튜플로 묶어 사용.
        # 파이선은 접근제어자(private, public 등)이 존재하지 않는다.
        # 대신, 개발자들 간의 규칙 설정을 위한 단순 표기 목적으로 변수 앞에 _를 사용/미사용으로 갈림
        # _를 사용 시, private로서 별도의 setter 등으로만 접근하기로 하는 약속. 즉, 파이선에는 클래스 필드에 대한 '''시스템적 강제성이 없음'''
        self._ranges = {
            'inter_temp': (0, 1),
            'exter_temp': (0, 21),
            'inter_humi': (0.5, 0.6),
            'exter_illum': (500, 715),
            'inter_co2': (0.0002, 0.001),
            'inter_oxy': (0.04, 0.07)
        }

        # 이거도 마찬가지로 앞에 _써서 private 처럼 사용해줄 것 부탁(명시)하였음.
        # 객체 외부에서 env_values 수정/가져와야 하는 경우 setter/getter 만들어서 사용해야함!
        # 주저리 : 근데 밖에서 안쓰고 안에서만 쓰고있음. 지금 코드만으로도 눈돌아갈거같으니 일단 setter/getter 안만들기. 
        self._env_values = {
            self._fieldnames[0] : 0, # 18 ~ 30도
            self._fieldnames[1] : 0, # 0 ~ 21도
            self._fieldnames[2] : 0.0, # 50 ~ 60%
            self._fieldnames[3] : 0, # 500 ~ 715 W/m2
            self._fieldnames[4] : 0.0, # 0.02 ~ 0.1%
            self._fieldnames[5] : 0.0 # 4 ~ 7%
        } # 딕셔너리 형식으로 설정
        
        print(f'getter 동작 확인목적\ninter_temp_range : {self.inter_temp_range}')
        self.inter_temp_range = (18, 30)# setter 동작 확인 목적
        print(f'setter/getter 동작 확인목적\ninter_temp_range : {self.inter_temp_range}')
    
        
        
    def set_env(self) : # 값들을 랜덤 설정하는 메소드. 개별 setter 목적이 아님에 주의
        r = self._ranges 
        
        # 1. *{튜플명}은 형식의 사용은 튜플을 해체 해 내부 값들을 사용하겠음을 의미한다.
        #    즉, 아래 매개변수들은 inter_temp 기준, random.randrange(18,30)과 같이 두 개의 매개변수로 제공된다.
        # 2. _env_values는 private로 자체적으로 규약하였으나, set_env 자체가 DummySensor 내에 있으니까 getter/setter 사용 상관X
        self._env_values['mars_base_internal_temperature'] = random.randrange(*r["inter_temp"])
        self._env_values['mars_base_external_temperature'] = random.randrange(*r["exter_temp"])
        self._env_values['mars_base_internal_humidity'] = round(random.uniform(*r["inter_humi"]), 2)
        self._env_values['mars_base_external_illuminance'] = random.randrange(*r["exter_illum"])
        self._env_values['mars_base_internal_co2'] = round(random.uniform(*r["inter_co2"]), 4)
        self._env_values['mars_base_internal_oxygen'] = round(random.uniform(*r["inter_oxy"]), 2)

        # discord 내 교수님 언급에 따라 로그파일 작성 기능을 set_env()로 이전합니다.
        # 추가 과제 1 - 로그파일에 현재 객체 내역을 연월일시분초와 함께 추가하기.
        # 해당 메소드는 get_time_with_ctypes py 파일 참조해주세요.
        nowTime = my_time.stamp_time_with_ctypes()
        isLogExists = os.path.exists(LOG_SAVE_DIRECTORY) 
        
        header = ''
        if not isLogExists : # 파일이 존재하지 않는 경우에만 수행
            try : # join문 쓰면서 하도 에러가 나서, 아예 별도로 try-catch문 작성.
                if 'time' not in self._fieldnames :
                    self._fieldnames.insert(0, 'time')
                header = ', '.join(self._fieldnames) + '\n'
                
            except Exception as e :
                print(f"Unexpected Exception: {type(e).__name__} => {e}")
                print('join문 잘못쓴거같으니 확인해보기. 파일은 안만들어짐.')  
        
        with open(LOG_SAVE_DIRECTORY, 'a') as file :
            file.write(header)
            file.write(f"{nowTime}, {self._env_values['mars_base_internal_temperature']}, {self._env_values['mars_base_external_temperature']}, " \
                    f"{self._env_values['mars_base_internal_humidity']}, {self._env_values['mars_base_external_illuminance']}, " \
                    f"{self._env_values['mars_base_internal_co2']}, {self._env_values['mars_base_internal_oxygen']}\n")
        
    def get_env(self) :
        return self._env_values

def set_sensor() :
    ds = DummySensor()
    ds.set_env()
    return ds

def print_sensor(envDict) :
    print('DummySensor 값 출력하기 : ')
    for key in envDict.keys() :
        print(' '.join([key, str(envDict[key])]))

def main() :
    ds = set_sensor()
    print_sensor(ds.get_env())
    
    
try : 
    main()
except Exception as e:
    print(f"Unexpected Exception: {type(e).__name__} => {e}")  
    sys.exit(1)