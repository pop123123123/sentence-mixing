from model.phonem import Phonem
from model.target_word import TargetWord

class TargetPhonem(Phonem):
    def __init__(self, word, transcription):
        Phonem.__init__(self, TargetWord, word, transcription)
