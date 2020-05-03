class AudioSegment():
    """This class represent an abstract audio segment

    Internal attributes:
    - start: start timestamp of the segment in the audio file
    - end: end timestamp of the segment in the audio file
    """

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def _get_wave_path(self):
        raise NotImplementedError()

    def get_wave(self):
        audio_path = _get_wave_path()
        #TODO: play data

