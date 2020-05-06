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


def get_last_vowel(audio_chosen):
    c_v_dict = tp.get_consonant_vowel_dict()
    for audio_seg in reversed(audio_chosen):
        if isinstance(audio_seg, Word):
            for audio_phonem in reversed(audio_seg.phonems):
                if c_v_dict[audio_phonem.transcription] == "VOWEL":
                    return audio_phonem
        elif c_v_dict[audio_seg.transcription] == "VOWEL":
            return audio_seg
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


def step_3_n_following_previous_phonems(audio_chosen, audio_phonem):
    n = 0
    previous_phonems = utils.get_phonems(audio_chosen)
    audio_phonem = audio_phonem.previous_in_seq()
    while len(previous_phonems) > 0 and audio_phonem == previous_phonems.pop():
        audio_phonem = audio_phonem.previous_in_seq()
        n += 1
    return n


def step_3_rating(audio_chosen, audio_phonem):
    if len(audio_chosen) > 0:
        rate = 0

        rate += (
            step_3_audio_rating(get_last_vowel(audio_chosen), audio_phonem)
            * params.RATING_SPECTRAL_SIMILARITY
        )

        rate += (
            params.RATING_LENGTH_SAME_PHONEM
            * step_3_n_following_previous_phonems(audio_chosen, audio_phonem)
        )

        return rate
    return 0
