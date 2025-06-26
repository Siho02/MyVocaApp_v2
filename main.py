import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget

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

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

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

        self.show()

    def show_home_screen(self):
        self.stack.setCurrentWidget(self.home_screen)
    
    def switch_screen(self, screen):
        self.stack.setCurrentWidget(screen)
    
    def start_study(self):
        # 이전 study_screen이 이미 있었다면 제거 (중복 방지)
        if hasattr(self, 'study_screen') and self.study_screen is not None:
            self.stack.removeWidget(self.study_screen)

        # 새로운 StudyScreen 생성 (mode 전달)
        self.study_screen = StudyScreen(mode, self.show_home_screen)
        self.stack.addWidget(self.study_screen)
        self.stack.setCurrentWidget(self.study_screen)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())