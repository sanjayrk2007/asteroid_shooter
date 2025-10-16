import json
import os
from datetime import datetime

class Leaderboard:
    def __init__(self, filename):
        self.filename = filename
        self.scores = []
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    self.scores = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.scores = []
        else:
            self.scores = []

    def save(self):
        try:
            with open(self.filename, "w") as f:
                json.dump(self.scores, f, indent=4)
        except IOError as e:
            print(f"Error saving leaderboard: {e}")

    def add_score(self, name, score):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.scores.append({
            "name": name,
            "score": score,
            "timestamp": timestamp
        })
        self.scores.sort(key=lambda s: s["score"], reverse=True)

    def get_top_scores(self, count=None):
        if count is None:
            return self.scores
        return self.scores[:count]

    def get_player_rank(self, name, score):
        temp_scores = self.scores.copy()
        temp_scores.append({"name": name, "score": score})
        temp_scores.sort(key=lambda s: s["score"], reverse=True)
        
        for i, entry in enumerate(temp_scores):
            if entry["name"] == name and entry["score"] == score:
                return i + 1
        return len(temp_scores)

    def get_high_score(self):
        if self.scores:
            return self.scores[0]["score"]
        return 0

    def clear_leaderboard(self):
        self.scores = []
        self.save()
