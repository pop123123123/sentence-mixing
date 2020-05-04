class Sentence:
    def __init__(self, original_text):
        self.original_text = original_text
        self.words = []
        self.index_words = {}

    def set_words(self, words):
        self.words = list(words)
        self.index_words = {p: i for i, p in enumerate(self.words)}

    def add_word(self, word):
        self.index_words[word] = len(self.words)
        self.words.append(word)

    def get_index_word(self, word):
        assert self.index_words is not None and word in self.index_words
        return self.index_words[word]


class Word:
    def __init__(self, sentence_class, sentence, token, original_word):
        self.token = token
        self.original_word = original_word
        assert type(sentence) == sentence_class
        self.sentence = sentence
        self.phonems = []
        self.index_phonems = {}

    def set_phonems(self, phonems):
        self.phonems = list(phonems)
        self.index_phonems = {p: i for i, p in enumerate(self.phonems)}

    def add_phonem(self, phonem):
        self.index_phonems[phonem] = len(self.phonems)
        self.phonems.append(phonem)

    def get_index_phonem(self, phonem):
        assert self.index_phonems is not None and phonem in self.index_phonems
        return self.index_phonems[phonem]

    def get_index_in_sentence(self):
        return self.sentence.get_index_word(self)


class Phonem:
    def __init__(self, word_class, word, transcription):
        self.transcription = transcription
        assert type(word) == word_class
        self.word = word

    def get_index_in_word(self):
        return self.word.get_index_phonem(self)
