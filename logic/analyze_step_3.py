import functools
import itertools

import logic.audio_analysis as audio_analysis
import logic.parameters as params
import logic.text_parser as tp
import logic.utils as utils
import model.choice
from model.abstract import Sentence, Word


def get_last_phonem(audio):
    if isinstance(audio, Sentence):
        audio = audio.words[-1]
    if isinstance(audio, Word):
        audio = audio.phonems[-1]
    return audio


def get_last_vowel(choices):
    c_v_dict = tp.get_consonant_vowel_dict()
    for choice in choices:
        if c_v_dict[choice.association.audio_phonem.transcription] == "VOWEL":
            return choice.association.audio_phonem
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


def step_3_n_following_previous_phonems(choices):
    return utils.count_finite_iterable(
        itertools.takewhile(
            lambda c: c.association.target_phonem.word.token == "<BLANK>"
            or (
                c.parent is not None
                and c.association.audio_phonem.previous_in_seq()
                == c.parent.association.audio_phonem
            ),
            choices,
        )
    )


def step_3_rating(choice, association):
    choices = list(choice.get_self_and_previous_choices())

    choices.insert(0, model.choice.Choice(choices[0], association, 1, 0, 0))

    if len(choices) > 1:
        rate = []

        rate.append(
            step_3_audio_rating(
                get_last_vowel(choices), choice.association.audio_phonem
            )
            * params.RATING_SPECTRAL_SIMILARITY
        )

        rate.append(
            params.RATING_LENGTH_SAME_PHONEM
            * step_3_n_following_previous_phonems(choices)
        )

        return rate
    return [0, 0]
