import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QStackedWidget, QWidget, 
                             QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from data_manager import DataManager
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
        self.data_manager = DataManager()
        self.current_deck = None

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
        deck_settings = self.data_manager.app_data["decks"][self.current_deck]["settings"]
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
        decks = self.data_manager.app_data['decks']
        self.deck_selection_screen.update_deck_list(list(decks.keys()))
        self.stack.setCurrentWidget(self.deck_selection_screen)
        
    def go_to_stats_screen(self):
        self.stats_screen.load_stats_data()
        self.stack.setCurrentWidget(self.stats_screen)
        
    def handle_deck_selection(self, deck_name, is_new):
        decks = self.data_manager.app_data['decks']
        if is_new:
            if deck_name not in decks:
                decks[deck_name] = {'settings' : {}, 'words' : []}
                self.data_manager.save_data()
                self.language_setup_screen.set_deck_name(deck_name)
                self.stack.setCurrentWidget(self.language_setup_screen)
        else:
            self.current_deck = deck_name
            self.go_to_home_screen()

    def handle_setup_complete(self, deck_name, native_lang, study_lang):
        settings = self.data_manager.app_data["decks"][deck_name]["settings"]
        settings["native_lang"] = native_lang
        settings["study_lang"] = study_lang
        self.data_manager.save_data()
        self.current_deck = deck_name
        self.go_to_home_screen()

    def handle_deck_deletion(self, deck_name):
        decks = self.data_manager.app_data['decks']
        if deck_name in self.app_data["decks"]:
            del decks[deck_name]
            self.data_manager.save_data()
            self.deck_selection_screen.update_deck_list(list(decks.keys()))


if __name__ == "__main__":
    from PyQt5.QtGui import QFontDatabase 
    import sys, os
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    font_file_name = 'HMKMMAG.ttf'
    font_path = os.path.join(os.path.dirname(__file__), "resources", "fonts", font_file_name)
    
    print('-' * 30)
    print(f"EXECUTING FILE: {__file__}") # 현재 실행 중인 파일 이름 출력
    print(f"1. Attempting to load font from: {font_path}")

    font_id = QFontDatabase.addApplicationFont(font_path)
    font_family = "Malgun Gothic"
    
    if font_id < 0:
        print("2. FAILED to load font. Please check the file path and integrity.")
    else:
        print("2. SUCCESS: Font loaded into the application.")
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            font_family = font_families[0]
            print(f"3. Detected Font Family Name: '{font_family}'")
        else:
            print("3. FAILED: Could not retrieve font family name.")

    print(f"4. Applying stylesheet with font-family: '{font_family}'")
    print("-" * 30)


    DARK_STYLE = """
    QWidget {
        background-color: #2E3440; 
        color: #ECEFF4;
        font-family: {font_family};
        font-size: 11pt;
    }
    QPushButton {
        background-color: #4C566A;
        color: #ECEFF4;
        border: 1px solid #4C566A;
        padding: 8px;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #5E81AC;
    }
    QPushButton:pressed {
        background-color: #81A1C1;
    }
    QLineEdit, QTextEdit {
        background-color: #3B4252;
        border: 1px solid #4C566A;
        padding: 5px;
        border-radius: 5px;
    }
    QGroupBox {
        font-weight: bold;
        border: 1px solid #4C566A;
        border-radius: 5px;
        margin-top: 10px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 0 3px;
    }

    /* 라벨 스타일 */
    QLabel {
        color: #ECEFF4;
    }
    QLabel#titleLabel {
        font-size: 20pt;
        font-weight: bold;
    }
    """

    app.setStyleSheet(DARK_STYLE)
    window = MainWindow()
    sys.exit(app.exec_())