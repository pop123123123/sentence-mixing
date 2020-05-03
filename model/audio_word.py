from word import Word

from model.audio_segment import AudioSegment
from model.subtitle_line import SubtitleLine


class AudioWord(Word, AudioSegment):
    def __init__(self, subtitle, token, original_word, start, end):
        Word.__init__(self, SubtitleLine, subtitle, token, original_word)
        AudioSegment.__init__(self, start, end)

    def _get_audio_wave(self):
        return self.subtitle._get_audio_wave()
