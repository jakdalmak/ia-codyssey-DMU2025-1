#
# 참고. 에러나는 코드입니다. private/public 학습 목적이라 당연히 날 수 밖에 없음.. 이거저거 주석 달았다 풀었다하며 사용해보기.
#


### 1. _ 는 private이며, 시스템 차원에서 판정하지 않는다? => X

class myClass :
    
    __slots__ = ['__thisIsPrivate', '_thisIsProtected', 'thisIsPublic']
    
    def __init__(self) :
        self.__thisIsPrivate = 0
        self._thisIsProtected = 0
        self.thisIsPublic = 0
    
    def __privateMethod(self) :
        print("imPrivate!!! 외부에서 보이나요?")
    
    def _protected(self) :
        print("imProtected!!!") 
    
    def public(self) :
        print("imPublic!!!")
    

def main() :
    mc = myClass()
    
    mc.__thisIsPrivate = 1 
    # 이렇게 외부에서 __로 할당하는건 아예 해당 명칭의 새 변수를 만드는듯 하다. 
    # __가 접근제어자로 사용되지 않고 그냥 변수명으로 적용되는지 아래 print문이 가동되어버림...
    # slots 매직변수까지 이용해야 완전히 막는듯 보임.
    
    print(mc.__thisIsPrivate) 
    # slot 매직변수가 없으면 위의 선언문이 가동되긴하지만, 이건 또 접근이 안된다!
    # 아마 기존의 __thisIsPrivate라는 필드 변수에 대해 접근하려 시도해서, 이건 private 판정으로 접근이 안되는듯.
    # 사실 정확히는, 파이선의 private은 이름을 바꿔치기해서 가리는 일종의 속임수라고 함.
    # 이런걸 'mangling'이라고 부른다고 하는데, 이런거 명칭까지 알아야하나.. -_-;;
    
    
    
    mc._protected()
    mc.public()
    
    mc.__privateMethod() # 얘는 구동이 안되요~ private 메소드라서 그럼.
    
    #
    # 2. 파이선 private 빨간약 먹기 - 클래스 외부에서 수정/접근 맘대로 하는법(선언은 아님)
    #
    mc._myClass__thisIsPrivate = 1 # 파이선의 __ 를 통한 private 지정은 다음과 같이 _클래스명__접근대상private변수명 으로 접근할 수 있다고함.
    
    print(mc._myClass__thisIsPrivate) # 바뀌어버린 1이라는 값으로 나오는거 확인 가능. 
    
    mc._myClass__privateMethod()
    
main()