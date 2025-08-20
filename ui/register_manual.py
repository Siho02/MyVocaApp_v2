from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QMessageBox
from datetime import datetime, timedelta

class RegisterManualScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        # MainWindow 객체를 통째로 받아와 필요한 기능(데이터, 화면전환)을 사용
        self.main_window = main_window
        
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
        self.home_button = QPushButton("← 이전으로") # '홈으로' 대신 '이전으로'가 더 적합

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

        self.save_button.clicked.connect(self.save_word)
        # '이전으로' 버튼을 누르면 MainWindow의 go_to_home_screen 함수를 호출
        self.home_button.clicked.connect(self.main_window.go_to_home_screen)

    def save_word(self):
        word = self.word_input.text().strip()
        meaning_text = self.meaning_input.toPlainText().strip()
        example = self.example_input.toPlainText().strip()

        if not word or not meaning_text:
            QMessageBox.warning(self, "입력 오류", "단어와 뜻을 모두 입력해주세요.")
            return

        meanings = [m.strip() for m in meaning_text.splitlines() if m.strip()]
        
        # MainWindow를 통해 현재 덱의 단어 목록에 접근
        deck_name = self.main_window.current_deck
        if not deck_name:
            QMessageBox.critical(self, "오류", "선택된 덱이 없습니다.")
            return
            
        word_list = self.main_window.data_manager.app_data["decks"][deck_name]["words"]
        existing_word_entry = next((item for item in word_list if item["word"] == word), None)

        message = ""
        if existing_word_entry: # 이미 단어가 존재할 경우
            original_meanings = set(existing_word_entry.get("meaning", []))
            new_meanings = set(meanings)
            added_meanings = new_meanings - original_meanings
            if added_meanings:
                existing_word_entry['meaning'].extend(list(added_meanings))
                message = f"기존 단어 '{word}'에 뜻 {len(added_meanings)}개를 추가했습니다."
            else:
                message = f"단어 '{word}'는 이미 등록되어 있으며 새로운 뜻이 없습니다."
        else: # 새로운 단어일 경우
            new_word_data = {
                "word": word,
                "meaning": meanings,
                "example": example,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "review_stats": { # 기본 복습 통계
                    "study_to_native": {"correct_cnt": 0, "incorrect_cnt": 0, "prob_mode" : "objective", "last_reviewed": None, "next_review" :(datetime.now() + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M")},
                    "native_to_study": {"correct_cnt": 0, "incorrect_cnt": 0, "prob_mode" : "objective", "last_reviewed": None, "next_review" :(datetime.now() + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M")}
                }
            }
            word_list.append(new_word_data)
            message = f"새로운 단어 '{word}'를 등록했습니다."
        
        self.main_window.data_manager.save_data() # MainWindow를 통해 데이터 저장
        QMessageBox.information(self, "등록 결과", message)
        
        self.word_input.clear()
        self.meaning_input.clear()
        self.example_input.clear()