import ctypes, ctypes.util, platform
# ctypes.util은 ctypes 임포트만으로 불러와지지 않음.
# ctypes == 파이선에서 C 라이브러리 불러와 사용하기 위해 사용한 기본모듈
# platform == 현재 파일이 실행되고있는 운영체제 명칭을 제대로 확인하기 위해 사용한 기본모듈

def stamp_time_with_ctypes() :
    # C 기준 time 구조체 양식 그대로 따오기.
    class TM(ctypes.Structure): # class임에도 매개변수형식 있는 것은 c의 구조체 구조를 따온것임을 명시적으로 선언하기 위함.
                                # why?? ctypes에서 그냥 그렇게 한대요... 구조 맞추어주어야함.
        _fields_ = [ # 이 파이선 코드에 불러올 C 코드값을 저장하기위해 만든 파이선 내에서의 'C 구조체' 구조를 선언. -> _fields_
            ('tm_sec', ctypes.c_int),    # 초 (0~59)
            ('tm_min', ctypes.c_int),    # 분 (0~59)
            ('tm_hour', ctypes.c_int),   # 시 (0~23)
            ('tm_mday', ctypes.c_int),   # 일 (1~31)
            ('tm_mon', ctypes.c_int),    # 월 (0~11) → 주의: 0이 1월
            ('tm_year', ctypes.c_int),   # 년도 (1900년부터의 년수)
            ('tm_wday', ctypes.c_int),   # 요일 (0~6, 일요일=0)
            ('tm_yday', ctypes.c_int),   # 1년 중 몇 번째 날인지 (0~365)
            ('tm_isdst', ctypes.c_int),  # 일광절약시간 여부... 일광절약시간이 뭐지???
            # 구조체 내부 변수 명칭과 해당 변수의 자료형 명시적으로 설정.
        ]
    
    platformName = platform.system()
    
    # 플랫폼에 따라 C 표준 라이브러리를 로드한다. 플랫폼 별로 c 표준 라이브러리의 이름이 다르기 때문.
    # c 표준 라이브러리가 설치되어있지 않을 확률은 0. 본 미션은 python을 설치한 채로 진행되는 만큼 c 표준 라이브러리도 당연히 설치되어있다.
    # ctypes.util.find_library()를 이용하여 C 런타임이 기본으로 설치되어있는 경로가 아닌 다른 위치에 C가 설치되어있는 경우도 캐치한다.
    if platformName == 'Windows':
        libc = ctypes.CDLL(ctypes.util.find_library('msvcrt')) # Windows에서는 msvcrt.dll (Microsoft C 런타임)을 로드
    elif platformName == 'Linux':
        libc = ctypes.CDLL(ctypes.util.find_library('c')) # Linux,Unix에서는 libc.so.6를 로드
    elif platformName == 'Darwin':  
        # /usr/lib/libSystem.dylib
        libc = ctypes.CDLL(ctypes.util.find_library('c')) # macOS는 C는 물론 갖가지 라이브러리들을 한 곳에 모아둔 슈퍼라이브러리(== libSystem.dylib) 제공. 이거 가져오기.
    else:
        raise OSError('본 모듈에서 지원하지 않는 운영체제입니다. 문의 바랍니다')
        ### ☆☆ 본 에러 발생 시 FAIL 주실 때, 실행된 운영체제를 함께 언급해주시면 감사하겠습니다 ☆☆ ###
        
    
    time_t = ctypes.c_long() # C의 long 타입으로 time_t 변수를 하나 만들기 (time() 함수에 넘길 인자)
    libc.time(ctypes.byref(time_t)) # C의 time() 함수 호출(libc == c표준라이브러리 메소드 지닌 객체) -> 현재 시간을 time_t 변수에 저장
    
    libc.localtime.restype = ctypes.POINTER(TM) # libc에서 참조해 사용할 c의 localtime() 메소드의 리턴값이 struct tm* 타입임을 명시
    
    tm_ptr = libc.localtime(ctypes.byref(time_t))  # time_t를 넘겨 struct tm '포인터'반환받기
                                                   # 왜 포인터를 사용하나요? -> ctypes가 쓰래요...;;
    tm = tm_ptr.contents # 포인터가 가리키는 struct tm 값 가져오기. ctypes를 이용해 저장한 변수 값을 파이선 변수로 불러오기 위해서는 반드시 포인터로 지정해서 가져와야함.
    
    # struct tm에서 각 필드 값 꺼내기 (C에서 했던 것과 똑같이 처리)
    year = tm.tm_year + 1900      # C에서는 1900년 기준이므로 보정 필요
    month = tm.tm_mon + 1         # 0~11 → 1~12 보정
    day = tm.tm_mday
    hour = tm.tm_hour
    minute = tm.tm_min
    second = tm.tm_sec

    # 4자리 or 2자리 가 아닐 때 로그파일 표기 망가질 수 있는 문제 해결 위해 자리별 포맷팅 수행
    return f'{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}'