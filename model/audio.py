from model.abstract import Phonem, Sentence, Word


class VideoSegment:
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

    def _get_original_wave(self):
        raise NotImplementedError()

    def get_wave(self):
        rate, data = self._get_original_wave()
        return rate, data[int(self.start * rate) : int(self.end * rate)]

    def _get_original_video(self):
        raise NotImplementedError()

    def get_video_clip(self):
        clip = self._get_original_video()
        return clip.subclip(self.start, self.end)

    def __repr__(self):
        return f"{self.start}, {self.end}, {type(self)}"


class SubtitleLine(Sentence, VideoSegment):
    """Represents a line of subtitle in a video"""

    def __init__(self, original_text, start, end, video):
        Sentence.__init__(self, original_text)
        VideoSegment.__init__(self, start, end)
        self.video = video
        self.words = []

    def _get_original_wave(self):
        return self.video.get_audio_wave()

    def _get_original_video(self):
        return self.video.get_video()

    def get_index_in_video(self):
        return self.video.get_index_subtitle(self)

    def next_in_seq(self):
        if self == self.video.subtitles[-1]:
            return None
        return self.video.subtitles[self.get_index_in_video() + 1]

    def previous_in_seq(self):
        if self == self.video.subtitles[0]:
            return None
        return self.video.subtitles[self.get_index_in_video() - 1]


class AudioWord(Word, VideoSegment):
    """Represents a word spotted by Montreal aligner in a sentence"""

    def __init__(self, subtitle, token, original_word, start, end):
        Word.__init__(self, SubtitleLine, subtitle, token, original_word)
        VideoSegment.__init__(self, start, end)

    def _get_original_wave(self):
        return self.sentence._get_original_wave()

    def _get_original_video(self):
        return self.sentence._get_original_video()


class AudioPhonem(Phonem, VideoSegment):
    """Represents a phonem spotted by Montreal aligner in a sentence"""

    def __init__(self, word, transcription, start, end):
        Phonem.__init__(self, AudioWord, word, transcription)
        VideoSegment.__init__(self, start, end)

    def _get_original_wave(self):
        return self.word._get_original_wave()

    def _get_original_video(self):
        return self.word._get_original_video()
