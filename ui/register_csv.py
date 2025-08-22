from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox
import csv
from datetime import datetime, timedelta

class RegisterCSVScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()
        self.label = QLabel("CSV 파일을 업로드하여 단어를 등록합니다.")
        layout.addWidget(self.label)

        self.upload_button = QPushButton("📂 CSV 파일 업로드")
        self.upload_button.clicked.connect(self.upload_csv)
        layout.addWidget(self.upload_button)

        self.home_button = QPushButton("← 이전으로")
        self.home_button.clicked.connect(self.main_window.go_to_home_screen)
        layout.addWidget(self.home_button)

        self.setLayout(layout)

    def upload_csv(self):
        deck_name = self.main_window.current_deck
        if not deck_name:
            QMessageBox.critical(self, "오류", "선택된 덱이 없습니다.")
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "CSV 파일 선택", "", "CSV Files (*.csv)")
        if not file_path:
            return

        try:
            with open(file_path, newline='', encoding='utf-8-sig') as csvfile: # utf-8-sig for BOM
                reader = csv.DictReader(csvfile)
                new_words_from_csv = list(reader)

            word_list_in_deck = self.main_window.data_manager.get_words_for_deck(deck_name)
            existing_words_dict = {w['word']: w for w in word_list_in_deck}
            
            added_count = 0
            updated_count = 0
            duplicate_count = 0

            for row in new_words_from_csv:
                word = row.get('word', '').strip()
                if not word: continue

                meanings = [m.strip() for m in row.get('meaning', '').split(';') if m.strip()]
                example = row.get('example', '').strip()

                if word in existing_words_dict:
                    entry = existing_words_dict[word]
                    original_meanings = set(entry.get("meaning", []))
                    new_meanings_set = set(meanings)
                    added_meanings = new_meanings_set - original_meanings
                    
                    if added_meanings:
                        entry['meaning'].extend(list(added_meanings))
                        updated_count += 1
                    else:
                        duplicate_count += 1
                else:
                    new_word_data = {
                        "word": word, "meaning": meanings, "example": example,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "review_stats": {
                            "study_to_native": {"correct_cnt": 0, "incorrect_cnt": 0, "prob_mode" : "objective", "last_reviewed": None, "next_review" :(datetime.now() + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M")},
                            "native_to_study": {"correct_cnt": 0, "incorrect_cnt": 0, "prob_mode" : "objective", "last_reviewed": None, "next_review" :(datetime.now() + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M")}
                        }
                    }
                    word_list_in_deck.append(new_word_data)
                    added_count += 1

            self.main_window.data_manager.save_data()

            QMessageBox.information(
                self, "등록 결과",
                f"총 {len(new_words_from_csv)}개의 단어 처리 완료\n"
                f"- 신규 등록: {added_count}개\n"
                f"- 뜻 추가(업데이트): {updated_count}개\n"
                f"- 중복: {duplicate_count}개"
            )

        except Exception as e:
            QMessageBox.critical(self, "오류 발생", f"CSV 파일 처리 중 오류가 발생했습니다: {str(e)}")