import base64
from functools import lru_cache

import numpy as np
import webvtt
from moviepy.video.io.VideoFileClip import VideoFileClip
from scipy.io import wavfile

from sentence_mixing.model.audio import SubtitleLine


class Video:
    def __init__(self, url, base_path, subtitles_extension):
        self.url = url
        self._base_path = base_path
        self._subtitles_extension = subtitles_extension
        self.extension = None
        self.subtitles = []
        self.index_subtitles = {}

    def _get_audio_path(self):
        return self._base_path + ".wav"

    def _get_video_path(self):
        assert self.extension is not None
        return self._base_path + "." + self.extension

    def get_subtitle_path(self):
        return self._base_path + self._subtitles_extension

    @lru_cache(maxsize=None)
    def get_audio_wave(self):
        rate, data = wavfile.read(self._get_audio_path())
        if len(np.shape(data)) == 1 or data.shape[1] == 1:
            data = np.stack((data, data), axis=1)
        return (rate, data)

    @lru_cache(maxsize=None)
    def get_video(self):
        return VideoFileClip(self._get_video_path())

    def add_subtitle(self, subtitle):
        assert type(subtitle) == SubtitleLine
        self.index_subtitles[subtitle] = len(self.subtitles)
        self.subtitles.append(subtitle)

    def get_index_subtitle(self, subtitle):
        assert (
            self.index_subtitles is not None
            and subtitle in self.index_subtitles
        )
        return self.index_subtitles[subtitle]

    @lru_cache(maxsize=None)
    def get_subtitle_file(self):
        return webvtt.read(self.get_subtitle_path())

    def get_hashed_basename(self):
        hashed_name = base64.b64encode(self._base_path.encode("utf-8"))
        return str(hashed_name, "utf-8")
