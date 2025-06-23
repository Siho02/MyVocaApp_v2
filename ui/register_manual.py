from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QMessageBox
import json
from datetime import datetime
import os

class RegisterManualScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("단어 입력")
        layout.addWidget(QLabel("단어 : "))
        layout.addWidget(self.word_input)

        self.meaning_input = QTextEdit()
        self.meaning_input.setPlaceholderText("뜻 입력 (줄바꿈으로 여러 개 가능)")
        layout.addWidget(QLabel("뜻:"))
        layout.addWidget(self.meaning_input)

        self.example_input = QTextEdit()
        self.example_input.setPlaceholderText("예문 입력 (선택)")
        layout.addWidget(QLabel("예문:"))
        layout.addWidget(self.example_input)

        self.save_btn = QPushButton("저장하기")
        self.save_btn.clicked.connect(self.save_word)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)

    def save_word(self):
        word = self.word_input.text().strip()
        meanings = [line.strip() for line in self.meaning_input.toPlainText().splitlines() if line.strip()]
        example = self.example_input.toPlainText().strip()

        if not word or not meanings:
            QMessageBox.warning(self, "입력 오류", "단어와 뜻을 모두 입력해주세요.")
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
                    "next_review": (datetime.now().timestamp() + 60 * 180)
                },
                "kor_to_eng": {
                    "correct_cnt": 0,
                    "incorrect_cnt": 0,
                    "last_reviewed": None,
                    "next_review": (datetime.now().timestamp() + 60 * 180)
                }
            }
        }

         # 파일에 저장
        if not os.path.exists("words.json"):
            with open("words.json", "w", encoding="utf-8") as f:
                json.dump([], f)

        with open("words.json", "r", encoding="utf-8") as f:
            words = json.load(f)

        words.append(data)

        with open("words.json", "w", encoding="utf-8") as f:
            json.dump(words, f, ensure_ascii=False, indent=2)

        QMessageBox.information(self, "성공", f"'{word}' 단어가 저장되었습니다.")
        self.word_input.clear()
        self.meaning_input.clear()
        self.example_input.clear()