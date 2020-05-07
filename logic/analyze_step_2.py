import functools
import itertools

import logic.parameters as params
import logic.randomizer as rnd
import logic.text_parser as tp
import logic.utils as utils


def rating_sequence_by_phonem_length(x):
    return rnd.noise_score(params.RATING_LENGTH_SAME_PHONEM) * x


def rating_word_by_phonem_length(x):
    return rnd.noise_score(params.RATING_LENGTH_SAME_WORD) * x


@functools.lru_cache(maxsize=None)
def get_word_phonem_similarity(association):
    n_same_tokens = len(
        list(association.sequence_aligner_homophones_phonems())
    )
    return rating_word_by_phonem_length(n_same_tokens)


@functools.lru_cache(maxsize=None)
def get_same_phonems_in_word(target_phonem, audio_phonem):
    w0, w1 = target_phonem, audio_phonem
    assert tp.from_token_to_phonem(w0.token) == w1.phonems
    return list(
        itertools.takewhile(
            lambda ws: ws[0].phonems == ws[1].phonems,
            zip(utils.sequence_word(w0), utils.sequence_word(w1),),
        )
    )
