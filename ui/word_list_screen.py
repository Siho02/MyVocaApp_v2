from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton,
    QMessageBox, QHBoxLayout, QDialog, QLineEdit, QTextEdit
)
from PyQt5.QtCore import Qt

class WordListScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.all_words_in_deck = [] # 현재 덱의 단어 목록을 저장할 변수

        self.layout = QVBoxLayout(self)

        self.title = QLabel("📖 저장된 단어 목록")
        self.title.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.layout.addWidget(self.title)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("검색할 단어 또는 뜻을 입력하세요...")
        self.search_input.textChanged.connect(self.filter_words) # 텍스트가 변경될 때마다 filter_words 함수 호출
        self.layout.addWidget(self.search_input)

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
        self.all_words_in_deck = self.main_window.data_manager.get_words_for_deck(deck_name)
        
        self.word_list_widget.clear()
        self.filter_words() 
        
    def filter_words(self):
        search_text = self.search_input.text().lower()
        self.word_list_widget.clear()

        for entry in self.all_words_in_deck:
            word = entry.get("word", "").lower()
            meanings = " ".join(entry.get("meaning", [])).lower()
            
            # 검색어가 비어있거나, 단어 또는 뜻에 포함되어 있으면 목록에 추가
            if not search_text or search_text in word or search_text in meanings:
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

        selected_word_text = selected_items[0].text()
        entry = next((word for word in self.all_words_in_deck if word["word"] == selected_word_text), None)
        if not entry: return

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
        selected_word_text = self.word_list_widget.currentItem().text()

        word_to_delete_index = -1
        for i, word in enumerate(self.all_words_in_deck):
            if word["word"] == selected_word_text:
                word_to_delete_index = i
                break
        if word_to_delete_index == -1: return
        
        confirm = QMessageBox.question(self, "삭제 확인", f"'{selected_word_text}' 단어를 정말 삭제하시겠습니까?")
        if confirm == QMessageBox.Yes:
            del self.all_words_in_deck[word_to_delete_index]
            self.main_window.data_manager.save_data()
            QMessageBox.information(self, "삭제 완료", f"'{selected_word_text}' 단어가 삭제되었습니다.")
            self.load_words()

    def edit_selected_word(self):
        if not self.word_list_widget.currentItem(): return
        selected_word_text = self.word_list_widget.currentItem().text()

        entry = next((word for word in self.all_words_in_deck if word["word"] == selected_word_text), None)
        if not entry: return

        # --- 수정 다이얼로그 생성 ---
        dialog = QDialog(self)
        dialog.setWindowTitle(f"'{entry['word']}' 수정")
        dialog_layout = QVBoxLayout(dialog)

        dialog_layout.addWidget(QLabel("뜻 (세미콜론(;)으로 구분):"))
        meaning_input = QTextEdit()
        meaning_input.setText(";".join(entry.get("meaning", [])))
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
            
            self.main_window.data_manager.save_data() # 변경사항 저장
            dialog.accept() # 다이얼로그 닫기
            self.load_words() # 목록 새로고침

        save_button.clicked.connect(save_changes)
        dialog.exec_()