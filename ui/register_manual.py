from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QMessageBox
import json
from datetime import datetime, timedelta
import os

class RegisterManualScreen(QWidget):
    def __init__(self, switch_to_home_callback):
        super().__init__()
        self.switch_to_home_callback = switch_to_home_callback
        
         # --- 위젯 생성 ---
        self.word_label = QLabel("단어 :")
        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("단어 입력")

        self.meaning_label = QLabel("뜻 :")
        self.meaning_input = QTextEdit()
        self.meaning_input.setPlaceholderText("뜻 입력 (줄바꿈으로 여러 개 가능)")

        self.example_label = QLabel("예문 :")
        self.example_input = QTextEdit()
        self.example_input.setPlaceholderText("예문 입력 (선택)")

        self.save_button = QPushButton("저장하기")
        self.home_button = QPushButton("← 홈으로")

        # --- 레이아웃 구성 ---
        layout = QVBoxLayout()
        layout.addWidget(self.word_label)
        layout.addWidget(self.word_input)
        layout.addWidget(self.meaning_label)
        layout.addWidget(self.meaning_input)
        layout.addWidget(self.example_label)
        layout.addWidget(self.example_input)
        layout.addWidget(self.save_button)
        layout.addWidget(self.home_button)

        self.setLayout(layout)

        # --- 버튼 동작 연결 ---
        self.save_button.clicked.connect(self.save_word)
        self.home_button.clicked.connect(self.switch_to_home_callback)

    def save_word(self):
        word = self.word_input.text().strip()
        meanings = [line.strip() for line in self.meaning_input.toPlainText().splitlines() if line.strip()]
        example = self.example_input.toPlainText().strip()

        if not word or not meanings:
            QMessageBox.warning(self, "입력 오류", "단어와 뜻을 모두 입력해주세요.")
            return

        # 파일에 저장 
        file_path = "data/words.json"

        if not os.path.exists("data"):
            os.makedirs("data")

        try:
            with open(file_path, "r", encoding='utf-8') as f:
                words = json.load(f)
        except FileNotFoundError:
            words = []

        for w in words:
            if w["word"] == word:
                QMessageBox.warning(self, "중복 단어", f"이미 등록 된 단어입니다. : {word}")
                return
            
        data = {
            "word": word,
            "meaning": meanings,
            "example": example,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "review_stats": {
                "eng_to_kor": {
                    "correct_cnt": 0,
                    "incorrect_cnt": 0,
                    "last_reviewed": None,
                    "next_review" :(datetime.now() + timedelta(minutes=60)).strftime("%Y-%m-%d %H:%M")
                },
                "kor_to_eng": {
                    "correct_cnt": 0,
                    "incorrect_cnt": 0,
                    "last_reviewed": None,
                    "next_review" :(datetime.now() + timedelta(minutes=60)).strftime("%Y-%m-%d %H:%M")
                }
            }
        }

        # 저장
        words.append(data)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(words, f, ensure_ascii=False, indent=2)
        
        QMessageBox.information(self, "성공", f"'{word}' 단어가 저장되었습니다.")
        
        self.word_input.clear()
        self.meaning_input.clear()
        self.example_input.clear()