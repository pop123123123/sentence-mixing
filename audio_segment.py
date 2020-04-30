class AudioSegment():
    """This class represent an abstract audio segment

    Internal attributes:
    - start: start timestamp of the segment in the audio file
    - end: end timestamp of the segment in the audio file
    - text: text told during the segment
    - audio_path: related audio file
    """

    def __init__(self, start_timestamp, end_timestamp, text, audio_path):
        self._start = start_timestamp
        self._end = end_timestamp
        self._text = text
        self._audio_path = audio_path

    def get_start_timestamp(self):
        return self._start

    def get_end_timestamp(self):
        return self._end

    def __str__(self):
        return "(" + str(self._start) + ", " + str(self._end) + ", " + str(self._text) + ", " + str(self._audio_path) + ")"
