class PhonemError(Exception):
    def __init__(self, target_phonem):
        self.target_phonem = target_phonem

    def __str__(self):
        return f'Phonem "{self.target_phonem.transcription}" from "{self.target_phonem.word.original_word}" not found.'
