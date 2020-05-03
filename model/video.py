from scipy.io import wavfile
from model.subtitleLine import SubtitleLine

class Video():
  def __init__(self, base_path, extension):
    self._base_path = base_path
    self._extension = extension
    self._wave = None
    self._subtitles = []

  def _get_audio_path(self):
    return self._base_path + '.wav'

  def get_video_path(self):
    return self._base_path + '.' + self._extension

  def get_subtitle_path(self):
    return self._base_path + '.vtt'

  def get_audio_wave(self):
    if self._wave is None:
      self._wave = wavfile.read(self._get_audio_path())
    return self._wave

  def add_subtitle(subtitle):
    assert type(subtitle) == SubtitleLine
    self._subtitles.append(subtitle)

  def extend_subtitles(iter_subtitle):
    # assumes all members of the iterator are SubtitleLine
    self._subtitles.extend(subtitles)