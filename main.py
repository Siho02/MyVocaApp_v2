import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QStackedLayout
from ui.home_screen import HomeScreen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Voca App")
        self.setGeometry(100, 100, 400, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QStackedLayout()
        self.central_widget.setLayout(self.layout)

        self.home_screen = HomeScreen()
        self.layout.addWidget(self.home_screen)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())