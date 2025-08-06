from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from datetime import datetime, timedelta
import json, os, random
from ui.review_utils import update_study_log, calculate_after_min

class StudyScreen(QWidget):
    def __init__(self, switch_to_home_callback, mode="eng_to_kor"):
        super().__init__()
        self.switch_to_home_callback = switch_to_home_callback
        self.mode = mode
        self.quiz_word = None
        self.word_list = []
        self.all_words = []
        self.session_reviewed = []
        self.start_time = datetime.now().strftime("%H:%M")

        self.init_ui()
        self.load_words()
        self.next_question()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.label_question = QLabel("질문이 여기 표시 됩니다.")
        self.answer_input = QLineEdit()
        self.submit_button = QPushButton('제출')
        self.submit_button.clicked.connect(self.check_subjective_answer)
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
            if w.get("review_stats", {}).get(self.mode, {}).get("next_review") is not None and
               datetime.strptime(w['review_stats'][self.mode]['next_review'], "%Y-%m-%d %H:%M") <= now
        ]
        self.all_words = all_words

    def next_question(self):
        if not self.word_list:
            QMessageBox.information(self, "완료", "복습할 단어가 없습니다.")
            self.finish_study_and_return_home()
            return

        self.clear_layout()
        self.current_word = random.choice(self.word_list)

        stats = self.current_word['review_stats'][self.mode]
        prob_mode = stats.get("prob_mode", "objective")
        correct = stats.get("correct_cnt", 0)
        incorrect = stats.get("incorrect_cnt", 0)
        total = correct + incorrect
        accuracy = correct / total if total > 0 else 0

        if total >= 10 and accuracy >= 0.85:
            stats['prob_mode'] = 'subjective'
            prob_mode = 'subjective'
        else:
            stats['prob_mode'] = 'objective'

        for i, w in enumerate(self.all_words):
            if w['word'] == self.current_word['word']:
                self.all_words[i] = self.current_word
                break

        with open('data/words.json', 'w', encoding='utf-8') as f:
            json.dump(self.all_words, f, ensure_ascii=False, indent=2)

        if prob_mode == 'subjective':
            self.show_subjective_question()
        else:
            if self.mode == 'eng_to_kor':
                self.show_objective_eng_to_kor()
            else:
                self.show_objective_kor_to_eng()

    def show_objective_eng_to_kor(self):
        self.clear_layout()
        correct = random.choice(self.current_word['meaning'])
        all_meanings = [m for w in self.all_words if w['word'] != self.current_word['word'] for m in w.get("meaning", [])]
        wrong_choices = random.sample(all_meanings, 3) if len(all_meanings) >= 3 else all_meanings
        options = wrong_choices + [correct]
        random.shuffle(options)

        self.label_question.setText(f"'{self.current_word['word']}'의 뜻은?")
        for option in options:
            btn = QPushButton(option)
            btn.clicked.connect(lambda _, c=option: self.check_objective_answer(c, correct))
            self.layout.addWidget(btn)

    def show_objective_kor_to_eng(self):
        self.clear_layout()
        correct = self.current_word['word']
        meaning = random.choice(self.current_word['meaning'])
        all_words = [w['word'] for w in self.all_words if w['word'] != correct]
        wrong_choices = random.sample(all_words, 3) if len(all_words) >= 3 else all_words
        options = wrong_choices + [correct]
        random.shuffle(options)

        self.label_question.setText(f"'{meaning}' 에 해당하는 영어 단어는?")
        for option in options:
            btn = QPushButton(option)
            btn.clicked.connect(lambda _, c=option: self.check_objective_answer(c, correct))
            self.layout.addWidget(btn)

    def show_subjective_question(self):
        self.clear_layout()
        if self.mode == 'eng_to_kor':
            question = self.current_word['word']
            self.label_question.setText(f"'{question}'의 뜻을 입력하세요:")
        else:
            question = ", ".join(self.current_word['meaning'])
            self.label_question.setText(f"'{question}'에 해당하는 영어 단어는?")

        self.answer_input = QLineEdit()
        self.submit_button = QPushButton('제출')
        self.submit_button.clicked.connect(self.check_subjective_answer)
        self.layout.addWidget(self.answer_input)
        self.layout.addWidget(self.submit_button)

    def check_objective_answer(self, selected, correct):
        is_correct = selected.strip().lower() == correct.strip().lower()
        self.process_answer(is_correct)

    def check_subjective_answer(self):
        user_answer = self.answer_input.text().strip().replace(" ", "")
        correct_answers = [m.replace(" ", "") for m in self.current_word['meaning']] if self.mode == 'eng_to_kor' else [self.current_word['word'].replace(" ", "")]
        is_correct = user_answer in correct_answers
        self.process_answer(is_correct)

    def process_answer(self, is_correct):
        if not self.current_word or not self.word_list:
            return 
        
        stats = self.current_word['review_stats'][self.mode]
        if is_correct:
            QMessageBox.information(self, "정답", "정답입니다!")
            stats['correct_cnt'] += 1
            update_study_log("study", 
                             correct=1, 
                             incorrect=0, 
                             start_time=self.start_time, 
                             end_time=datetime.now().strftime("%H:%M"))
        else:
            QMessageBox.information(self, "오답", "오답입니다!")
            stats['incorrect_cnt'] += 1
            update_study_log("study", 
                             correct=0, 
                             incorrect=1, 
                             start_time=self.start_time, 
                             end_time=datetime.now().strftime("%H:%M"))
            
        now = datetime.now()
        stats['last_reviewed'] = now.strftime("%Y-%m-%d %H:%M")
        after_min = calculate_after_min(stats['correct_cnt'], stats['incorrect_cnt'])
        stats['next_review'] = (now + timedelta(minutes=after_min)).strftime('%Y-%m-%d %H:%M')

        self.session_reviewed.append(self.current_word)

        for i, w in enumerate(self.all_words):
            if w['word'] == self.current_word['word']:
                self.all_words[i] = self.current_word
                break

        with open("data/words.json", "w", encoding="utf-8") as f:
            json.dump(self.all_words, f, ensure_ascii=False, indent=2)

        self.word_list.remove(self.current_word)
        self.last_question_time = datetime.now().strftime("%H:%M")
        self.next_question()

    def finish_study_and_return_home(self):
        end_time = datetime.now().strftime("%H:%M")
        update_study_log("study", 
                         correct=0, 
                         incorrect=0, 
                         start_time = self.start_time, 
                         end_time = end_time)

        log_path = "data/study_log.json"
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                log_data = json.load(f)
            today = datetime.now().strftime("%Y=%m=%d")
            if today in log_data:
                log_data[today]['studied_word_count'] += len(self.session_reviewed)
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)

        self.switch_to_home_callback()

    def clear_layout(self):
        for i in reversed(range(self.layout.count())):
            item = self.layout.itemAt(i)
            widget = item.widget()
            if widget is not None and widget != self.label_question:
                widget.setParent(None)
        
        '''
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        '''