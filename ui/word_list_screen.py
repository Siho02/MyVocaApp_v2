from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton,
    QMessageBox, QHBoxLayout, QDialog, QLineEdit
)
import json
import os

DATA_PATH = "data/words.json"

class WordListScreen(QWidget):
    def __init__(self, switch_to_home_callback):
        super().__init__()
        self.switch_to_home_callback = switch_to_home_callback
        self.data = []

        self.layout = QVBoxLayout(self)

        self.title = QLabel("📖 저장된 단어 목록")
        self.layout.addWidget(self.title)

        self.word_list = QListWidget()
        self.layout.addWidget(self.word_list)

        self.detail_label = QLabel("")
        self.layout.addWidget(self.detail_label)

        btn_layout = QHBoxLayout()
        self.delete_button = QPushButton("🗑️ 삭제")
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self.delete_selected_word)
        btn_layout.addWidget(self.delete_button)

        self.edit_button = QPushButton("🛠️ 수정")
        self.edit_button.setEnabled(False)
        self.edit_button.clicked.connect(self.edit_selected_word)
        btn_layout.addWidget(self.edit_button)

        self.layout.addLayout(btn_layout)

        self.home_button = QPushButton("← 홈으로")
        self.home_button.clicked.connect(self.switch_to_home_callback)
        self.layout.addWidget(self.home_button)

        self.word_list.itemSelectionChanged.connect(self.show_word_details)
        self.load_words()

    def load_words(self):
        if os.path.exists(DATA_PATH):
            try:
                with open(DATA_PATH, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except json.JSONDecodeError:
                self.data = []
        else:
            self.data = []

        self.word_list.clear()
        for entry in self.data:
            self.word_list.addItem(entry["word"])
        
        self.detail_label.setText("")
        self.delete_button.setEnabled(False)
        self.edit_button.setEnabled(False)

    def show_word_details(self):
        selected_items = self.word_list.selectedItems()
        if not selected_items:
            return

        index = self.word_list.currentRow()
        entry = self.data[index]

        word = entry.get("word", "")
        meanings = ", ".join(entry.get("meaning", []))
        example = entry.get("example", "")

        detail_text = f"📘 단어: {word}\n📚 뜻: {meanings}"
        if example:
            detail_text += f"\n✏️ 예문: {example}"

        self.detail_label.setText(detail_text)
        self.delete_button.setEnabled(True)
        self.edit_button.setEnabled(True)

    def delete_selected_word(self):
        index = self.word_list.currentRow()
        word = self.data[index]["word"]

        confirm = QMessageBox.question(self, "삭제 확인", f"'{word}' 단어를 삭제하시겠습니까?")
        if confirm == QMessageBox.Yes:
            del self.data[index]
            with open(DATA_PATH, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "삭제 완료", f"'{word}' 삭제 완료")
            self.load_words()

    def edit_selected_word(self):
        index = self.word_list.currentRow()
        entry = self.data[index]

        dialog = QDialog(self)
        dialog.setWindowTitle(f"{entry['word']} 수정")
        dialog.setFixedSize(300, 150)
        layout = QVBoxLayout(dialog)

        meaning_input = QLineEdit(", ".join(entry.get("meaning", [])))
        layout.addWidget(QLabel("뜻 (쉼표로 구분):"))
        layout.addWidget(meaning_input)

        example_input = QLineEdit(entry.get("example", ""))
        layout.addWidget(QLabel("예문:"))
        layout.addWidget(example_input)

        save_button = QPushButton("저장")
        layout.addWidget(save_button)

        def save_changes():
            entry["meaning"] = [m.strip() for m in meaning_input.text().split(",") if m.strip()]
            entry["example"] = example_input.text().strip()
            with open(DATA_PATH, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            dialog.accept()
            self.load_words()

        save_button.clicked.connect(save_changes)
        dialog.exec_()
