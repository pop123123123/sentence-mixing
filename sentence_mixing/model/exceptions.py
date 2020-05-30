class PhonemError(Exception):
    def __init__(self, target_phonem):
        self.target_phonem = target_phonem

    def __str__(self):
        return f'Phonem "{self.target_phonem.transcription}" from "{self.target_phonem.word.original_word}" not found.'


class TokenAmbiguityError(Exception):
    def __init__(self, token):
        self.token = token

    def __str__(self):
        return f'Word "{self.token}" has multiple readings. Please choose a different word.'


class Interruption(Exception):
    def __init__(self, callback):
        self.callback = callback

    def __str__(self):
        return f' Callback "{self.callback.__name_}" returned True'
