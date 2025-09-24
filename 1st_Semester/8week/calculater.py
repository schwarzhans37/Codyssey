import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QGridLayout, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontMetrics

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.default_font_size = 40
        # Internal 상태
        self.current_input = "0"
        self.operator = None
        self.operand = None
        
        self.initUI()

    def initUI(self):
        self.setWindowTitle("iPhone Style Calculator")
        self.setFixedSize(300, 400)

        main_layout = QVBoxLayout()

        # 디스플레이
        self.label = QLabel(self.current_input, self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label.setFont(QFont("Arial", self.default_font_size))
        self.label.setFixedHeight(60)
        main_layout.addWidget(self.label)

        # 버튼
        grid_layout = QGridLayout()
        btn_texts = [
            ["AC", "±", "%", "÷"],
            ["7",  "8",  "9",  "×"],
            ["4",  "5",  "6",  "-"],
            ["1",  "2",  "3",  "+"],
            ["0",  ".",  "="]
        ]

        for row, texts in enumerate(btn_texts):
            for col, text in enumerate(texts):
                btn = QPushButton(text, self)
                btn.setFont(QFont("Arial", 14))
                btn.clicked.connect(self.button_clicked)
                if row < 4:
                    grid_layout.addWidget(btn, row, col, 1, 1)
                else:
                    if col == 0:
                        grid_layout.addWidget(btn, row, 0, 1, 2)
                    elif col == 1:
                        grid_layout.addWidget(btn, row, 2, 1, 1)
                    elif col == 2:
                        grid_layout.addWidget(btn, row, 3, 1, 1)

        main_layout.addLayout(grid_layout)
        self.setLayout(main_layout)

    # 사칙 연산 메소드
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b

    def divide(self, a, b):
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return a / b

    # 초기화, 부호 전환, 퍼센트
    def reset(self):
        self.current_input = "0"
        self.operator = None
        self.operand = None
        self.update_label_text(self.current_input)

    def negative_positive(self):
        if self.current_input.startswith("-"):
            self.current_input = self.current_input[1:]
        else:
            if self.current_input != "0":
                self.current_input = "-" + self.current_input
        self.update_label_text(self.current_input)

    def percent(self):
        try:
            num = float(self.current_input)
            num = num / 100
            self.current_input = str(num)
            self.update_label_text(self.current_input)
        except Exception:
            self.update_label_text("Error")

    # 결과 계산
    def equal(self):
        if self.operator is None or self.operand is None:
            return
        try:
            current = float(self.current_input)
            if self.operator == "+":
                result = self.add(self.operand, current)
            elif self.operator == "-":
                result = self.subtract(self.operand, current)
            elif self.operator == "×":
                result = self.multiply(self.operand, current)
            elif self.operator == "÷":
                result = self.divide(self.operand, current)
            # 소수점 6자리 이하로 반올림
            if not float(result).is_integer():
                result = round(result, 6)
            # 결과 포맷 (정수면 소수점 제거)
            if float(result).is_integer():
                self.current_input = str(int(result))
            else:
                self.current_input = str(result)
            self.update_label_text(self.current_input)
        except ZeroDivisionError:
            self.update_label_text("Error")
        except OverflowError:
            self.update_label_text("Error")
        finally:
            self.operator = None
            self.operand = None

    # 숫자 입력
    def press_digit(self, digit):
        if self.current_input == "0":
            self.current_input = digit
        else:
            self.current_input += digit
        self.update_label_text(self.current_input)

    # 소수점 입력
    def press_decimal(self):
        if "." not in self.current_input:
            self.current_input += "."
            self.update_label_text(self.current_input)

    # 연산자 입력
    def press_operator(self, op):
        try:
            self.operand = float(self.current_input)
        except ValueError:
            self.operand = 0
        self.operator = op
        self.current_input = "0"

    # UI 업데이트
    def update_label_text(self, new_text: str):
        self.label.setText(new_text)
        # 폰트 크기 초기화
        font = QFont("Arial", self.default_font_size)
        self.label.setFont(font)
        max_width = self.label.width() - 10
        metrics = QFontMetrics(font)
        text_width = metrics.horizontalAdvance(new_text)
        # 텍스트가 넘어가면 폰트 크기 감소
        while text_width > max_width and font.pointSize() > 5:
            font.setPointSize(font.pointSize() - 1)
            self.label.setFont(font)
            metrics = QFontMetrics(font)
            text_width = metrics.horizontalAdvance(new_text)

    # 버튼 클릭 핸들러
    def button_clicked(self):
        btn = self.sender()
        value = btn.text()

        if value == "AC":
            self.reset()
            return
        if value == "±":
            self.negative_positive()
            return
        if value == "%":
            self.percent()
            return
        if value in ["+", "-", "×", "÷"]:
            self.press_operator(value)
            return
        if value == ".":
            self.press_decimal()
            return
        if value == "=":
            self.equal()
            return
        # 숫자
        self.press_digit(value)


def main():
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
