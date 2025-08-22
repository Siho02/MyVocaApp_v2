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

    def get_deck_names(self):
        """모든 덱의 이름 목록을 반환합니다."""
        return list(self.app_data.get("decks", {}).keys())

    def add_deck(self, deck_name):
        """새로운 덱을 추가합니다."""
        if deck_name not in self.app_data["decks"]:
            self.app_data["decks"][deck_name] = {"settings": {}, "words": [], "study_log": {}}
            self.save_data()
            return True
        return False

    def delete_deck(self, deck_name):
        """기존 덱을 삭제합니다."""
        if deck_name in self.app_data["decks"]:
            del self.app_data["decks"][deck_name]
            self.save_data()

    def update_deck_settings(self, deck_name, native_lang, study_lang):
        """덱의 언어 설정을 업데이트합니다."""
        if deck_name in self.app_data["decks"]:
            settings = self.app_data["decks"][deck_name]["settings"]
            settings["native_lang"] = native_lang
            settings["study_lang"] = study_lang
            self.save_data()

    def get_deck_settings(self, deck_name):
        """특정 덱의 언어 설정을 반환합니다."""
        return self.app_data["decks"].get(deck_name, {}).get("settings", {})

    def get_words_for_deck(self, deck_name):
        """특정 덱의 모든 단어 목록을 반환합니다."""
        return self.app_data["decks"].get(deck_name, {}).get("words", [])

    def get_study_log_for_deck(self, deck_name):
        """특정 덱의 학습 기록을 반환합니다."""
        return self.app_data["decks"].get(deck_name, {}).get("study_log", {})
    
    def get_all_decks_data(self):
        """모든 덱의 데이터를 반환합니다."""
        return self.app_data.get("decks", {})
