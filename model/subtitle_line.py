from model.sentence import Sentence
from model.audio_segment import AudioSegment
from model.audio_word import AudioWord

class SubtitleLine(Sentence, AudioSegment):
  def __init__(self, original_text, start, end, video):
    Sentence.__init__(self, original_text)
    AudioSegment.__init__(self, start, end)
    self.video = video
    self._words = []

  def add_word(word):
    assert type(word) == AudioWord
    self._subtitles.append(word)

  def extend_subtitles(iter_subtitles):
    # assumes all members of the iterator are SubtitleLine
    self._subtitles.extend(iter_subtitles)

  def _get_wave_path(self):
    return self.video.get_audio_wave()
