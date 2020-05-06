import functools
import itertools

import logic.text_parser as tp
from model.abstract import Word


def get_phonems(words_or_phonems):
    return list(
        itertools.chain(
            *map(
                lambda w: w.phonems if isinstance(w, Word) else [w],
                words_or_phonems,
            )
        )
    )


def sequence_word(word):
    while word is not None:
        if word.token != "<BLANK>":
            yield word
        word = word.next_in_seq()


@functools.lru_cache(maxsize=None)
def get_same_tokens(target_phonem, audio_phonem):
    w0, w1 = target_phonem, audio_phonem
    assert tp.from_token_to_phonem(w0.token) == tp.from_token_to_phonem(
        w1.token
    )
    return list(
        itertools.takewhile(
            lambda ws: tp.from_token_to_phonem(ws[0].token)
            == tp.from_token_to_phonem(ws[1].token),
            zip(sequence_word(w0), sequence_word(w1),),
        )
    )
