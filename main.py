import sys
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QStackedWidget, QVBoxLayout, QHBoxLayout, QPushButton

from ui.home_screen import HomeScreen
from ui.register_manual import RegisterManualScreen
from ui.register_csv import RegisterCSVScreen
from ui.word_list_screen import WordListScreen
from ui.study_mode_select import StudyModeSelectScreen
from ui.study_screen import StudyScreen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My Voca App")
        self.setGeometry(100, 100, 400, 600)

        #total layout
        
        main_layout = QVBoxLayout()
        #self.setLayout(main_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        
        # 화면 생성
        self.register_screen = RegisterManualScreen(self.show_home_screen)
        self.csv_screen = RegisterCSVScreen(self.show_home_screen)
        self.word_list_screen = WordListScreen(self.show_home_screen)
        self.study_mode_select_screen = StudyModeSelectScreen(
            switch_to_home=self.show_home_screen,
            switch_to_study=self.start_study
        )

        self.home_screen = HomeScreen(
            switch_to_register_callback=lambda: self.switch_screen(self.register_screen),
            switch_to_csv_callback=lambda: self.switch_screen(self.csv_screen),
            switch_to_wordlist_callback=lambda: self.switch_screen(self.word_list_screen),
            switch_to_study_mode_callback=lambda: self.switch_screen(self.study_mode_select_screen)
        )
        
        # 화면 스택에 추가
        self.stack.addWidget(self.home_screen)
        self.stack.addWidget(self.register_screen)
        self.stack.addWidget(self.csv_screen)
        self.stack.addWidget(self.word_list_screen)
        self.stack.addWidget(self.study_mode_select_screen)

        nav_bar = QHBoxLayout()
        btn_home = QPushButton("🏠 홈")
        btn_stats = QPushButton("📊 통계")
        btn_settings = QPushButton("⚙️ 설정")

        btn_home.clicked.connect(lambda : self.switch_screen(self.home_screen))
        #btn_stats.clicked.connect(lambda: )
        #btn_settings.clicked.connect(lambda: )

        nav_bar.addWidget(btn_home)
        nav_bar.addWidget(btn_stats)
        nav_bar.addWidget(btn_settings)

        main_layout.addLayout(nav_bar)

        self.show()

    def show_home_screen(self):
        self.stack.setCurrentWidget(self.home_screen)
    
    def switch_screen(self, screen):
        self.stack.setCurrentWidget(screen)
    
    def start_study(self,mode):
        # 이전 study_screen이 이미 있었다면 제거 (중복 방지)
        if hasattr(self, 'study_screen') and self.study_screen is not None:
            self.stack.removeWidget(self.study_screen)

        # 새로운 StudyScreen 생성 (mode 전달)
        self.study_screen = StudyScreen(mode=mode, switch_to_home_callback=self.show_home_screen)
        self.stack.addWidget(self.study_screen)
        self.stack.setCurrentWidget(self.study_screen)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())