from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from datetime import datetime, timedelta
import json, os, random
from ui.review_utils import update_study_log, calculate_after_min

class StudyScreen(QWidget):
    def __init__(self, switch_to_home_callback, mode="kor_to_eng_subjective"):
        super().__init__()
        self.switch_to_home_callback = switch_to_home_callback
        self.mode = mode
        self.quiz_word = None
        self.session_reviewed = []  
        self.word_list = [] 
        self.all_words = []
        self.start_time = datetime.now().strftime("%H:%M")

        self.init_ui()
        self.load_words()
        self.next_question() 

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.label_question = QLabel("질문이 여기 표시 됩니다.")
        self.answer_input = QLineEdit()
        
        self.submit_button = QPushButton('제출')
        self.submit_button.clicked.connect(self.check_answer)

        self.home_button = QPushButton("홈으로")
        self.home_button.clicked.connect(self.finish_study_and_return_home)
        
        self.layout.addWidget(self.label_question)
        self.layout.addWidget(self.answer_input)
        self.layout.addWidget(self.submit_button)
        self.layout.addWidget(self.home_button)
        
        self.setLayout(self.layout)
    
    def load_words(self):
        file_path = 'data/words.json'
        if os.path.exists(file_path):
            with open(file_path, encoding='utf-8') as f:
                try:
                    all_words = json.load(f)
                except json.JSONDecodeError:
                    all_words = []
        else:
            all_words = []

        now = datetime.now()
        self.word_list = [
            w for w in all_words
            if w.get("review_stats", {}).get(self.mode, {}).get("next_review") is not None and datetime.strptime(w['review_stats'][self.mode]['next_review'], "%Y-%m-%d %H:%M") <= now
        ]
        self.all_words = all_words
    
    def next_question(self):
        if not self.word_list:
            QMessageBox.information(self, "완료", "복습할 단어가 없습니다.")
            self.switch_to_home_callback()
            return
        
        self.clear_layout()
        self.current_word = random.choice(self.word_list)

        stats = self.current_word['review_stats'][self.mode]
        prob_mode = stats.get("prob_mode", "objective")
        correct = stats.get("correct_cnt", 0)
        incorrect = stats.get("incorrect_cnt", 0)
        total = correct + incorrect
        accuracy = correct / total if total > 0 else 0

        
    def check_answer(self):
        user_answer = self.answer_input.text().strip().lower()

        if self.mode == 'eng_to_kor':
            correct_answers = [m.lower() for m in self.current_word['meaning']]
        else:
            correct_answers = [self.current_word['word'].lower()]
        
        is_correct = user_answer in correct_answers

        mode_stat = self.current_word['review_stats'][self.mode]
        if is_correct:
            QMessageBox.information(self, "정답", "정답입니다!")
            mode_stat['correct_cnt'] += 1
        else:
            QMessageBox.information(self, "오답", f"오답입니다!\n정답 : {', '.join(correct_answers)}")
            mode_stat['incorrect_cnt'] += 1

        now = datetime.now()
        mode_stat['last_reviewed'] = now.strftime("%Y-%m-%d %H:%M")
        after_min = calculate_after_min(mode_stat['correct_cnt'], mode_stat['incorrect_cnt'])
        mode_stat['next_review'] = (now + timedelta(minutes=after_min)).strftime('%Y-%m-%d %H:%M')

        self.session_reviewed.append(self.current_word)

        for i, w in enumerate(self.all_words):
            if w['word'] == self.current_word['word']:
                self.all_words[i] = self.current_word
                break

        with open('data/words.json', 'w', encoding='utf-8') as f:
            json.dump(self.all_words, f, ensure_ascii=False, indent=2)
        
        self.word_list.remove(self.current_word)
        self.next_question()
        
    def finish_study_and_return_home(self):
        """홈으로 돌아가기 + 로그 기록"""
        end_time = datetime.now().strftime("%H:%M")

        # ✅ 세션에서 실제로 복습한 단어 기준으로 정오답 수 계산
        correct = sum(w['review_stats'][self.mode]['correct_cnt'] for w in self.session_reviewed)
        incorrect = sum(w['review_stats'][self.mode]['incorrect_cnt'] for w in self.session_reviewed)

        update_study_log("study", correct, incorrect, self.start_time, end_time)

        self.switch_to_home_callback()