import json
import os
from datetime import datetime, timedelta
import math

def update_study_log(mode, correct, incorrect, start_time, end_time):
    log_path = "data/study_log.json"
    today = datetime.now().strftime("%Y-%m-%d")

    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            try:
                log_data = json.load(f)
            except json.JSONDecodeError:
                print("study_log.json 파일 손상. 새로 초기화 합니다.")
                log_data = {}
    else:
        log_data = {}

    if today not in log_data:
        log_data[today] = {
            "studied_word_count": 0,
            "registered_word_count": 0,
            "deleted_word_count": 0,
            "correct_count": 0,
            "incorrect_count": 0,
            "study_minutes": 0,
            "study_sessions": []
        }

    #log_data[today]["studied_word_count"] += 1
    log_data[today]["correct_count"] += correct
    log_data[today]["incorrect_count"] += incorrect

    # 학습 시간 추가
    try: 
        start_dt = datetime.strptime(start_time, "%H:%M")
        end_dt = datetime.strptime(end_time, "%H:%M")
        minutes = max(1, int((end_dt - start_dt).total_seconds() / 60))  # 최소 1분
    except Exception as e:
        print(f"시간 파싱 오류 : {e}")
        minutes += 1
        
    log_data[today]["study_minutes"] += minutes
    log_data[today]["study_sessions"].append({
        "start": start_time,
        "end": end_time
    })

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)

def calculate_after_min(correct, incorrect):
    total = correct + incorrect
    if total == 0:
        return 180  # 기본값 3시간

    accuracy = correct / total
    log_factor = math.log(total + 1, 2)
    acc_weight = 0.5 + accuracy  # 0.5 ~ 1.5 사이

    after_min = 180 * log_factor * acc_weight
    return int(min(max(after_min, 3), 43200))  # 3분 ~ 30일 제한
