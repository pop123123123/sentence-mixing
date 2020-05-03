from model.audio_segment import AudioSegment
from model.audio_word import AudioWord
from model.sentence import Sentence


class SubtitleLine(Sentence, AudioSegment):
    def __init__(self, original_text, start, end, video):
        Sentence.__init__(self, original_text)
        AudioSegment.__init__(self, start, end)
        self.video = video
        self._words = []

    def add_word(self, word):
        assert type(word) == AudioWord
        self._subtitles.append(word)

    def extend_subtitles(self, iter_subtitles):
        # assumes all members of the iterator are SubtitleLine
        self._subtitles.extend(iter_subtitles)

    def _get_audio_wave(self):
        return self.video.get_audio_wave()
