import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QStackedWidget, QWidget, 
                             QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt

from ui.deck_selection_screen import DeckSelectionScreen
from ui.language_setup_screen import LanguageSetupScreen
from ui.home_screen import HomeScreen
from ui.stats_screen import StatsScreen
from ui.register_manual import RegisterManualScreen
from ui.register_csv import RegisterCSVScreen
from ui.word_list_screen import WordListScreen
from ui.study_mode_select import StudyModeSelectScreen
from ui.study_screen import StudyScreen
from ui.settings_screen import SettingsScreen

DARK_STYLE = """
QWidget {
    background-color: #2E2E2E;
    color: #FFFFFF;
    font-family: Malgun Gothic;
}
QPushButton {
    background-color: #555555;
    border: 1px solid #777777;
    padding: 5px;
    border-radius: 5px;
}
QPushButton:hover {
    background-color: #777777;
}
QLineEdit, QTextEdit {
    background-color: #444444;
    border: 1px solid #777777;
    padding: 5px;
    border-radius: 5px;
}
"""

DATA_FILE = "data/app_data.json"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # ... (이전과 동일한 초기화 코드)
        self.setWindowTitle("My Voca App")
        self.setGeometry(100, 100, 400, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack, 1)

        nav_bar = QHBoxLayout()
        btn_home = QPushButton("🏠 첫화면")
        btn_stats = QPushButton("📊 통계")
        btn_settings = QPushButton("⚙️ 설정")
        
        nav_bar.addWidget(btn_home)
        nav_bar.addWidget(btn_stats)
        nav_bar.addWidget(btn_settings)
        
        main_layout.addLayout(nav_bar)

        self.current_deck = None
        self.app_data = self.load_data()

        # --- 화면 인스턴스 생성 ---
        self.deck_selection_screen = DeckSelectionScreen()
        self.language_setup_screen = LanguageSetupScreen()
        self.stats_screen = StatsScreen(self)
        self.register_manual_screen = RegisterManualScreen(self)
        self.register_csv_screen = RegisterCSVScreen(self)
        self.word_list_screen = WordListScreen(self)
        self.study_mode_select_screen = StudyModeSelectScreen(self) 
        self.study_screen = StudyScreen(self)
        self.settings_screen = SettingsScreen(self) 
        self.home_screen = HomeScreen(
            switch_to_register_callback=self.open_manual_register,
            switch_to_csv_callback=self.open_csv_register,
            switch_to_wordlist_callback=self.open_word_list,
            switch_to_study_mode_callback=self.open_study_mode_select # [수정]
        )

        # --- 화면 스택에 추가 ---
        self.stack.addWidget(self.deck_selection_screen)
        self.stack.addWidget(self.language_setup_screen)
        self.stack.addWidget(self.home_screen)
        self.stack.addWidget(self.stats_screen)
        self.stack.addWidget(self.register_manual_screen)
        self.stack.addWidget(self.register_csv_screen)
        self.stack.addWidget(self.word_list_screen)
        self.stack.addWidget(self.study_mode_select_screen) 
        self.stack.addWidget(self.study_screen)
        self.stack.addWidget(self.settings_screen)

        # --- 시그널 연결 ---
        # ... (이전 시그널 연결)
        self.deck_selection_screen.deck_selected.connect(self.handle_deck_selection)
        self.deck_selection_screen.deck_deleted.connect(self.handle_deck_deletion)
        self.language_setup_screen.setup_complete.connect(self.handle_setup_complete)
        self.study_mode_select_screen.mode_selected.connect(self.start_study) # [추가]
        
        btn_home.clicked.connect(self.go_to_first_screen)
        btn_stats.clicked.connect(self.go_to_stats_screen)
        btn_settings.clicked.connect(self.go_to_settings_screen)

        self.go_to_first_screen()
        self.show()

    # --- 화면 열기 함수들 ---
    def open_manual_register(self): self.stack.setCurrentWidget(self.register_manual_screen)
    def open_csv_register(self): self.stack.setCurrentWidget(self.register_csv_screen)
    def open_word_list(self): 
        self.word_list_screen.load_words() 
        self.stack.setCurrentWidget(self.word_list_screen)
        
    def open_study_mode_select(self): 
        deck_settings = self.app_data["decks"][self.current_deck]["settings"]
        study_lang = deck_settings.get("study_lang", "학습언어")
        native_lang = deck_settings.get("native_lang", "기본언어")
        self.study_mode_select_screen.set_deck_languages(study_lang, native_lang)
        self.stack.setCurrentWidget(self.study_mode_select_screen)
        
    def start_study(self, mode):
        can_start = self.study_screen.start_new_study_session(mode) 
        if can_start:
            # 시작 가능할 때만 화면 전환
            self.stack.setCurrentWidget(self.study_screen)
        else:
            # 시작 불가능하면 메시지만 표시하고 화면은 전환하지 않음
            QMessageBox.information(self, "완료", "오늘 복습할 단어가 없습니다!")
         
    def go_to_home_screen(self):
        if self.current_deck: self.home_screen.set_deck_name(self.current_deck)
        self.stack.setCurrentWidget(self.home_screen)

    def go_to_settings_screen(self): 
        self.stack.setCurrentWidget(self.settings_screen)

    def go_to_first_screen(self):
        self.deck_selection_screen.update_deck_list(list(self.app_data["decks"].keys()))
        self.stack.setCurrentWidget(self.deck_selection_screen)
        
    def go_to_stats_screen(self):
        self.stats_screen.load_stats_data()
        self.stack.setCurrentWidget(self.stats_screen)
        
    # --- 데이터 로드/저장 및 핸들러 함수들 (이전과 동일) ---
    def load_data(self):
        if not os.path.exists(DATA_FILE):
            os.makedirs("data", exist_ok=True)
            with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump({"decks": {}, "study_log": {}}, f, ensure_ascii=False, indent=2)
            return {"decks": {}, "study_log": {}}
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except json.JSONDecodeError: return {"decks": {}, "study_log": {}}

    def save_data(self):
        with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(self.app_data, f, ensure_ascii=False, indent=2)

    def handle_deck_selection(self, deck_name, is_new):
        if is_new:
            if deck_name not in self.app_data["decks"]:
                self.app_data["decks"][deck_name] = {"settings": {}, "words": []}
                self.save_data()
                self.language_setup_screen.set_deck_name(deck_name)
                self.stack.setCurrentWidget(self.language_setup_screen)
        else:
            self.current_deck = deck_name
            self.go_to_home_screen()

    def handle_setup_complete(self, deck_name, native_lang, study_lang):
        settings = self.app_data["decks"][deck_name]["settings"]
        settings["native_lang"] = native_lang
        settings["study_lang"] = study_lang
        self.save_data()
        self.current_deck = deck_name
        self.go_to_home_screen()

    def handle_deck_deletion(self, deck_name):
        if deck_name in self.app_data["decks"]:
            del self.app_data["decks"][deck_name]
            self.save_data()
            self.deck_selection_screen.update_deck_list(list(self.app_data["decks"].keys()))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)
    window = MainWindow()
    sys.exit(app.exec_())