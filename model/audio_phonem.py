from model.phonem import Phonem
from model.audio_segment import AudioSegment

class AudioPhonem(Phonem, AudioSegment):
    def __init__(self, word, trancription, start, end):
        Phonem.__init__(self, word, transcription)
        AudioSegment.__init__(self, start, end)

    def _get_wave_path(self):
        return self.word._get_wave_path()
