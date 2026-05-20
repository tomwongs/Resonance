
class InternalState:

    def __init__(self):
        self.state = {
            "mood": "neutral",
            "valence": 0, # +1 positive, -1 negative
            "arousal": 0
        }
        self.relationships = {
            "user": {
                "affection": 0,
                "trust": 0,
                "attachment": 0,
                "comfort": 0
            }
        }

        self.activity = {
            "focus": "user",
            "energy": 0,
            "social_drive": 0
        }

    def update_from_interaction(self):
        pass

    def decay_over_time(self):
        pass

    def compute_initiative(self):
        pass
