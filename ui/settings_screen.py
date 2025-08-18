import shutil
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt

# 앱의 데이터 파일 경로 (main.py와 동일하게 설정)
DATA_FILE = "data/app_data.json"

class SettingsScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        title = QLabel("⚙️ 설정")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)

        # --- 백업 버튼 및 기능 ---
        backup_button = QPushButton("💾 데이터 백업하기")
        backup_button.clicked.connect(self.backup_data)
        layout.addWidget(backup_button)

        # --- 복원 버튼 및 기능 ---
        restore_button = QPushButton("📂 데이터 복원하기")
        restore_button.clicked.connect(self.restore_data)
        layout.addWidget(restore_button)
        
        layout.addStretch()

    def backup_data(self):
        # 1. 백업 파일 저장 위치 및 이름 정하기
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"voca_backup_{timestamp}.json"
        
        # QFileDialog를 사용해 사용자에게 저장 경로를 묻습니다.
        save_path, _ = QFileDialog.getSaveFileName(self, '백업 파일 저장', default_filename, 'JSON Files (*.json)')

        if save_path:
            try:
                # 2. 현재 데이터 파일을 지정된 경로에 복사 (shutil 라이브러리 사용)
                shutil.copy(DATA_FILE, save_path)
                QMessageBox.information(self, "백업 완료", f"데이터를 성공적으로 백업했습니다.\n경로: {save_path}")
            except Exception as e:
                QMessageBox.critical(self, "백업 실패", f"백업 중 오류가 발생했습니다: {e}")

    def restore_data(self):
        # 1. 사용자에게 강력한 경고 메시지 표시
        reply = QMessageBox.warning(self, '복원 확인', 
                                     "데이터를 복원하시겠습니까?\n\n"
                                     "경고: 현재 모든 데이터가 선택한 백업 파일의 내용으로 덮어쓰기 됩니다.\n"
                                     "이 작업은 되돌릴 수 없습니다.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.No:
            return

        # 2. 복원할 백업 파일 선택하기
        restore_path, _ = QFileDialog.getOpenFileName(self, '백업 파일 선택', '', 'JSON Files (*.json)')

        if restore_path:
            try:
                # 3. 선택된 백업 파일을 현재 데이터 파일 위치에 덮어쓰기
                shutil.copy(restore_path, DATA_FILE)
                QMessageBox.information(self, "복원 완료", 
                                          "데이터를 성공적으로 복원했습니다.\n\n"
                                          "앱을 재시작해야 변경사항이 적용됩니다.")
                # 변경사항을 완전히 적용하기 위해 앱 종료
                self.main_window.close()
            except Exception as e:
                QMessageBox.critical(self, "복원 실패", f"복원 중 오류가 발생했습니다: {e}")