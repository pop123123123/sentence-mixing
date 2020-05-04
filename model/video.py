import base64
from functools import lru_cache

import webvtt
from scipy.io import wavfile

from model.audio import SubtitleLine


class Video:
    def __init__(self, base_path, subtitles_extension, extension):
        self._base_path = base_path
        self._subtitles_extension = subtitles_extension
        self._extension = extension
        self.subtitles = []

    def _get_audio_path(self):
        return self._base_path + ".wav"

    def get_video_path(self):
        return self._base_path + "." + self._extension

    def get_subtitle_path(self):
        return self._base_path + self._subtitles_extension

    @lru_cache(maxsize=None)
    def get_audio_wave(self):
        return wavfile.read(self._get_audio_path())

    def add_subtitle(self, subtitle):
        assert type(subtitle) == SubtitleLine
        self.subtitles.append(subtitle)

    def extend_subtitles(self, iter_subtitles):
        # assumes all members of the iterator are SubtitleLine
        self.subtitles.extend(iter_subtitles)

    @lru_cache(maxsize=None)
    def get_subtitle_file(self):
        return webvtt.read(self.get_subtitle_path())

    def get_hashed_basename(self):
        hashed_name = base64.b64encode(self._base_path.encode("utf-8"))
        return str(hashed_name, "utf-8")
