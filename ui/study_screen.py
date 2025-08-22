from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QFrame
from datetime import datetime, timedelta
import random, difflib

# review_utils.py가 필요하다면 다시 임포트
# from ui.review_utils import update_study_log, calculate_after_min

class StudyScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.mode = None
        self.word_list_for_review = []
        self.actually_studied_words = []
        self.incorrectly_answered_words = [] 
        self.is_reviewing_mistakes = False 
        self.current_word = None
        self.session_correct = 0
        self.session_incorrect = 0

        self.current_question_text = ""
        self.current_question_lang = ""

        # --- UI 위젯 초기화 ---
        self.layout = QVBoxLayout(self)

        question_layout = QHBoxLayout()
        self.question_label = QLabel("질문이 여기에 표시됩니다.")

        self.speak_button = QPushButton("🔊")
        self.speak_button.setFixedSize(40, 40) # 버튼 크기 고정
        self.speak_button.clicked.connect(self.speak_current_word)
        
        question_layout.addWidget(self.question_label)
        question_layout.addWidget(self.speak_button)

        self.subjective_widget = QWidget()
        subjective_layout = QHBoxLayout(self.subjective_widget)
        self.answer_input = QLineEdit()
        self.submit_button = QPushButton('제출')
        subjective_layout.addWidget(self.answer_input)
        subjective_layout.addWidget(self.submit_button)
        
        # ---객관식용 위젯
        self.objective_widget = QWidget()
        self.objective_layout = QVBoxLayout(self.objective_widget)
        self.finish_button = QPushButton("학습 종료")

        self.layout.addLayout(question_layout)
        self.layout.addWidget(self.subjective_widget)
        self.layout.addWidget(self.objective_widget)
        self.layout.addStretch(1)
        self.layout.addWidget(self.finish_button)

        self.submit_button.clicked.connect(self.check_subjective_answer)
        self.finish_button.clicked.connect(self.finish_study_session)

    def start_new_study_session(self, mode):
        # 세션 시작 -> 모든 상태 초기화
        self.mode = mode
        self.is_reviewing_mistakes = False
        self.incorrectly_answered_words = []
        self.session_correct = 0
        self.session_incorrect = 0
        self.actually_studied_words = []
        
        deck_name = self.main_window.current_deck
        all_words_in_deck = self.main_window.data_manager.get_words_for_deck(deck_name)
        
        now = datetime.now()
        self.word_list_for_review = [
            w for w in all_words_in_deck
            if w.get("review_stats", {}).get(self.mode, {}).get("next_review") and
               datetime.strptime(w['review_stats'][self.mode]['next_review'], "%Y-%m-%d %H:%M") <= now
        ]
        
        self.initial_review_list = list(self.word_list_for_review)

        if not self.word_list_for_review:
            return False
        
        random.shuffle(self.word_list_for_review) # 단어 순서 섞기
        self.next_question()        
        return True
    
    def next_question(self):
        if not self.word_list_for_review:
            self.prompt_for_mistake_review()
            return
            
        self.current_word = self.word_list_for_review.pop()
        stats = self.current_word['review_stats'][self.mode]
        total_reviews = stats['correct_cnt'] + stats['incorrect_cnt']
        accuracy = 0
        if total_reviews > 0:
            accuracy = stats['correct_cnt'] / total_reviews

        if total_reviews >= 10 and accuracy >= 0.85:
            self.create_subjective_question()
        else:
            self.create_objective_question()
        
    def create_objective_question(self):
        self.objective_widget.show()
        self.subjective_widget.hide()
        self._clear_objective_buttons()

        deck_settings = self.main_window.data_manager.get_deck_settings(self.main_window.current_deck)

        if self.mode == 'study_to_native':
            self.current_question_text = self.current_word['word']
            self.current_question_lang = deck_settings.get("study_lang")
            prompt_text = f"'{self.current_question_text}'의 뜻으로 올바른 것은?"
        else:
            self.current_question_text = random.choice(self.current_word['meaning'])
            self.current_question_lang = deck_settings.get("native_lang")
            prompt_text = f"'{self.current_question_text}'에 해당하는 단어는?"

        self.question_label.setText(prompt_text)
        
        correct_answers = self.current_word['meaning'] if self.mode == 'study_to_native' else [self.current_word['word']]
        choices = self._get_distractors(correct_answers)
        choices.append(random.choice(correct_answers))
        random.shuffle(choices)
        for choice in choices:
            btn = QPushButton(choice)
            btn.clicked.connect(lambda _, c=choice: self.check_objective_answer(c))
            self.objective_layout.addWidget(btn)
        self.objective_layout.addStretch(1)

    def create_subjective_question(self):
        self.subjective_widget.show()
        self.objective_widget.hide()
        self.answer_input.clear()
        self.answer_input.setFocus()

        deck_settings = self.main_window.data_manager.get_deck_settings(self.main_window.current_deck)
        
        if self.mode == 'study_to_native':
            self.current_question_text = self.current_word['word']
            self.current_question_lang = deck_settings.get("study_lang")
            prompt = "의 뜻을 입력하세요."
        else:
            self.current_question_text = random.choice(self.current_word['meaning'])
            self.current_question_lang = deck_settings.get("native_lang")
            prompt = "에 해당하는 단어를 입력하세요."

        self.question_label.setText(f"'{self.current_question_text}' {prompt}")

    def check_objective_answer(self, chosen_answer):
        correct_answers = self.current_word['meaning'] if self.mode == 'study_to_native' else [self.current_word['word']]
        is_correct = chosen_answer in correct_answers
        self.process_answer_result(is_correct)

    def check_subjective_answer(self):
        user_answer = self.answer_input.text().strip()
        
        if self.mode == 'study_to_native':
            correct_answers = self.current_word['meaning']
            is_correct = user_answer in correct_answers # 뜻 중 하나만 맞아도 정답

            #아깝게 틀린 경우 확인
            if not is_correct:
                for answer in correct_answers:
                    similarity = difflib.SequenceMatcher(None, user_answer, answer).ratio()
                    if similarity >= 0.8: # 80% 이상 유사하면 '아까운 오답'
                        self.process_answer_result(False, was_close=True, suggestion=answer)
                        return
            self.process_answer_result(is_correct)

        else:
            correct_answer = self.current_word['word']
            is_correct = user_answer.lower() == correct_answer.lower()
            
            if not is_correct:
                similarity = difflib.SequenceMatcher(None, user_answer.lower(), correct_answer.lower()).ratio()
                if similarity >= 0.8:
                    self.process_answer_result(False, was_close=True, suggestion=correct_answer)
                    return
            self.process_answer_result(is_correct)
    
    def process_answer_result(self, is_correct, was_close=False, suggestion=""):
        if self.current_word not in self.actually_studied_words:
            self.actually_studied_words.append(self.current_word)
        
        # 피드백 메시지 생성
        if is_correct:
            self.session_correct += 1
            message = "정답입니다! 🎉"
        else:
            self.session_incorrect += 1 
            if was_close:
                message = f"아깝네요! 혹시 '{suggestion}'을(를) 입력하려고 하셨나요?"
            else:
                message = "오답입니다."
        
        # 주관식의 경우 항상 모든 뜻 보여주기 (객관식 포함)
        all_meanings = ", ".join(self.current_word['meaning'])
        correct_word = self.current_word['word']
        full_answer_text = f"단어: {correct_word}\n전체 뜻: {all_meanings}"
        
        QMessageBox.information(self, "결과", f"{message}\n\n{full_answer_text}")

        # review_stats 업데이트
        if not is_correct and not self.is_reviewing_mistakes:
             self.incorrectly_answered_words.append(self.current_word)
        
        stats = self.current_word['review_stats'][self.mode]
        stats['correct_cnt'] += 1 if is_correct else 0
        stats['incorrect_cnt'] += 1 if not is_correct else 0
        stats['last_reviewed'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        corrects = stats['correct_cnt']
        incorrects = stats['incorrect_cnt']
        if is_correct:
            after_min = 60 * (2 ** corrects) if corrects > 0 else 60
        else:
            after_min = 30
        stats['next_review'] = (datetime.now() + timedelta(minutes=after_min)).strftime('%Y-%m-%d %H:%M')

        self.main_window.data_manager.save_data()
        self.next_question()

    def prompt_for_mistake_review(self):
        if self.incorrectly_answered_words and not self.is_reviewing_mistakes:
            reply = QMessageBox.question(self, '오답 다시 풀기', 
                                         f"오늘 {len(self.incorrectly_answered_words)}개의 단어를 틀렸습니다.\n틀린 단어들을 다시 복습하시겠습니까?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            
            if reply == QMessageBox.Yes:
                self.word_list_for_review = self.incorrectly_answered_words
                self.incorrectly_answered_words = []
                self.is_reviewing_mistakes = True
                random.shuffle(self.word_list_for_review)
                self.next_question()
                return

        QMessageBox.information(self, "학습 완료", "오늘의 학습을 모두 마쳤습니다!")
        self.finish_study_session()

    def finish_study_session(self):
        # 학습 세션 로그 기록 
        deck_name = self.main_window.current_deck
        if not deck_name: return

        deck_data = self.main_window.data_manager.app_data["decks"][deck_name]
        
        if "study_log" not in deck_data:
            deck_data["study_log"] = {}
        
        today_str = datetime.now().strftime("%Y-%m-%d")

        # 오늘 날짜의 로그가 없으면 새로 생성
        if today_str not in deck_data["study_log"]:
            deck_data["study_log"][today_str] = {
                "studied_word_count": 0,
                "correct_count": 0,
                "incorrect_count": 0,
                "studied_words_today": [] # 분 단위 기록은 단순화를 위해 일단 제외
            }
        
        # 로그 업데이트
        today_log = deck_data["study_log"][today_str]

        if "studied_words_today" not in today_log:
            today_log["studied_words_today"] = []

        if not self.is_reviewing_mistakes:
            for word_obj in self.actually_studied_words:
                word = word_obj['word']
                if word not in today_log["studied_words_today"]:
                    today_log["studied_words_today"].append(word)

        today_log["correct_count"] += self.session_correct
        today_log["incorrect_count"] += self.session_incorrect
        today_log["studied_word_count"] = len(today_log["studied_words_today"])

        self.main_window.data_manager.save_data() # 변경사항 저장
        self.main_window.go_to_home_screen()
    
    def speak_current_word(self):
        if self.current_question_text and self.current_question_lang:
            self.main_window.speak(self.current_question_text, self.current_question_lang)
    
    def _clear_objective_buttons(self):
        while self.objective_layout.count():
            child = self.objective_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _get_distractors(self, correct_answers):
        # 전체 덱에서 오답 보기를 추출하는 로직
        all_words_in_deck = self.main_window.data_manager.app_data["decks"][self.main_window.current_deck]["words"]
        
        if self.mode == 'study_to_native':
            distractor_pool = [m for w in all_words_in_deck for m in w['meaning'] if w != self.current_word]
        else:
            distractor_pool = [w['word'] for w in all_words_in_deck if w != self.current_word]
        
        # 중복 제거 및 정답과 겹치지 않게 처리
        distractor_pool = list(set(distractor_pool) - set(correct_answers))
        
        return random.sample(distractor_pool, min(len(distractor_pool), 3))