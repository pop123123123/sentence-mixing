import functools
import random

from sentence_mixing.model.association import association_builder

VIDEOS = None


def set_videos(videos):
    """Sets global variable VIDEOS and allows to use related functions"""

    global VIDEOS
    VIDEOS = videos


@functools.lru_cache(maxsize=1)
def get_all_audio_phonems():
    """
    Retrieve all the audio phonems from the video corpus
    Rases exception if video was not set before
    """

    global VIDEOS
    if VIDEOS is None:
        raise Exception(
            "Use set_videos(videos) before running get_all_audio_phonems()"
        )

    audio_phonems = [
        p
        for v in VIDEOS
        for s in v.subtitles
        for w in s.words
        for p in w.phonems
    ]
    random.shuffle(audio_phonems)
    return audio_phonems


@functools.lru_cache(maxsize=1)
def get_transcription_dict_audio_phonem():
    """
    Builds a dictionary associating each possible phonem transcriptions with a list containing
    every audio_phonem having this transcription.
    """

    transcription_audio_phonem_dict = dict()

    for phonem in get_all_audio_phonems():
        if phonem.transcription not in transcription_audio_phonem_dict:
            transcription_audio_phonem_dict[phonem.transcription] = [phonem]
        else:
            transcription_audio_phonem_dict[phonem.transcription].append(
                phonem
            )

    return transcription_audio_phonem_dict


@functools.lru_cache(maxsize=None)
def get_candidates(target_phonem):
    """
    Returns a list of associations where target phonem's transcription and audio phonem's
    transcription are the same.
    This list is sorted by score.
    """

    audio_phonems = get_transcription_dict_audio_phonem()[
        target_phonem.transcription
    ]
    associations = [
        association_builder(target_phonem, audio) for audio in audio_phonems
    ]

    return sorted(
        associations, key=lambda asso: asso.get_total_score(), reverse=True
    )
