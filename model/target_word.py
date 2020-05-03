from target_phonem import TargetPhonem

from model.target_sentence import TargetSentence
from model.word import Word
from target_parser import from_token_to_phonem, from_word_to_token


class TargetWord(Word):
    def __init__(self, sentence, original_word):
        token = from_word_to_token(original_word)

        Word.__init__(self, TargetSentence, sentence, token, original_word)

        transcriptions = from_token_to_phonem(token)
        self.phonems = [
            TargetPhonem(self, transcription)
            for transcription in transcriptions
        ]
