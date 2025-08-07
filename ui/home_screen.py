from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt 

class HomeScreen(QWidget):
    def __init__(self, switch_to_register_callback, switch_to_csv_callback, switch_to_wordlist_callback, switch_to_study_mode_callback):
        super().__init__()  
        self.switch_to_register_callback = switch_to_register_callback
        self.switch_to_csv_callback = switch_to_csv_callback
        self.switch_to_wordlist_callback = switch_to_wordlist_callback
        self.switch_to_study_mode_callback = switch_to_study_mode_callback
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()

        #상단 제목 만들기
        title = QLabel("단어장")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # 주요 기능 버튼들
        # csv 등록 
        csv_button = QPushButton("📥 CSV로 단어 등록")
        csv_button.clicked.connect(self.switch_to_csv_callback)
        layout.addWidget(csv_button)

        # 수동 등록
        manual_button = QPushButton("✏️ 수동으로 단어 등록")
        manual_button.clicked.connect(self.switch_to_register_callback)
        layout.addWidget(manual_button)
        
        # 등록 단어
        view_button = QPushButton("📚 등록한 단어 전체 보기")
        view_button.clicked.connect(self.switch_to_wordlist_callback)
        layout.addWidget(view_button)

        # 단어 공부하러가기
        study_button = QPushButton("🎯 단어 공부하러 가기")
        study_button.clicked.connect(self.switch_to_study_mode_callback)
        layout.addWidget(study_button)

        layout.addStretch()


        '''
        # 하단 내비게이션
        nav_layout = QHBoxLayout()
        for name in ["🏠 홈", "📊 통계", "⚙️ 설정"]:
            nav_btn = QPushButton(name)
            nav_btn.setStyleSheet("background-color: lightgray;")
            nav_layout.addWidget(nav_btn)
        layout.addLayout(nav_layout)
        '''
        self.setLayout(layout)