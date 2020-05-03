class AudioSegment:
    def __init__(self, start, end, audible):
        self.start = start
        self.end = end
        self.audible = audible

    def __str__(self):
        return (
            "("
            + str(self._start)
            + ", "
            + str(self._end)
            + ", "
            + str(self._text)
            + ", "
            + str(self._audio_path)
            + ")"
        )
