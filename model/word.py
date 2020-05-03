class Word:
    def __init__(self, sentence_class, sentence, token, original_word):
        self.token = token
        self.original_word = original_word
        assert type(sentence) == sentence_class
        self.sentence = sentence
