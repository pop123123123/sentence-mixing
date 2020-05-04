import logic.target_parser as parser
from model.abstract import Phonem, Sentence, Word


class TargetSentence(Sentence):
    def __init__(self, original_text):
        Sentence.__init__(self, original_text)

        original_words = parser.split_text(self.original_text)

        self.set_words(TargetWord(self, ow) for ow in original_words)


class TargetWord(Word):
    def __init__(self, sentence, original_word):
        token = parser.from_word_to_token(original_word)

        Word.__init__(self, TargetSentence, sentence, token, original_word)

        transcriptions = parser.from_token_to_phonem(token)
        self.set_phonems(
            TargetPhonem(self, transcription)
            for transcription in transcriptions
        )


class TargetPhonem(Phonem):
    def __init__(self, word, transcription):
        Phonem.__init__(self, TargetWord, word, transcription)
