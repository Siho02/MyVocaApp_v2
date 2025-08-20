import json
import os

DATA_FILE = "data/app_data.json"

class DataManager:
    """
    앱의 모든 데이터(app_data.json)를 읽고, 쓰고, 관리하는
    유일한 클래스. 앱의 '데이터베이스' 역할을 합니다.
    """
    def __init__(self):
        self.app_data = {}
        self.load_data()

    def load_data(self):
        """앱 시작 시 app_data.json 파일을 읽어와 데이터를 로드합니다."""
        if not os.path.exists(DATA_FILE):
            os.makedirs("data", exist_ok=True)
            # 파일이 없으면 기본 구조로 새로 만듭니다.
            default_data = {"decks": {}, "study_log": {}}
            self.app_data = default_data
            self.save_data()
        else:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                try:
                    self.app_data = json.load(f)
                except json.JSONDecodeError:
                    self.app_data = {"decks": {}, "study_log": {}}
                    self.save_data()

    def save_data(self):
        """현재 데이터를 app_data.json 파일에 저장합니다."""
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.app_data, f, ensure_ascii=False, indent=2)
