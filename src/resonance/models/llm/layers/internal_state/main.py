
class InternalState:

    def __init__(self, emotions: dict, relationships: dict, activity: dict):
        self.emotions = emotions
        self.emotions_locked = [] 
        self.relationships = relationships
        self.activity = activity

        #self.emotions_locked = {"happiness": True}     State that the happiness emotion cannot be changed, will stay locked.

        #self.emotions = {
        #    "mood": "neutral",
        #    "valence": 0, # +1 positive, -1 negative
        #}
        #self.relationships = {
        #    "user": {
        #        "affection": 0,
        #        "trust": 0,
        #        "attachment": 0,
        #        "comfort": 0
        #    }
        #}
        #
        #self.activity = {
        #    "focus": "user",
        #    "energy": 0,
        #    "social_drive": 0
        #}

    def lock_emotion(self, emotion: str):
        if emotion in self.emotions and emotion not in self.emotions_locked:
            self.emotions_locked.append(emotion)

        return

    def set_emotion(self, emotion: str, value):
        if emotion in self.emotions:
            if emotion in self.emotions_locked:
                print(f"\x1b[33mEmotion \"{emotion}\" locked, cannot modify!\x1b[0m")
            self.emotions[emotion] = value

        return

    def update_from_interaction(self, emotions={}):
        if emotions:
            for emotion, value in emotions.items():
                self.set_emotion(emotion, value)

        return self.emotions


    def decay_over_time(self):
        pass


    def compute_initiative(self):
        pass
