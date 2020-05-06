import functools
import itertools

import logic.parameters as params
import logic.utils as utils
from model.abstract import Sentence, Word


def get_last_phonem(audio):
    if isinstance(audio, Sentence):
        audio = audio.words[-1]
    if isinstance(audio, Word):
        audio = audio.phonems[-1]
    return audio


@functools.lru_cache(maxsize=None)
def step_3_audio_rating(previous_audio_phonem, audio_phonem):
    # TODO audio matching
    return 0


def step_3_n_following_previous_phonems(audio_chosen, audio_phonem):
    n = 0
    previous_phonems = utils.get_phonems(audio_chosen)
    audio_phonem = audio_phonem.previous_in_seq()
    while len(previous_phonems) > 0 and audio_phonem == previous_phonems.pop():
        audio_phonem = audio_phonem.previous_in_seq()
        n += 1
    return n


def step_3_rating(audio_chosen, audio_phonem):
    rate = 0

    last_phonem = get_last_phonem(audio_chosen[-1])
    rate += step_3_audio_rating(last_phonem, audio_phonem)

    rate += (
        params.RATING_LENGTH_SAME_PHONEM
        * step_3_n_following_previous_phonems(audio_chosen, audio_phonem)
    )

    return rate
