from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

class StudyModeSelectScreen(QWidget):
    def __init__(self, switch_to_home, switch_to_study):
        super().__init__()
        self.switch_to_home = switch_to_home
        self.switch_to_study = switch_to_study
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        label = QLabel("📘 어떤 방식으로 공부할까요?")
        layout.addWidget(label)

        # 영어 → 한국어 버튼
        eng_to_kor_button = QPushButton("영어 → 한국어")
        eng_to_kor_button.clicked.connect(lambda: self.switch_to_study("eng_to_kor"))
        layout.addWidget(eng_to_kor_button)

        # 한국어 → 영어 버튼
        kor_to_eng_button = QPushButton("한국어 → 영어")
        kor_to_eng_button.clicked.connect(lambda: self.switch_to_study("kor_to_eng"))
        layout.addWidget(kor_to_eng_button)

        # 홈으로 돌아가기 버튼
        home_button = QPushButton("🏠 홈으로")
        home_button.clicked.connect(self.switch_to_home)
        layout.addWidget(home_button)

        self.setLayout(layout)
