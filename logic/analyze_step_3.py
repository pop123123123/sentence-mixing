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
    c_v_dict = tp.get_consonant_vowel_dict()
    for a in associations:
        if c_v_dict[a.audio_phonem.transcription] == "VOWEL":
            return a.audio_phonem
    return None


@functools.lru_cache(maxsize=None)
def step_3_audio_rating(last_vowel, audio_phonem):
    # TODO split by words
    score = 0
    c_v_dict = tp.get_consonant_vowel_dict()
    if (
        last_vowel is not None
        and c_v_dict[audio_phonem.transcription] == "VOWEL"
    ):
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
    n = 0
    i = 0
    while i < len(associations) - 1:
        a = associations[i]
        parent = associations[i + 1]

        if (
            i != 0 and a.target_phonem.word.token == "<BLANK>"
        ) or a.audio_phonem.previous_in_seq() == parent.audio_phonem:
            n += 1
        i += 1
    return n
