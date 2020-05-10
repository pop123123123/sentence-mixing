import functools
import itertools

import logic.audio_analysis as audio_analysis
import logic.parameters as params
import logic.text_parser as tp
import logic.utils as utils
from model.abstract import Sentence, Word


def get_last_phonem(audio):
    if isinstance(audio, Sentence):
        audio = audio.words[-1]
    if isinstance(audio, Word):
        audio = audio.phonems[-1]
    return audio


def get_last_vowel(associations):
    for a in associations:
        if a.audio_phonem.get_type() == "VOWEL":
            return a.audio_phonem
    return None


@functools.lru_cache(maxsize=None)
def step_3_audio_rating(last_vowel, audio_phonem):
    # TODO split by words
    score = 0
    if last_vowel is not None and audio_phonem.get_type() == "VOWEL":
        (rate, last_vowel_wave), (_, current_wave) = tuple(
            audio_analysis.resample_highest_rate(
                [last_vowel.get_wave(), audio_phonem.get_wave()]
            )
        )
        score += audio_analysis.cross_power_spectral_density_sum(
            current_wave, last_vowel_wave, rate
        )
    return score


def step_3_n_following_previous_phonems(associations):
    i = 0
    while i < len(associations) - 1:
        a = associations[i]
        parent = associations[i + 1]

        if a.audio_phonem.previous_in_seq() == parent.audio_phonem:
            i += 1
        else:
            break
    return i
