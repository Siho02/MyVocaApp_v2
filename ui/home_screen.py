from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt 

class HomeScreen(QWidget):
    def __init__(self, switch_to_register_callback, switch_to_csv_callback, switch_to_wordlist_callback, switch_to_study_mode_callback, switch_to_deck_stats_callback):
        super().__init__()  
        self.switch_to_register_callback = switch_to_register_callback
        self.switch_to_csv_callback = switch_to_csv_callback
        self.switch_to_wordlist_callback = switch_to_wordlist_callback
        self.switch_to_study_mode_callback = switch_to_study_mode_callback
        self.switch_to_deck_stats_callback = switch_to_deck_stats_callback

        layout = QVBoxLayout()

        self.title = QLabel("") 
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(self.title)

        # --- 기능 버튼들 ---
        csv_button = QPushButton("📥 CSV로 단어 등록")
        csv_button.clicked.connect(self.switch_to_csv_callback)
        layout.addWidget(csv_button)

        manual_button = QPushButton("✏️ 수동으로 단어 등록")
        manual_button.clicked.connect(self.switch_to_register_callback)
        layout.addWidget(manual_button)
        
        view_button = QPushButton("📚 등록한 단어 전체 보기")
        view_button.clicked.connect(self.switch_to_wordlist_callback)
        layout.addWidget(view_button)

        study_button = QPushButton("🎯 단어 공부하러 가기")
        study_button.clicked.connect(self.switch_to_study_mode_callback)
        layout.addWidget(study_button)

        # 덱별 통계 보기 버튼
        deck_stats_button = QPushButton("📊 이 덱의 통계 보기")
        deck_stats_button.clicked.connect(self.switch_to_deck_stats_callback)
        layout.addWidget(deck_stats_button)

        layout.addStretch()
        self.setLayout(layout)

    def set_deck_name(self, deck_name):
        """
        main.py로부터 덱 이름을 받아와 제목 라벨의 텍스트를 변경합니다.
        """
        self.title.setText(deck_name)
