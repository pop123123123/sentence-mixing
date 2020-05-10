import functools
import math

import logic.parameters as params
import logic.randomizer as rnd
import logic.text_parser as tp


def get_malus(length, max_length, max_malus):
    if length > max_length:
        multiplier = math.sqrt(max_malus) / max_length
        return min(((length - max_length) * multiplier) ** 2, max_malus,)
    return 0


@functools.lru_cache(maxsize=None)
def score_length(audio_phonem):
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
    malus = (max((params.MINIMAL_PHONEM_LENGTH - length), 0) * multiplier) ** 2

    c_v_dict = tp.get_consonant_vowel_dict()
    if c_v_dict[audio_phonem.transcription] == "CONSONANT":
        malus += get_malus(
            length,
            params.MAXIMAL_CONSONANT_LENGTH,
            params.MAXIMAL_MAXIMAL_CONSONANT_LENGTH_MALUS,
        )
    elif c_v_dict[audio_phonem.transcription] == "VOWEL":
        malus += get_malus(
            length,
            params.MAXIMAL_VOWEL_LENGTH,
            params.MAXIMAL_MAXIMAL_VOWEL_LENGTH_MALUS,
        )
    elif c_v_dict[audio_phonem.transcription] == "SPACE":
        pass
    return -malus
