from model.abstract import Phonem, Sentence, Word


class AudioSegment:
    """
    This class represents an abstract audio segment
    All the following audio classes are inherited from this object, soidentifies precise spots of
    the video

    Internal attributes:
    - start: start timestamp of the segment in the audio file
    - end: end timestamp of the segment in the audio file
    """

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def _get_audio_wave(self):
        raise NotImplementedError()

    def get_wave(self):
        rate, data = self._get_audio_wave()
        return rate, data[int(self.start * rate) : int(self.end * rate)]


class SubtitleLine(Sentence, AudioSegment):
    """Represents a line of subtitle in a video"""

    def __init__(self, original_text, start, end, video):
        Sentence.__init__(self, original_text)
        AudioSegment.__init__(self, start, end)
        self.video = video
        self.words = []

    def _get_audio_wave(self):
        return self.video.get_audio_wave()


class AudioWord(Word, AudioSegment):
    """Represents a word spotted by Montreal aligner in a sentence"""

    def __init__(self, subtitle, token, original_word, start, end):
        Word.__init__(self, SubtitleLine, subtitle, token, original_word)
        AudioSegment.__init__(self, start, end)

    def _get_audio_wave(self):
        return self.sentence._get_audio_wave()


class AudioPhonem(Phonem, AudioSegment):
    """Represents a phonem spotted by Montreal aligner in a sentence"""

    def __init__(self, word, transcription, start, end):
        Phonem.__init__(self, AudioWord, word, transcription)
        AudioSegment.__init__(self, start, end)

    def _get_audio_wave(self):
        return self.word._get_audio_wave()
