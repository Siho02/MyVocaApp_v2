import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QPushButton, QWidget, QVBoxLayout

from ui.home_screen import HomeScreen
from ui.register_manual import RegisterManualScreen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Voca App")
        self.setGeometry(100, 100, 400, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 화면 구성
        self.home_screen = HomeScreen()
        self.register_screen = RegisterManualScreen()  # ← Step 2: 단어 등록 화면

        self.stack.addWidget(self.home_screen)
        self.stack.addWidget(self.register_screen)

        # Step 2: 버튼 클릭 시 화면 전환 연결
        self.home_screen.manual_button.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.register_screen)
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())