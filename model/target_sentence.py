from model.sentence import Sentence
from model.target_word import TargetWord
from target_parser import split_text, transform_numbers


class TargetSentence(Sentence):
    def __init__(self, original_text):
        Sentence.__init__(self, original_text)

        self.original_text = transform_numbers(self.original_text)

        original_words = split_text(self.original_text)

        self.words = [TargetWord(self, ow) for ow in original_words]
