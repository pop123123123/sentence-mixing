from model.audio_segment import AudioSegment
from model.phonem import Phonem


class AudioPhonem(Phonem, AudioSegment):
    def __init__(self, word, transcription, start, end):
        Phonem.__init__(self, word, transcription)
        AudioSegment.__init__(self, start, end)

    def _get_audio_wave(self):
        return self.word._get_audio_wave()
