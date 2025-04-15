# calculator.py

import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QGridLayout, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontMetrics

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.default_font_size = 40  # 기본 디스플레이 폰트 크기
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("iPhone Style Calculator")
        self.setFixedSize(300, 400)

        main_layout = QVBoxLayout()

        # 디스플레이 설정
        self.label = QLabel("0", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label.setFont(QFont("Arial", self.default_font_size))
        self.label.setFixedHeight(60)
        main_layout.addWidget(self.label)

        # 버튼들을 배치할 그리드 레이아웃 생성
        grid_layout = QGridLayout()

        # iPhone 계산기와 유사한 버튼 배열
        btn_texts = [
            ["AC", "±", "%", "÷"],
            ["7",  "8",  "9",  "×"],
            ["4",  "5",  "6",  "-"],
            ["1",  "2",  "3",  "+"],
            ["0",  ".",  "="]
        ]

        # 버튼 생성 및 배치
        for row in range(len(btn_texts)):
            for col in range(len(btn_texts[row])):
                text = btn_texts[row][col]
                btn = QPushButton(text, self)
                btn.setFont(QFont("Arial", 14))
                btn.clicked.connect(self.button_clicked)
                
                if row < 4:
                    grid_layout.addWidget(btn, row, col, 1, 1)
                else:
                    # 5번째 줄: "0" 버튼은 2칸 차지하도록 처리
                    if col == 0:
                        grid_layout.addWidget(btn, row, 0, 1, 2)
                    elif col == 1:
                        grid_layout.addWidget(btn, row, 2, 1, 1)
                    elif col == 2:
                        grid_layout.addWidget(btn, row, 3, 1, 1)

        main_layout.addLayout(grid_layout)
        self.setLayout(main_layout)

    def update_label_text(self, new_text: str):
        """
        label에 표시할 텍스트를 최대 11자로 제한한 후,
        label 너비에 맞게 폰트를 자동 축소 및 확대하는 함수.
        """
        # 최대 11자까지 허용 (11자 초과시 앞 11자만 사용)
        if len(new_text) > 20:
            new_text = new_text[:20]
            
        self.label.setText(new_text)
        
        max_width = self.label.width()
        font = self.label.font()
        metrics = QFontMetrics(font)
        text_width = metrics.horizontalAdvance(new_text)
        
        # 1) 축소: 텍스트 폭이 라벨 너비보다 크면 폰트를 줄인다.
        while text_width > max_width and font.pointSize() > 5:
            font.setPointSize(font.pointSize() - 1)
            self.label.setFont(font)
            metrics = QFontMetrics(font)
            text_width = metrics.horizontalAdvance(new_text)
        
        # 2) 확대: 텍스트 폭이 라벨 너비보다 작고 기본 폰트 크기보다 작으면 폰트를 늘린다.
        while text_width < max_width and font.pointSize() < self.default_font_size:
            # 테스트: 폰트를 1pt 늘린 값으로 텍스트폭을 계산
            test_size = font.pointSize() + 1
            temp_font = QFont(font)
            temp_font.setPointSize(test_size)
            temp_metrics = QFontMetrics(temp_font)
            test_text_width = temp_metrics.horizontalAdvance(new_text)
            if test_text_width > max_width:
                break  # 확대하면 넘치므로 종료
            else:
                font.setPointSize(test_size)
                self.label.setFont(font)
                metrics = QFontMetrics(font)
                text_width = metrics.horizontalAdvance(new_text)
    
    def button_clicked(self):
        button = self.sender()
        value = button.text()

        # AC 버튼: 초기화
        if value == "AC":
            self.update_label_text("0")
            return

        # "=" 버튼: 식 계산
        if value == "=":
            expression = self.label.text()
            # '×'와 '÷' 기호를 파이썬 연산자로 치환
            expression = expression.replace("×", "*").replace("÷", "/")
            try:
                result = eval(expression)
                self.update_label_text(str(result))
            except Exception:
                self.update_label_text("Error")
            return

        # "±" 버튼: 현재 숫자의 부호 전환 (단일 숫자에 대해 동작)
        if value == "±":
            current = self.label.text()
            try:
                num = float(current)
                self.update_label_text(str(-num))
            except Exception:
                pass
            return

        # "%" 버튼: 현재 숫자를 100으로 나누기
        if value == "%":
            current = self.label.text()
            try:
                num = float(current)
                self.update_label_text(str(num / 100))
            except Exception:
                pass
            return

        # 그 외의 경우, 숫자 또는 연산자 추가
        current_text = self.label.text()
        if current_text == "0":
            current_text = ""
        new_text = current_text + value
        self.update_label_text(new_text)

def main():
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
