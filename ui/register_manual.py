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
        meaning_text = self.meaning_input.toPlainText().strip()
        example = self.example_input.toPlainText().strip()

        if not word or not meaning_text:
            QMessageBox.warning(self, "입력 오류", "단어와 뜻을 모두 입력해주세요.")
            return

        meanings = [m.strip() for m in meaning_text.splitlines() if m.strip()]

        json_path = "data/words.json"
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                existing_words = json.load(f)
        else:
            existing_words = []

        existing_dict = {w['word']: w for w in existing_words}
        message = ""

        if word in existing_dict:
            existing_meanings = set(existing_dict[word]['meaning'])
            new_meanings = set(meanings)
            added_meanings = new_meanings - existing_meanings

            if added_meanings:
                existing_dict[word]['meaning'].extend(list(added_meanings))
                message = f"기존 단어 '{word}'에 뜻 {len(added_meanings)}개를 추가했습니다."
            else:
                message = f"단어 '{word}'는 이미 등록되어 있으며 새로운 뜻이 없습니다."
        else:
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
            existing_words.append(data)
            message = f"새로운 단어 '{word}'를 등록했습니다."
        
        
        # 저장
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(list(existing_dict.values()) + [
            w for w in existing_words if w['word'] not in existing_dict
        ], f, ensure_ascii=False, indent=2)
        
        QMessageBox.information(self, "등록 결과", message)
        
        self.word_input.clear()
        self.meaning_input.clear()
        self.example_input.clear()