from model.abstract import Phonem, Sentence, Word


class AudioSegment:
    """This class represent an abstract audio segment

    Internal attributes:
    - start: start timestamp of the segment in the audio file
    - end: end timestamp of the segment in the audio file
    """

    def __init__(self, start, end):
        self._start = start
        self._end = end

    def _get_audio_wave(self):
        raise NotImplementedError()

    def get_wave(self):
        rate, data = self._get_audio_wave()
        return data[int(self._start * rate) : int(self._end * rate)]


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


class AudioWord(Word, AudioSegment):
    def __init__(self, subtitle, token, original_word, start, end):
        Word.__init__(self, SubtitleLine, subtitle, token, original_word)
        AudioSegment.__init__(self, start, end)

    def _get_audio_wave(self):
        return self.subtitle._get_audio_wave()


class AudioPhonem(Phonem, AudioSegment):
    def __init__(self, word, transcription, start, end):
        Phonem.__init__(self, word, transcription)
        AudioSegment.__init__(self, start, end)

    def _get_audio_wave(self):
        return self.word._get_audio_wave()
