from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QInputDialog, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal

class DeckSelectionScreen(QWidget):
    deck_selected = pyqtSignal(str, bool) 
    deck_deleted = pyqtSignal(str) # 덱 삭제를 위한 새 시그널

    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignTop)

        title = QLabel("Word Books")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        main_layout.addWidget(title)
        
        content_layout = QHBoxLayout()
        
        self.add_deck_button = QPushButton("+")
        self.add_deck_button.setFixedSize(60, 60)
        self.add_deck_button.setStyleSheet("""
            QPushButton { font-size: 30px; color: white; background-color: #3498DB; border-radius: 30px; }
            QPushButton:hover { background-color: #2980B9; }
        """)
        self.add_deck_button.clicked.connect(self.create_new_deck)
        content_layout.addWidget(self.add_deck_button, 0, Qt.AlignTop)

        self.deck_list_layout = QVBoxLayout()
        content_layout.addLayout(self.deck_list_layout)
        main_layout.addLayout(content_layout)

    def update_deck_list(self, deck_names):
        for i in reversed(range(self.deck_list_layout.count())): 
            item = self.deck_list_layout.takeAt(i)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # QHBoxLayout 안의 위젯들도 삭제
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
        
        for name in deck_names:
            # --- 각 덱을 위한 수평 레이아웃 생성 ---
            deck_row = QHBoxLayout()
            
            # 덱 이름 버튼
            deck_button = QPushButton(name)
            deck_button.setStyleSheet("text-align: left; padding: 10px;")
            deck_button.clicked.connect(lambda _, n=name: self.deck_selected.emit(n, False))
            
            # 삭제 버튼
            delete_button = QPushButton("🗑️")
            delete_button.setFixedSize(40, 40)
            delete_button.clicked.connect(lambda _, n=name: self.confirm_delete_deck(n))
            
            deck_row.addWidget(deck_button)
            deck_row.addWidget(delete_button)
            
            self.deck_list_layout.addLayout(deck_row)
            
        self.deck_list_layout.addStretch()

    def create_new_deck(self):
        text, ok = QInputDialog.getText(self, '새 덱 만들기', '덱의 이름을 입력하세요:')
        if ok and text:
            self.deck_selected.emit(text, True)
            
    def confirm_delete_deck(self, deck_name):
        reply = QMessageBox.question(self, '삭제 확인', 
                                     f"'{deck_name}' 덱을 정말로 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.deck_deleted.emit(deck_name)