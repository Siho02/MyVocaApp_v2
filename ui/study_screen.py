from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from datetime import datetime
import json
import random

class StudyScreen(QWidget):
    def __init__(self, switch_to_home_callback, mode="kor_to_eng_subjective"):
        super().__init__()
        self.switch_to_home_callback = switch_to_home_callback
        self.mode = mode
        self.quiz_word = None
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout()

        self.label_question = QLabel("뜻을 보고 영어 단어를 입력하세요:")
        self.layout.addWidget(self.label_question)

        self.line_edit_answer = QLineEdit()
        self.layout.addWidget(self.line_edit_answer)

        self.submit_button = QPushButton("제출")
        self.submit_button.clicked.connect(self.check_answer)
        self.layout.addWidget(self.submit_button)

        self.home_button = QPushButton("홈으로")
        self.home_button.clicked.connect(self.switch_to_home_callback)
        self.layout.addWidget(self.home_button)

        self.setLayout(self.layout)
        self.load_next_question()
    
    def load_next_question(self):
        with open("data/words.json", "r", encoding="utf-8") as f:
            words = json.load(f)
        
        # 현재 시간 이전의 복습 대상만 필터링
        now = datetime.now()
        reviewable_words = [
            w for w in words
            if w["review_stats"]["kor_to_eng"]["next_review"] and
               datetime.strptime(w["review_stats"]["kor_to_eng"]["next_review"], "%Y-%m-%d %H:%M") <= now
        ]
    
        #복습할 단어가 없는 경우
        if not reviewable_words:
            QMessageBox.information(self, "완료", "복습할 단어가 없습니다.")
            return

        self.quiz_word = random.choice(reviewable_words)
        meaning = '; '.join(self.quiz_word["meaning"])
        self.label_question.setText(f"뜻: {meaning}")
        self.line_edit_answer.clear()
    
    def check_answer(self):
        user_input = self.line_edit_answer.text().strip().lower()
        correct_answer = self.quiz_word["word"].strip().lower()

        if user_input == correct_answer:
            QMessageBox.information(self, "정답", f"정답입니다! ({correct_answer})")
            self.update_stats(correct=True)
        else:
            QMessageBox.warning(self, "오답", f"오답입니다. 정답은: {correct_answer}")
            self.update_stats(correct=False)

        self.load_next_question()
    
    def update_stats(self, correct):
        now = datetime.now()
        with open("data/words.json", "r", encoding="utf-8") as f:
            words = json.load(f)

        for w in words:
            if w["word"] == self.quiz_word["word"]:
                stats = w["review_stats"]["kor_to_eng"]
                if correct:
                    stats["correct_cnt"] += 1
                else:
                    stats["incorrect_cnt"] += 1

                stats["last_reviewed"] = now.strftime("%Y-%m-%d %H:%M")
                stats["next_review"] = (now + timedelta(hours=6)).strftime("%Y-%m-%d %H:%M")

        with open("data/words.json", "w", encoding="utf-8") as f:
            json.dump(words, f, ensure_ascii=False, indent=2)