from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton,
    QMessageBox, QHBoxLayout, QDialog, QLineEdit, QTextEdit
)

class WordListScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.word_data = [] # 현재 덱의 단어 목록을 저장할 변수

        self.layout = QVBoxLayout(self)

        self.title = QLabel("📖 저장된 단어 목록")
        self.title.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.layout.addWidget(self.title)

        self.word_list_widget = QListWidget()
        self.layout.addWidget(self.word_list_widget)

        self.detail_label = QLabel("단어를 선택하면 상세 정보가 표시됩니다.")
        self.detail_label.setWordWrap(True) # 자동 줄바꿈
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

        self.home_button = QPushButton("← 이전으로")
        self.home_button.clicked.connect(self.main_window.go_to_home_screen)
        self.layout.addWidget(self.home_button)

        self.word_list_widget.itemSelectionChanged.connect(self.show_word_details)
        
    def load_words(self):
        deck_name = self.main_window.current_deck
        if not deck_name:
            self.word_list_widget.clear()
            self.title.setText("선택된 덱이 없습니다")
            return
            
        self.title.setText(f"📖 '{deck_name}' 덱 단어 목록")
        self.word_data = self.main_window.app_data["decks"][deck_name]["words"]
        
        self.word_list_widget.clear()
        for entry in self.word_data:
            self.word_list_widget.addItem(entry["word"])
        
        self.detail_label.setText("단어를 선택하면 상세 정보가 표시됩니다.")
        self.delete_button.setEnabled(False)
        self.edit_button.setEnabled(False)

    def show_word_details(self):
        selected_items = self.word_list_widget.selectedItems()
        if not selected_items:
            self.delete_button.setEnabled(False)
            self.edit_button.setEnabled(False)
            return

        index = self.word_list_widget.currentRow()
        entry = self.word_data[index]

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
        index = self.word_list_widget.currentRow()
        word_to_delete = self.word_data[index]["word"]

        confirm = QMessageBox.question(self, "삭제 확인", f"'{word_to_delete}' 단어를 정말 삭제하시겠습니까?")
        if confirm == QMessageBox.Yes:
            del self.word_data[index] # self.word_data는 실제 app_data의 단어 리스트를 가리킴
            self.main_window.save_data() # 변경사항 저장
            QMessageBox.information(self, "삭제 완료", f"'{word_to_delete}' 단어가 삭제되었습니다.")
            self.load_words() # 목록 새로고침

    def edit_selected_word(self):
        index = self.word_list_widget.currentRow()
        entry = self.word_data[index]

        # --- 수정 다이얼로그 생성 ---
        dialog = QDialog(self)
        dialog.setWindowTitle(f"'{entry['word']}' 수정")
        dialog_layout = QVBoxLayout(dialog)

        dialog_layout.addWidget(QLabel("뜻 (줄바꿈으로 구분):"))
        meaning_input = QTextEdit()
        meaning_input.setText("\n".join(entry.get("meaning", [])))
        dialog_layout.addWidget(meaning_input)

        dialog_layout.addWidget(QLabel("예문:"))
        example_input = QTextEdit(entry.get("example", ""))
        dialog_layout.addWidget(example_input)

        save_button = QPushButton("저장")
        dialog_layout.addWidget(save_button)

        def save_changes():
            # 원본 데이터(entry)를 직접 수정
            entry["meaning"] = [m.strip() for m in meaning_input.toPlainText().splitlines() if m.strip()]
            entry["example"] = example_input.toPlainText().strip()
            
            self.main_window.save_data() # 변경사항 저장
            dialog.accept() # 다이얼로그 닫기
            self.load_words() # 목록 새로고침

        save_button.clicked.connect(save_changes)
        dialog.exec_()