from model.sentence import Sentence


class TargetSentence(Sentence):
    def __init__(self, text):
        Sentence.__init__(self, text)
        # TODO: create word
