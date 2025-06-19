from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt 

class HomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()

        #상단 제목 만들기
        title = QLabel("단어장")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # 주요 기능 버튼들
        buttons = [
            ("📥 CSV로 단어 등록", self.csv_register),
            ("✏️ 단어 수동 등록", self.manual_register),
            ("📚 단어 전체 보기", self.view_all),
            ("🎯 단어 공부하러 가기", self.study),
        ]

        for text, func in buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(40)
            btn.clicked.connect(func)
            layout.addWidget(btn)
        
        layout.addStretch()

        # 하단 내비게이션
        nav_layout = QHBoxLayout()
        for name in ["🏠 홈", "📊 통계", "⚙️ 설정"]:
            nav_btn = QPushButton(name)
            nav_btn.setStyleSheet("background-color: lightgray;")
            nav_layout.addWidget(nav_btn)
        layout.addLayout(nav_layout)

        self.setLayout(layout)
    

    def csv_register(self):
        print("CSV 등록 화면으로 이동")

    def manual_register(self):
        print("수동 등록 화면으로 이동")

    def view_all(self):
        print("전체 단어 보기 화면으로 이동")

    def study(self):
        print("단어 공부 화면으로 이동")