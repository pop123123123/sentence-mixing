import os

from scipy.io import wavfile

from audio_segment import AudioSegment


class Subtitle(AudioSegment):
    """This class represent a subtitle related to the audio file
    audio_path corresponds to the generated mini audio file containing the sub's related audio"""

    def __init__(self, start_timestamp, end_timestamp, subtitle):
        AudioSegment.__init__(
            self, start_timestamp, end_timestamp, subtitle, None
        )
        self._mini_audio = None

    def get_subtitle(self):
        return self._text

    def create_audio(self, save_path, full_audio_path, wave_file=None):
        """Saves sub's related audio in a separate audio file"""

        self._audio_path = full_audio_path

        if self._mini_audio:
            raise Exception(
                "Corresponding audio file has already been saved in",
                self._mini_audio,
            )

        if not save_path.endswith(".wav"):
            raise Exception(
                "Subtitles file must have .wav extension (Received",
                save_path,
                ")",
            )

        self._mini_audio = save_path

        if wave_file is None:
            rate, data = wavfile.read(full_audio_path)
        else:
            rate, data = wave_file

        # Audio processing
        # Cuts the audio file at the proper frames
        # Saves the new audio to an individual file
        start_frame = int(self._start * rate)
        end_frame = int(self._end * rate)

        sub_audio_data = data[start_frame:end_frame]
        wavfile.write(os.path.join(save_path), rate, sub_audio_data)

    def save_sub(self, save_path):
        """Saves sub text in a proper text file"""

        if not save_path.endswith(".lab"):
            raise Exception(
                "Subtitles file must have .lab extension (Received",
                save_path,
                ")",
            )

        # Writes the subtitle in a .lab file
        with open(save_path, "w") as subfile:
            subfile.write(self._text)

    def get_basename_audio(self):
        return os.path.basename(self._mini_audio)[:-4]
