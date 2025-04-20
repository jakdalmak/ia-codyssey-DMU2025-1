# 설치 관련 주의사항
# 아래 두 개의 명령어를 사용해주세요. (전역 파이선 기반 설치, 가상환경(venv)로 별도로 나누지 않았음)
# pip install PyQt5
# pip install pyqt5-tools

import os, sys


### 주의사항 - 제대로 실행되지 않는다면 여기부터 'PyQt 임포트 진행' 사이의 코드를 삭제후 실행해보시기 바랍니다.
### 작업자 환경상에서, 실행에 필요한 파일(qwindows.dll)을 제대로 찾지 못해 작성한 내역입니다.

# ─── 0) 가능한 모든 후보 경로를 sys.path 에서 찾기 ───
candidates = []
for base in sys.path:
    for pkg in ("PyQt5", "pyqt5_tools", "qt5_tools", "qt5_applications", "pyqt5_plugins"):
        p = os.path.join(base, pkg, "Qt", "plugins", "platforms")
        if os.path.isdir(p):
            candidates.append(p)
# 중복 제거
candidates = list(dict.fromkeys(candidates))

# ─── 1) 발견된 첫 번째 경로를 환경 변수에 설정 ───
if candidates:
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = candidates[0]
else:
    print("!!! Qt platform plugin 폴더를 찾을 수 없습니다.", 
          "\n  시도한 경로들:", *candidates, file=sys.stderr)

###
### 여기서부터 계산기 코드입니다.
###

