import functools

from model.association import association_builder

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
    return audio_phonems


@functools.lru_cache(maxsize=None)
def get_all_associations(target_phonem):
    """Returns all possible associations for a given target_phonem"""

    audio_phonems = get_all_audio_phonems()
    return [
        association_builder(target_phonem, audio_phonem)
        for audio_phonem in audio_phonems
    ]


@functools.lru_cache(maxsize=None)
def get_candidates(target_phonem):
    """Returns best association candidates for a given target_phonem"""

    associations = get_all_associations(target_phonem)
    return sorted(
        associations, key=lambda asso: asso.get_total_score(), reverse=True,
    )
