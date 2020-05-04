import logic.text_parser as parser
from model.abstract import Phonem, Sentence, Word


class TargetSentence(Sentence):
    """Represents the sentence we want to form from the video"""

    def __init__(self, original_text):
        """Asigns the fields and then generates the list of associated TargetWords"""

        Sentence.__init__(self, original_text)

        original_words = parser.split_text(self.original_text)

        self.set_words(TargetWord(self, ow) for ow in original_words)


class TargetWord(Word):
    """Represents words inside the TargetSentence"""

    def __init__(self, sentence, original_word):
        """Asigns the fields and then generates the lisr of associated TargetPhonems"""

        token = parser.from_word_to_token(original_word)

        Word.__init__(self, TargetSentence, sentence, token, original_word)

        transcriptions = parser.from_token_to_phonem(token)
        self.set_phonems(
            TargetPhonem(self, transcription)
            for transcription in transcriptions
        )


class TargetPhonem(Phonem):
    """Represents phonems in a word"""

    def __init__(self, word, transcription):
        Phonem.__init__(self, TargetWord, word, transcription)
