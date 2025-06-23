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
        self.csv_button = QPushButton("📥 CSV로 단어 등록")
        self.manual_button = QPushButton("✏️ 수동으로 단어 등록")
        self.view_button = QPushButton("📚 등록한 단어 전체 보기")
        self.study_button = QPushButton("🎯 단어 공부하러 가기")

        self.csv_button.setFixedHeight(40)
        self.manual_button.setFixedHeight(40)
        self.view_button.setFixedHeight(40)
        self.study_button.setFixedHeight(40)

        self.csv_button.clicked.connect(self.csv_register)
        self.manual_button.clicked.connect(self.manual_register)
        self.view_button.clicked.connect(self.view_all)
        self.study_button.clicked.connect(self.study)
        
        layout.addWidget(self.csv_button)
        layout.addWidget(self.manual_button)
        layout.addWidget(self.view_button)
        layout.addWidget(self.study_button)

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