import json
import os
from datetime import datetime, timedelta

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# 한글 폰트가 깨지지 않도록 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


class StatsScreen(QWidget):
    def __init__(self, switch_to_home_callback):
        super().__init__()
        self.switch_to_home_callback = switch_to_home_callback

        # --- 기본 레이아웃 및 위젯 설정 ---
        self.layout = QVBoxLayout(self)

        self.title_label = QLabel("📊 학습 통계")
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        # 텍스트 통계를 표시할 라벨
        self.total_study_time_label = QLabel("총 학습 시간: 정보 없음")
        self.total_accuracy_label = QLabel("전체 정답률: 정보 없음")
        self.layout.addWidget(self.total_study_time_label)
        self.layout.addWidget(self.total_accuracy_label)
        
        # Matplotlib 그래프를 담을 Canvas 위젯
        self.canvas = FigureCanvas(Figure(figsize=(4, 3)))
        self.layout.addWidget(self.canvas)

        # 홈으로 돌아가는 버튼
        self.home_button = QPushButton("← 홈으로")
        self.home_button.clicked.connect(self.switch_to_home_callback)
        self.layout.addWidget(self.home_button)

        self.load_stats_data()

    def load_stats_data(self):
        log_path = "data/study_log.json"
        if not os.path.exists(log_path):
            self.total_study_time_label.setText("학습 기록이 없습니다.")
            return

        with open(log_path, 'r', encoding='utf-8') as f:
            try:
                log_data = json.load(f)
            except json.JSONDecodeError:
                self.total_study_time_label.setText("학습 기록 파일이 손상되었습니다.")
                return

        # --- 전체 통계 계산 ---
        total_minutes = 0
        total_correct = 0
        total_incorrect = 0

        for daily_log in log_data.values():
            total_minutes += daily_log.get("study_minutes", 0)
            total_correct += daily_log.get("correct_count", 0)
            total_incorrect += daily_log.get("incorrect_count", 0)

        # 시간과 분으로 변환
        hours, minutes = divmod(total_minutes, 60)
        self.total_study_time_label.setText(f"총 학습 시간: {hours}시간 {minutes}분")

        # 정답률 계산
        if (total_correct + total_incorrect) > 0:
            accuracy = (total_correct / (total_correct + total_incorrect)) * 100
            self.total_accuracy_label.setText(f"전체 정답률: {accuracy:.2f}%")
        else:
            self.total_accuracy_label.setText("전체 정답률: 0.00%")

        # --- 그래프 데이터 준비 (최근 7일) ---
        today = datetime.now()
        last_7_days = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
        
        study_minutes_per_day = []
        for day in last_7_days:
            minutes = log_data.get(day, {}).get("study_minutes", 0)
            study_minutes_per_day.append(minutes)

        # 날짜 포맷을 'mm-dd' 형태로 변경
        short_dates = [f"{d[5:7]}-{d[8:10]}" for d in last_7_days]
        self.plot_bar_chart(short_dates, study_minutes_per_day)

    def plot_bar_chart(self, dates, minutes):
        ax = self.canvas.figure.subplots()
        ax.bar(dates, minutes, color='skyblue')
        ax.set_title('최근 7일 학습 시간 (분)')
        ax.set_xlabel('날짜')
        ax.set_ylabel('학습 시간 (분)')
        ax.figure.tight_layout() # 레이아웃 최적화
        self.canvas.draw()