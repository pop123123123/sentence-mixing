class Sentence:
    def __init__(self, original_text):
        self.original_text = original_text


class Word:
    def __init__(self, sentence_class, sentence, token, original_word):
        self.token = token
        self.original_word = original_word
        assert type(sentence) == sentence_class
        self.sentence = sentence


class Phonem:
    def __init__(self, word_class, word, transcription):
        self.transcription = transcription
        assert type(word) == word_class
        self.word = word
