import json
import os
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QGroupBox
from PyQt5.QtCore import pyqtSignal, Qt, QEvent

# -----------------------------------------------------
# 1. 날짜 별 활동 그래프
# ----------------------------------------------------- 
class ContributionGraph(QWidget):
    day_clicked = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(4)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.grid_layout)
        self.cells = {}

    def get_color(self, count):
        if count == 0: return "#EAECEE"
        elif 1 <= count < 10: return "#A3E4D7"
        elif 10 <= count < 30: return "#76D7C4"
        elif 30 <= count < 50: return "#48C9B0"
        else: return "#1ABC9C"

    def set_data(self, log_data):
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)
        self.cells.clear()

        today = datetime.now()
        num_weeks = 18

        last_month = ""
        for i in range(num_weeks):
            date_of_week = today - timedelta(weeks=(num_weeks - 1 - i))
            current_month = date_of_week.strftime("%b")
            if current_month != last_month:
                month_label = QLabel(current_month)
                month_label.setAlignment(Qt.AlignCenter)
                self.grid_layout.addWidget(month_label, 0, i + 1, 1, 4, Qt.AlignLeft)
                last_month = current_month
        
        start_date = today - timedelta(days=today.weekday()) - timedelta(weeks=(num_weeks - 1))
        for day_offset in range(num_weeks * 7):
            date = start_date + timedelta(days=day_offset)
            if date > today: continue

            row, col = date.weekday() + 1, day_offset // 7
            date_str = date.strftime("%Y-%m-%d")
            
            count = log_data.get(date_str, {}).get("studied_word_count", 0)
            
            cell = QLabel()
            cell.setFixedSize(16, 16)
            cell.setStyleSheet(f"background-color: {self.get_color(count)}; border-radius: 3px;")
            cell.setToolTip(f"{date_str}\n학습 단어: {count}개")
            cell.installEventFilter(self)
            
            self.grid_layout.addWidget(cell, row, col + 1)
            self.cells[cell] = date_str

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress and source in self.cells:
            self.day_clicked.emit(self.cells[source])
            return True
        return super().eventFilter(source, event)

# -----------------------------------------------------
# 2. 통계 화면 전체 구성 
# ----------------------------------------------------- 
class StatsScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.log_data_by_date= {}

        self.layout = QVBoxLayout(self)

        self.title_label = QLabel("전체 통계")
        self.title_label.setObjectName("titleLabel")
        self.layout.addWidget(self.title_label)

        summary_layout = QHBoxLayout()
        self.total_words_label = QLabel("총 학습 단어: 0개")
        self.total_accuracy_label = QLabel("전체 정답률: 0.00%")
        summary_layout.addWidget(self.total_words_label)
        summary_layout.addWidget(self.total_accuracy_label)
        self.layout.addLayout(summary_layout)

        self.contribution_graph = ContributionGraph()
        self.layout.addWidget(self.contribution_graph)
        
        self.daily_detail_group = QGroupBox("일일 상세 정보")
        detail_layout = QVBoxLayout()
        self.detail_date_label = QLabel("날짜: -")
        self.detail_words_label = QLabel("학습 단어: -")
        self.detail_accuracy_label = QLabel("정답률: -")
        detail_layout.addWidget(self.detail_date_label)
        detail_layout.addWidget(self.detail_words_label)
        detail_layout.addWidget(self.detail_accuracy_label)
        
        self.daily_detail_group.setLayout(detail_layout)
        self.daily_detail_group.hide()
        self.layout.addStretch()
        self.layout.addWidget(self.daily_detail_group)
        self.contribution_graph.day_clicked.connect(self.on_day_clicked)

    def load_stats_data(self, deck_name=None):
        if deck_name: # 특정 덱의 통계를 볼 경우
            self.title_label.setText(f"'{deck_name}' 덱 통계")
            decks_to_process = {deck_name: self.main_window.data_manager.app_data["decks"][deck_name]}
        else: # 전체 통계를 볼 경우
            self.title_label.setText("전체 통계")
            decks_to_process = self.main_window.data_manager.app_data.get("decks", {})
        
        total_words, total_correct, total_incorrect = 0, 0, 0
        self.log_data_by_date = {}

        # 모든 덱을 순회하며 로그를 합산
        for deck_data in decks_to_process.values():
            log_data = deck_data.get("study_log", {})
            for date, daily_log in log_data.items():
                if date not in self.log_data_by_date:
                    self.log_data_by_date[date] = {"studied_word_count": 0, "correct_count": 0, "incorrect_count": 0}
                self.log_data_by_date[date]["studied_word_count"] += daily_log.get("studied_word_count", 0)
                self.log_data_by_date[date]["correct_count"] += daily_log.get("correct_count", 0)
                self.log_data_by_date[date]["incorrect_count"] += daily_log.get("incorrect_count", 0)
                
        # 합산된 데이터를 기반으로 전체 통계 계산
        for daily_summary in self.log_data_by_date.values():
            total_words += daily_summary["studied_word_count"]
            total_correct += daily_summary["correct_count"]
            total_incorrect += daily_summary["incorrect_count"]
        
        # 상단 전체 통계 라벨 업데이트
        self.total_words_label.setText(f"총 학습 단어: {total_words}개")
        if (total_correct + total_incorrect) > 0:
            accuracy = (total_correct / (total_correct + total_incorrect)) * 100
            self.total_accuracy_label.setText(f"전체 정답률: {accuracy:.1f}%")
        else:
            self.total_accuracy_label.setText("전체 정답률: 0.0%")
        
        # 그래프 데이터 설정
        self.contribution_graph.set_data(self.log_data_by_date)
        # 상세 정보창 숨기기
        self.daily_detail_group.hide()

    def on_day_clicked(self, date_str):
        # This method remains the same
        daily_data = self.log_data_by_date.get(date_str)
        if not daily_data:
            self.daily_detail_group.hide()
            return
        
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = date_obj.strftime(f"%dth %B, %Y")
        self.detail_date_label.setText(f"{formatted_date}")

        words = daily_data.get("studied_word_count", 0)
        correct = daily_data.get("correct_count", 0)
        incorrect = daily_data.get("incorrect_count", 0)

        self.detail_words_label.setText(f"∙ 학습 단어: {words}개")

        if (correct + incorrect) > 0:
            accuracy = (correct / (correct + incorrect)) * 100
            self.detail_accuracy_label.setText(f"∙ 정답률: {accuracy:.2f}%")
        else:
            self.detail_accuracy_label.setText(f"∙ 정답률: 정보 없음")
        
        self.daily_detail_group.show()