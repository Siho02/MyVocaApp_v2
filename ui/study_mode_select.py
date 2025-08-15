from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import pyqtSignal

class StudyModeSelectScreen(QWidget):
    mode_selected = pyqtSignal(str)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout(self)

        self.label = QLabel("📘 어떤 방식으로 공부할까요?")
        layout.addWidget(self.label)

        # study language → native language 버튼
        self.study_to_native_button = QPushButton()
        self.study_to_native_button.clicked.connect(lambda: self.mode_selected.emit("study_to_native"))
        layout.addWidget(self.study_to_native_button)

        # native language → study language 버튼
        self.native_to_study_button = QPushButton()
        self.native_to_study_button.clicked.connect(lambda: self.mode_selected.emit("native_to_study"))
        layout.addWidget(self.native_to_study_button)

        back_button = QPushButton("← 이전으로")
        back_button.clicked.connect(self.main_window.go_to_home_screen)
        layout.addWidget(back_button)

    def set_deck_languages(self, study_lang, native_lang):
        """main.py로부터 언어 설정을 받아 버튼 텍스트를 업데이트"""
        self.study_to_native_button.setText(f"{study_lang} → {native_lang}")
        self.native_to_study_button.setText(f"{native_lang} → {study_lang}")