# PyQt 임포트 진행
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLineEdit,
    QPushButton, QGridLayout, QVBoxLayout
)
from PyQt5.QtCore import Qt

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculator")
        self.setFixedSize(320, 480)
        self._expr = ""
        self._create_ui()
        self._connect_signals()

    def _create_ui(self):
        # 배경 검정색
        self.setStyleSheet("background-color: #000;")

        # 최상단 디스플레이
        self.display = QLineEdit("0", self)
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.display.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: white;
            }
        """)
        self.display.setFixedHeight(80)
        
        # display가 지니는 font 가져와 수정 후 다시 기입
        font = self.display.font()
        font.setPointSize(36)
        self.display.setFont(font)

        # 버튼 그리드
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setContentsMargins(10, 10, 10, 10)

        buttons = [
            ('AC', 0, 0), ('±', 0, 1), ('%', 0, 2), ('÷', 0, 3),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('×', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('−', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3),
            ('0', 4, 0, 1, 2), ('.', 4, 2), ('=', 4, 3),
        ]
        self.buttons = {}

        for btn in buttons:
            text = btn[0]
            row, col = btn[1], btn[2]
            rowspan = btn[3] if len(btn) > 3 else 1
            colspan = btn[4] if len(btn) > 4 else 1

            w = 70 * colspan + (colspan - 1) * grid.spacing()
            h = 70 * rowspan
            b = QPushButton(text)
            b.setFixedSize(w, h)

            # 스타일
            if text in ('÷','×','−','+','='):
                # 오렌지
                b.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #ff9500;
                        color: white;
                        border: none;
                        border-radius: {h//2}px;
                        font-size: 24px;
                    }}
                    QPushButton:pressed {{ background-color: #d17a00; }}
                """)
            elif text in ('AC','±','%'):
                # 연한 회색
                b.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #a5a5a5;
                        color: black;
                        border: none;
                        border-radius: {h//2}px;
                        font-size: 20px;
                    }}
                    QPushButton:pressed {{ background-color: #8e8e8e; }}
                """)
            else:
                # 숫자 버튼 (짙은 회색)
                b.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #333333;
                        color: white;
                        border: none;
                        border-radius: {h//2}px;
                        font-size: 24px;
                    }}
                    QPushButton:pressed {{ background-color: #4d4d4d; }}
                """)

            grid.addWidget(b, row, col, rowspan, colspan)
            self.buttons[text] = b

        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.display)
        main_layout.addLayout(grid)

    """
    각 버튼을 눌렀을 때 일어나는 이벤트 핸들러 할당.
    """
    def _connect_signals(self):
        for key, btn in self.buttons.items():
            btn.clicked.connect(lambda _, k=key: self.on_button_clicked(k))
            # _ == 사용하지 않을 변수임을 의미
            # _는 clicked가 자체적으로 넘기는 체크 상태값(bool)이지만,
            # 현재 우리는 QPushButton이 클릭되었을 때 일어날 이벤트 리스너에 대해 할당중이다. 즉, check 값 필요없으니 버린다는 뜻.
            # _ 없이 k=key를 바로 붙여 사용하면, clicked가 실제 구동되는 양식인 clicked.emit()이라는 메소드의 bool 값 반환으로 인해 k 값이 덮어씌워지는 문제가 있음.
            
            # k = key 사용 이유
            # for문 도는 내부에서 for문 주체로 다루는 값을 람다로 사용할 경우, 람다가 for문의 종료 시 값만 사용하는 문제가 있다고함.
            # 이걸 해결하기위해 k = key로서 for문의 각 단계별 key 값을 저장하여 해결.
            
            # 굳이 람다 쓰는 이유?
            # clicked.connect()의 매개변수로 그냥 self.on_button_clicked(k)를 넣어두면 문제가 발생함
            # 할당이아니라, 그냥 바로 실행되어버린다는 것이다. 우리는 이벤트 리스너를 만들어야하는건데...
            # 이를 방지하기위해 람다를 사용해서 한 번 래핑을 수행하는 것.
    
    
    """
    계산기에 기입된 문자열을 character 단위로 떼어내어 처리
    """
    def _tokenize(self, expr: str):
        """_summary_

        tokens == 숫자 또는 연산자를 저장하는 리스트
        
        """
        tokens, numStr, i = [], '', 0
        ops = set('+-*/') # set에 대해 in 이용하면 해시테이블을 이용해 O(1)시간 만에 찾을 수 있대요... 
        while i < len(expr):
            char = expr[i]
            
            # char가 숫자거나 소수점인 경우
            if char.isdigit() or char == '.':
                numStr += char
                i += 1
                continue # 다음 while문 구동
            
            # 처음 기입된 char가 '-'거나, -의 앞에 다른 연산자가 위치한 경우
            # == '음수' 계산을 목적으로 한다.
            # 문자열의 맨 첫번째 자리 또는 연산자의 다음에 또다시 -가 오는 경우는 음수 표기 외에는 없다.
            if char == '-' and (i == 0 or expr[i-1] in '+-*/'):
                numStr += char 
                i += 1
                continue # 다음 while문 구동
            
            #
            # 위의 continue 구문 if를 통과했다면, 현재 char는 '연산자'이다. 
            #
            
            # 현재까지 적재된 numStr을 tokens에 넣는다 => 숫자 완성
            if numStr:
                tokens.append(numStr) # 
                numStr = ''
            
            # 현재 char가 연산자가 맞다면 tokens에 넣는다 -> 연산자 하나 처리완료
            if char in ops:
                tokens.append(char)
            i += 1
        
        # 위 while문의 numStr의 append는 연산자를 만나야만 수행된다.
        # 즉, 이후 연산자가 없는 마지막 항의 수를 tokens에 append하는 목적. 
        if numStr:
            tokens.append(numStr)
        return tokens

    """
    후위 연산자 표기법 변환
    """
    # tokens: list[str]은 타입 힌트를 의미한다.
    # 타입 힌트는 강제성이 없는 단순 표기 목적이다. 실제로 list[int]형 들어와도 문제 X
    # 이외에도 'function명() -> 반환타입힌트' 와 같이 반환타입힌트도 존재한다. 이것도 강제성 x
    def _to_postfix(self, tokens: list[str]):
        """
        prect == 연산자 우선순위 표기 목적 딕셔너리
        stack == 연산자를 저장해두기위한 별도의 stack. 실제 자료형 상 stack이 아니지만 stack처럼 활용 예정
        """
        
        # 참고 - 만들라는 계산기 양식에 괄호가 없어서 안만들었습니다..
        
        prec = {'+':1,'-':1,'*':2,'/':2}
        output, stack = [], []
        for tk in tokens:
            if tk not in prec: # tk가 문자열(==숫자)인경우
                output.append(tk)
            else: # tk가 연산자인 경우
                # 스택이 비어있지 않고 and stack top의 우선순위가(top 없으면 0) 현재 연산자의 우선순위와 같거나 크다면 
                while stack and prec.get(stack[-1],0) >= prec[tk]:
                    # 즉, top의 우선순위보다 작거나 같은 우선순위를 지닌 연산자를 현재 연산자로 만나는 경우 pop을 반복.
                    output.append(stack.pop()) # stack 내역을 output에 기입한다.
                stack.append(tk)
        
        # 마지막 피연산자까지 tokens를 순회했지만, stack에 연산자가 남아있는 경우를 위해 수행.
        while stack:
            output.append(stack.pop())
        return output
    

    """
    후위연산자 표기법 기반 수행
    """
    def _eval_postfix(self, postfix: list[str]):
        stack = []
        for tk in postfix:
            if tk not in '+-*/': # tk가 피연산자인 경우
                stack.append(float(tk))
            else: # tk가 연산자인경우
                b, a = stack.pop(), stack.pop()
                stack.append({
                    '+': a+b, '-': a-b,
                    '*': a*b, '/': a/b
                }[tk])
        # 최종적으로 stack에는 하나의 값이 남아있어야한다(후위연산 특성상 그렇다. 안남아있거나 2개이상이면 에러임.)
        return stack[0] if stack else 'error' # stack이 남아있을 경우 최종 값 전달.

    def on_button_clicked(self, key):
        # AC
        # 식 문자열 전체 제거
        if key == 'AC':
            self._expr = ''
            self.display.setText('0')
            return

        # =
        if key == '=':
            try:
                expr = (self._expr
                        .replace('×','*')
                        .replace('÷','/')
                        .replace('−','-'))
                tokens  = self._tokenize(expr)
                postfix = self._to_postfix(tokens)
                result  = self._eval_postfix(postfix)
                
                # 나오면 인생망함
                if result == 'error' :
                    raise SyntaxError('후위표기식 계산식 잘못짰으면 이거 나오는데 나오지마라')
                
                # result는 기본적으로 float 자료형 취한다.
                # 그러나 is_integer는 float의 소수점 이하 자리가 0인 경우 int로 인식하는 메소드.
                if result.is_integer():
                    res_str = str(int(result))
                else:
                    res_str = str(result)
                self._expr = res_str
                self.display.setText(res_str)
            except:
                self._expr = ''
                self.display.setText('Error')
            return

        # 숫자 및 소수점 클릭
        if key.isdigit() or key == '.':
            parts = self._expr.replace('×',' ').replace('÷',' ')\
                              .replace('−',' ').replace('+',' ').split()
            if key == '.' and '.' in parts[-1]:
                return
            self._expr += key
            self.display.setText(self._expr)
            return

        # 연산자
        if key in ('+','−','×','÷'):
            if not self._expr: # 계산기 표기식에 아무것도없는 경우(아직 암것도 클릭안한경우)에는 연산자 클릭해도 의미가 없음
                return
            if self._expr[-1] in '+−×÷': # 현재 기입하는 전단계가 연산자인경우 연산자를 변경하기 위해 기존 연산자 제거
                self._expr = self._expr[:-1]
            
            # 연산자 붙이기
            self._expr += key
            
            self.display.setText(self._expr)
            return

if __name__ == "__main__":
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show() # Calculator가 상속한 QWidget 클래스의 메소드. 
    sys.exit(app.exec_()) # app.exec_()가 실행된동안 pyqt 프로그램이 지속적으로 실행중.
    # 즉, app.exec_()의 종료는 pyqt 프로그램이 종료된 이후이다.