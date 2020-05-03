from audio_segment import AudioSegment


class Phonem(AudioSegment):
    """This class is derivated from AudioSegment and simply changes the abstract name of the
    argument text to the concrete name phonem"""

    def __init__(
        self, start_timestamp, end_timestamp, phonem, related_audio_path
    ):
        AudioSegment.__init__(
            self, start_timestamp, end_timestamp, phonem, related_audio_path
        )

    def get_phonem(self):
        return self._text

    def __eq__(self, other):
        if isinstance(other, str):
            return self.get_phonem() == other
        return self == other
