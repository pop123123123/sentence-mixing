import functools
import math
import random

import logic.parameters as params
import logic.text_parser as tp


@functools.lru_cache(maxsize=None)
def _score_length(audio_phonem):
    """
    Assigns a score malus to an audio phonem depending on the length of its audio and its phonem type

    The malus is computed following a quadratic distance to a length limit.

    These limits are more or less severe depending of the type of the phonem (consonant, vowel or
    space)

    Returns: a negative score corresponding to a negative malus
    """

    length = audio_phonem.get_length()

    multiplier = (
        math.sqrt(params.MAXIMAL_MINIMAL_PHONEM_LENGH_MALUS)
        / params.MINIMAL_PHONEM_LENGTH
    )
    malus = ((params.MINIMAL_PHONEM_LENGTH - length) * multiplier) ** 2

    c_v_dict = tp.get_consonant_vowel_dict()
    if c_v_dict[audio_phonem.transcription] == "CONSONANT":
        if length > params.MAXIMAL_CONSONANT_LENGTH:
            multiplier = (
                math.sqrt(params.MAXIMAL_MAXIMAL_CONSONANT_LENGTH_MALUS)
                / params.MAXIMAL_CONSONANT_LENGTH
            )
            malus += min(
                ((length - params.MAXIMAL_CONSONANT_LENGTH) * multiplier) ** 2,
                params.MAXIMAL_MAXIMAL_CONSONANT_LENGTH_MALUS,
            )
    elif c_v_dict[audio_phonem.transcription] == "VOWEL":
        if length > params.MAXIMAL_CONSONANT_LENGTH:
            multiplier = (
                math.sqrt(params.MAXIMAL_MAXIMAL_VOWEL_LENGTH_MALUS)
                / params.MAXIMAL_VOWEL_LENGTH
            )
            malus += min(
                ((length - params.MAXIMAL_VOWEL_LENGTH) * multiplier) ** 2,
                params.MAXIMAL_MAXIMAL_VOWEL_LENGTH_MALUS,
            )
    elif c_v_dict[audio_phonem.transcription] == "SPACE":
        pass

    return -malus


@functools.lru_cache(maxsize=None)
def step_1_rating(audio_phonem):
    score = 0

    # Assigns random score to each audio phonem
    score += random.uniform(0, params.MAX_DEFAULT_RATE)

    # Apply malus on phonem length
    score += _score_length(audio_phonem)

    return score
