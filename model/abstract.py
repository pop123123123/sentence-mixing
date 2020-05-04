class Sequencable:
    def next_in_seq(self):
        raise NotImplementedError()


class Sentence(Sequencable):
    """
    Represents an abstract sequence of words

    Class attributes:
    original_text - string of sentence
    words - list of associated words
    index_words - dictionary associating for each word its index in words list
    """

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


class Word(Sequencable):
    """
    Represents an abstract word

    Class attributes:
    sentence - sentence where the word comes from
    token - word as found in the dictionary
    original_word - word as found in the original sentence
    phonems - list of associated phonems
    index_phonems - dictionary associating for each phonem its index in phonems list
    """

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

    def next_in_seq(self):
        if self == self.sentence.words[-1]:
            sentence = self.sentence.next_in_seq()
            while sentence is not None and len(sentence.words) == 0:
                sentence = sentence.next_in_seq()
            if sentence is None:
                return None
            else:
                return sentence.words[0]
        return self.sentence.words[self.get_index_in_sentence() + 1]


class Phonem(Sequencable):
    """
    Represents an abstract phonem

    Class attributes:
    word - word where the phonem comes from
    transcription - phonem transcription as found  in the dictionary
    """

    def __init__(self, word_class, word, transcription):
        self.transcription = transcription
        assert type(word) == word_class
        self.word = word

    def get_index_in_word(self):
        return self.word.get_index_phonem(self)

    def next_in_seq(self):
        if self == self.word.phonems[-1]:
            word = self.word.next_in_seq()
            while word is not None and len(word.phonems) == 0:
                word = word.next_in_seq()
            if word is None:
                return None
            else:
                return word.phonems[0]
        return self.word.phonems[self.get_index_in_word() + 1]
