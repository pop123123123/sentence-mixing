import functools
import random

from sentence_mixing.model.association import association_builder


@functools.lru_cache(maxsize=3)
def audioDataFactory(videos):
    return AudioData(videos)


class AudioData:
    def __init__(self, videos):
        self.videos = videos

    @functools.lru_cache(maxsize=1)
    def get_all_audio_phonems(self, randomizer):
        """
        Retrieve all the audio phonems from the video corpus
        Rases exception if video was not set before
        """

        audio_phonems = [
            p
            for v in self.videos
            for s in v.subtitles
            for w in s.words
            for p in w.phonems
        ]
        randomizer.rand.shuffle(audio_phonems)
        return audio_phonems

    @functools.lru_cache(maxsize=1)
    def get_transcription_dict_audio_phonem(self, randomizer):
        """
        Builds a dictionary associating each possible phonem transcriptions with a list containing
        every audio_phonem having this transcription.
        """

        transcription_audio_phonem_dict = dict()

        for phonem in self.get_all_audio_phonems(randomizer):
            if phonem.transcription not in transcription_audio_phonem_dict:
                transcription_audio_phonem_dict[phonem.transcription] = [
                    phonem
                ]
            else:
                transcription_audio_phonem_dict[phonem.transcription].append(
                    phonem
                )

        return transcription_audio_phonem_dict

    @functools.lru_cache(maxsize=None)
    def get_candidates(self, target_phonem, randomizer):
        """
        Returns a list of associations where target phonem's transcription and audio phonem's
        transcription are the same.
        This list is sorted by score.
        """

        audio_phonems = self.get_transcription_dict_audio_phonem(randomizer)[
            target_phonem.transcription
        ]
        associations = [
            association_builder(target_phonem, audio, randomizer)
            for audio in audio_phonems
        ]

        return sorted(
            associations, key=lambda asso: asso.get_total_score(), reverse=True
        )
