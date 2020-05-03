class AudioSegment():

    def __init__(self, start, end, audible):
        self.start = start_timestamp
        self.end = end_timestamp
        self.audible = audible

    def __str__(self):
        return "(" + str(self._start) + ", " + str(self._end) + ", " + str(self._text) + ", " + str(self._audio_path) + ")"
