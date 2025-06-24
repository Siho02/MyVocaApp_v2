from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox
import csv
import json
import os
from datetime import datetime, timedelta

class RegisterCSVScreen(QWidget):
    def __init__(self, switch_to_home_callback):
        super().__init__()
        self.switch_to_home_callback = switch_to_home_callback

        layout = QVBoxLayout()

        self.label = QLabel("CSV 파일을 업로드하여 단어를 등록합니다.")
        layout.addWidget(self.label)

        self.upload_button = QPushButton("📂 CSV 파일 업로드")
        self.upload_button.clicked.connect(self.upload_csv)
        layout.addWidget(self.upload_button)

        self.home_button = QPushButton("← 홈으로")
        self.home_button.clicked.connect(self.switch_to_home_callback)
        layout.addWidget(self.home_button)

        self.setLayout(layout)

    def upload_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "CSV 파일 선택", "", "CSV Files (*.csv)")

        if not file_path:
            return

        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                new_words = []
                duplicate_words = []
                updated_words = []

                for row in reader:
                    word = row['word'].strip()
                    meanings = [m.strip() for m in row['meaning'].split(';') if m.strip()]
                    example = row.get('example', '').strip()

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
                    new_words.append(data)

            # 기존 단어 불러오기
            json_path = "data/words.json"
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    existing_words = json.load(f)
            else:
                existing_words = []

            existing_dict = {w['word']: w for w in existing_words}
            final_words = existing_words.copy()

            for new_word in new_words:
                word = new_word['word']
                if word in existing_dict:
                    existing_meanings = set(existing_dict[word]['meaning'])
                    new_meanings = set(new_word['meaning'])

                    added_meanings = new_meanings - existing_meanings
                    if added_meanings:
                        existing_dict[word]['meaning'].extend(list(added_meanings))
                        updated_words.append(word)
                    else:
                        duplicate_words.append(word)
                else:
                    final_words.append(new_word)

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(final_words, f, ensure_ascii=False, indent=2)

            total = len(new_words)
            updated = len(updated_words)
            duplicated = len(duplicate_words)
            new_entries = total - updated - duplicated

            QMessageBox.information(
                self, "등록 결과",
                f"{total}개의 단어 중\n"
                f"- 중복 단어: {duplicated}개\n"
                f"- 뜻이 추가된 단어: {updated}개\n"
                f"- 신규 등록된 단어: {new_entries}개"
            )

        except Exception as e:
            QMessageBox.critical(self, "오류 발생", f"CSV 파일 처리 중 오류: {str(e)}")