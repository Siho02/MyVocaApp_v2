from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGridLayout, QFrame, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal

class LanguageSetupScreen(QWidget):
    # (str) deck_name, (str) native_lang, (str) study_lang
    setup_complete = pyqtSignal(str, str, str) 

    def __init__(self):
        super().__init__()
        self.deck_name = ""
        self.native_lang = None
        self.study_lang = None
        
        self.native_lang_buttons = {}
        self.study_lang_buttons = {}

        # --- 전체 레이아웃 ---
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        self.title_label = QLabel("Deck Name")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(self.title_label)
        
        # --- 두 개의 열을 담을 수평 레이아웃 ---
        columns_layout = QHBoxLayout()

        # --- 왼쪽 열: 기본 언어 ---
        native_group = QGroupBox("기본 언어 (편한 언어)")
        native_vbox = QVBoxLayout()
        self.native_lang_buttons = self.create_language_buttons(native_vbox, self.on_native_lang_selected)
        native_group.setLayout(native_vbox)
        columns_layout.addWidget(native_group)

        # --- 오른쪽 열: 학습 언어 ---
        study_group = QGroupBox("학습할 언어")
        study_vbox = QVBoxLayout()
        self.study_lang_buttons = self.create_language_buttons(study_vbox, self.on_study_lang_selected)
        study_group.setLayout(study_vbox)
        columns_layout.addWidget(study_group)

        layout.addLayout(columns_layout)
        
        # --- 확인 버튼 ---
        self.confirm_button = QPushButton("선택 완료")
        self.confirm_button.setEnabled(False)
        self.confirm_button.clicked.connect(self.on_confirm)
        layout.addWidget(self.confirm_button)

    def create_language_buttons(self, layout, slot_function):
        """언어 버튼 그룹을 생성하고 레이아웃에 추가하는 헬퍼 함수"""
        buttons = {}
        languages = ["한국어", "English", "German", "日本語", "Castellano", "Française", "Русский", "العربية"]
        for lang in languages:
            btn = QPushButton(lang)
            btn.setCheckable(True) # 버튼이 선택 상태를 유지하도록 설정
            btn.clicked.connect(lambda _, l=lang: slot_function(l))
            layout.addWidget(btn)
            buttons[lang] = btn
        return buttons

    def set_deck_name(self, name):
        """새 덱 설정을 시작할 때 호출되는 함수"""
        self.deck_name = name
        self.title_label.setText(f"'{name}' 덱 설정")
        
        # 모든 선택 초기화
        self.native_lang = None
        self.study_lang = None
        for btn_dict in [self.native_lang_buttons, self.study_lang_buttons]:
            for btn in btn_dict.values():
                btn.setChecked(False)
                btn.setStyleSheet("")
        self.confirm_button.setEnabled(False)

    def on_native_lang_selected(self, lang):
        # 이전에 선택된 버튼이 있었다면 선택 해제
        if self.native_lang and self.native_lang != lang:
            self.native_lang_buttons[self.native_lang].setChecked(False)
            self.native_lang_buttons[self.native_lang].setStyleSheet("")
        
        self.native_lang = lang
        # 현재 선택된 버튼 스타일 적용
        self.native_lang_buttons[lang].setStyleSheet("background-color: #AED6F1;")
        self.check_selection_complete()

    def on_study_lang_selected(self, lang):
        if self.study_lang and self.study_lang != lang:
            self.study_lang_buttons[self.study_lang].setChecked(False)
            self.study_lang_buttons[self.study_lang].setStyleSheet("")

        self.study_lang = lang
        self.study_lang_buttons[lang].setStyleSheet("background-color: #AED6F1;")
        self.check_selection_complete()

    def check_selection_complete(self):
        """기본 언어와 학습 언어가 모두 선택되었는지 확인"""
        if self.native_lang and self.study_lang:
            self.confirm_button.setEnabled(True)
        else:
            self.confirm_button.setEnabled(False)
    
    def on_confirm(self):
        """선택 완료 버튼 클릭 시 실행"""
        self.setup_complete.emit(self.deck_name, self.native_lang, self.study_lang)