import json
import os
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QGroupBox
from PyQt5.QtCore import pyqtSignal, Qt, QEvent

class ContributionGraph(QWidget):
    # This class remains the same as before
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
        elif 1 <= count < 5: return "#A3E4D7"
        elif 5 <= count < 10: return "#76D7C4"
        elif 10 <= count < 20: return "#48C9B0"
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

class StatsScreen(QWidget):
    # <<< 수정된 부분: 생성자에서 'switch_to_home_callback' 인자 제거 >>>
    def __init__(self):
        super().__init__()
        self.log_data = {}

        self.layout = QVBoxLayout(self)

        self.stats_summary_group = QGroupBox("전체 통계")
        summary_layout = QVBoxLayout()
        self.total_words_label = QLabel("총 학습 단어: 0개")
        self.total_time_label = QLabel("총 학습 시간: 0시간 0분")
        self.total_accuracy_label = QLabel("전체 정답률: 0.00%")
        summary_layout.addWidget(self.total_words_label)
        summary_layout.addWidget(self.total_time_label)
        summary_layout.addWidget(self.total_accuracy_label)
        self.stats_summary_group.setLayout(summary_layout)

        self.contribution_graph = ContributionGraph()
        
        self.daily_detail_group = QGroupBox("일일 상세 정보")
        detail_layout = QVBoxLayout()
        self.detail_date_label = QLabel("날짜: -")
        self.detail_words_label = QLabel("학습 단어: -")
        self.detail_time_label = QLabel("학습 시간: -")
        self.detail_accuracy_label = QLabel("정답률: -")
        detail_layout.addWidget(self.detail_date_label)
        detail_layout.addWidget(self.detail_words_label)
        detail_layout.addWidget(self.detail_time_label)
        detail_layout.addWidget(self.detail_accuracy_label)
        self.daily_detail_group.setLayout(detail_layout)
        self.daily_detail_group.hide()

        self.layout.addWidget(self.stats_summary_group)
        self.layout.addWidget(self.contribution_graph)
        self.layout.addStretch()
        self.layout.addWidget(self.daily_detail_group)
        
        # <<< 수정된 부분: 'home_button' 관련 코드 모두 삭제됨 >>>
        self.contribution_graph.day_clicked.connect(self.on_day_clicked)
        self.load_stats_data()

    def load_stats_data(self):
        log_path = "data/app_data.json"
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8') as f:
                try: 
                    full_data = json.load(f)
                    self.log_data = full_data.get("study_log", {})
                except json.JSONDecodeError: 
                    self.log_data = {}
        
        total_words = 0
        total_minutes = 0
        total_correct = 0
        total_incorrect = 0
        
        for daily_log in self.log_data.values():
            total_words += daily_log.get("studied_word_count", 0)
            total_minutes += daily_log.get("study_minutes", 0)
            total_correct += daily_log.get("correct_count", 0)
            total_incorrect += daily_log.get("incorrect_count", 0)

        hours, minutes = divmod(total_minutes, 60)
        self.total_words_label.setText(f"총 학습 단어: {total_words}개")
        self.total_time_label.setText(f"총 학습 시간: {hours}시간 {minutes}분")

        if (total_correct + total_incorrect) > 0:
            accuracy = (total_correct / (total_correct + total_incorrect)) * 100
            self.total_accuracy_label.setText(f"전체 정답률: {accuracy:.2f}%")
        else:
            self.total_accuracy_label.setText("전체 정답률: 0.00%")
        
        self.contribution_graph.set_data(self.log_data)

    def on_day_clicked(self, date_str):
        # This method remains the same
        daily_data = self.log_data.get(date_str)
        if not daily_data:
            self.daily_detail_group.hide()
            return
        
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = date_obj.strftime(f"%dth %B, %Y")
        self.detail_date_label.setText(f"{formatted_date}")

        words = daily_data.get("studied_word_count", 0)
        minutes = daily_data.get("study_minutes", 0)
        correct = daily_data.get("correct_count", 0)
        incorrect = daily_data.get("incorrect_count", 0)

        self.detail_words_label.setText(f"∙ 학습 단어: {words}개")
        self.detail_time_label.setText(f"∙ 학습 시간: {minutes}분")

        if (correct + incorrect) > 0:
            accuracy = (correct / (correct + incorrect)) * 100
            self.detail_accuracy_label.setText(f"∙ 정답률: {accuracy:.2f}%")
        else:
            self.detail_accuracy_label.setText(f"∙ 정답률: 정보 없음")
        
        self.daily_detail_group.show()