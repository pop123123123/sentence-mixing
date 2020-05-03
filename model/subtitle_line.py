from model.sentence import Sentence
from model.audio_segment import Audible

class SubtitleLine(Sentence, Audible):
  def __init__(self, original_text):
    Sentence.__init__(self, original_text)
    self._words = []

  def add_word(word):
    assert type(subtitle) == SubtitleLine
    self._subtitles.append(subtitle)

  def extend_subtitles(iter_subtitle):
    # assumes all members of the iterator are SubtitleLine
    self._subtitles.extend(subtitles)