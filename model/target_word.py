from model.target_sentence import TargetSentence
from model.word import Word


class TargetWord(Word):
    def __init__(self, sentence, token, original_word):
        Word.__init__(self, TargetSentence, sentence, token, original_word)
        # TODO: create phonems
