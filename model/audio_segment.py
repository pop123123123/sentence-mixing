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
