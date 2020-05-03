class Phonem:
    def __init__(self, word_class, word, transcription):
        self.transcription = transcription
        assert type(word) == word_class
        self.word = word
