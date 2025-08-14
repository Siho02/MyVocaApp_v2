import sys, json, os
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt

# --- 화면 UI 클래스들을 임포트합니다. ---
from ui.deck_selection_screen import DeckSelectionScreen
from ui.language_setup_screen import LanguageSetupScreen
from ui.home_screen import HomeScreen
from ui.stats_screen import StatsScreen
from ui.register_manual import RegisterManualScreen 
from ui.register_csv import RegisterCSVScreen       
from ui.word_list_screen import WordListScreen       


DATA_FILE = "data/app_data.json"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Voca App")
        self.setGeometry(100, 100, 400, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack, 1) # 수정 후

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
        self.stats_screen = StatsScreen()
        self.register_manual_screen = RegisterManualScreen(self) 
        self.register_csv_screen = RegisterCSVScreen(self)      
        self.word_list_screen = WordListScreen(self) 
        self.home_screen = HomeScreen(
            switch_to_register_callback=self.open_manual_register,
            switch_to_csv_callback=self.open_csv_register,
            switch_to_wordlist_callback=self.open_word_list,
            switch_to_study_mode_callback=lambda: print("TODO"))
        
        # --- 화면 스택에 추가 ---
        self.stack.addWidget(self.deck_selection_screen)
        self.stack.addWidget(self.language_setup_screen)
        self.stack.addWidget(self.home_screen)
        self.stack.addWidget(self.stats_screen)
        self.stack.addWidget(self.register_manual_screen)
        self.stack.addWidget(self.register_csv_screen)
        self.stack.addWidget(self.word_list_screen)

        # --- 시그널 연결 ---
        self.deck_selection_screen.deck_selected.connect(self.handle_deck_selection)
        self.deck_selection_screen.deck_deleted.connect(self.handle_deck_deletion) # 삭제 신호 연결
        self.language_setup_screen.setup_complete.connect(self.handle_setup_complete)
        
        # 네비게이션 버튼 연결
        btn_home.clicked.connect(self.go_to_first_screen)
        btn_stats.clicked.connect(self.go_to_stats_screen)
        # btn_settings.clicked.connect(self.go_to_settings_screen) # 나중에 추가

        # --- 앱 시작 ---
        #self.deck_selection_screen.update_deck_list(self.app_data["decks"].keys())
        #self.stack.setCurrentWidget(self.deck_selection_screen)
        
        self.go_to_first_screen()
        self.show()

    def open_manual_register(self):
        self.stack.setCurrentWidget(self.register_manual_screen)

    def open_csv_register(self):
        self.stack.setCurrentWidget(self.register_csv_screen)

    def open_word_list(self): # [추가]
        # 단어 목록 화면으로 가기 전, 최신 데이터를 로드하도록 함
        self.word_list_screen.load_words() 
        self.stack.setCurrentWidget(self.word_list_screen)

    def go_to_home_screen(self):
        # 홈스크린으로 돌아갈 때마다 제목을 현재 덱 이름으로 설정
        if self.current_deck:
            self.home_screen.set_deck_name(self.current_deck)
        self.stack.setCurrentWidget(self.home_screen)

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            os.makedirs("data", exist_ok=True)
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump({"decks": {}, "study_log": {}}, f)
            return {"decks": {}, "study_log": {}}
        
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError: # 파일이 비어있는 경우 처리
                return {"decks": {}, "study_log": {}}

    def save_data(self):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.app_data, f, ensure_ascii=False, indent=2)
    
    # --- 화면 전환 함수 ---
    def go_to_first_screen(self):
        self.deck_selection_screen.update_deck_list(self.app_data["decks"].keys())
        self.stack.setCurrentWidget(self.deck_selection_screen)
        
    def go_to_stats_screen(self):
        self.stats_screen.load_stats_data() # 통계 화면으로 가기 전 데이터 리로드
        self.stack.setCurrentWidget(self.stats_screen)

    def handle_deck_selection(self, deck_name, is_new):
        if is_new: # 새 덱 생성
            if deck_name not in self.app_data["decks"]:
                self.app_data["decks"][deck_name] = {"settings": {}, "words": []}
                self.save_data()
                self.language_setup_screen.set_deck_name(deck_name)
                self.stack.setCurrentWidget(self.language_setup_screen)
            else:
                # 이미 있는 덱 이름 처리 (나중에 추가 가능)
                print(f"Deck '{deck_name}' already exists.")
        else: # 기존 덱 선택
            self.current_deck = deck_name
            self.home_screen.set_deck_name(deck_name)
            self.stack.setCurrentWidget(self.home_screen)
            # TODO: home_screen에 선택된 덱 정보를 전달해야 함
            # self.home_screen.set_deck(deck_name) 

    def handle_setup_complete(self, deck_name, study_lang, native_lang):
        settings = self.app_data["decks"][deck_name]["settings"]
        settings["study_lang"] = study_lang
        settings["native_lang"] = native_lang
        self.save_data()
        
        self.current_deck = deck_name
        self.home_screen.set_deck_name(deck_name)
        self.stack.setCurrentWidget(self.home_screen)
        # TODO: home_screen에 선택된 덱 정보를 전달해야 함
        # self.home_screen.set_deck(deck_name)

    def handle_deck_deletion(self, deck_name):
        if deck_name in self.app_data["decks"]:
            del self.app_data["decks"][deck_name]
            self.save_data()
            # UI를 즉시 새로고침
            self.deck_selection_screen.update_deck_list(self.app_data["decks"].keys())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())