import functools
import itertools

import logic.text_parser as tp
import model
from model.abstract import Word


def count_finite_iterable(iterable):
    return sum(1 for _ in iterable)


def get_phonems(words_or_phonems):
    return list(
        itertools.chain(
            *map(
                lambda w: w.phonems if isinstance(w, Word) else [w],
                words_or_phonems,
            )
        )
    )


def sequence_association(start_association):
    return map(
        lambda phs: model.association.association_builder(*phs),
        zip(
            sequence_phonem(start_association.target_phonem),
            sequence_phonem(start_association.audio_phonem),
        ),
    )


def sequence_phonem(phonem):
    while phonem is not None:
        yield phonem
        phonem = phonem.next_in_seq()


# TODO: le force_firt_blank est dé-gueu-lasse mais nécessaire pour éviter les effets de bord
def sequence_word(word, force_first_blank=False):
    if force_first_blank and word.token == "<BLANK>":
        yield word

    while word is not None:
        if word.token != "<BLANK>":
            yield word
        word = word.next_in_seq()


@functools.lru_cache(maxsize=None)
def get_sequence_aligner_homophones(target_phonem, audio_phonem):
    w0, w1 = target_phonem.word, audio_phonem.word
    return list(
        itertools.takewhile(
            lambda ws: ws[0].has_same_phonems_transcription(ws[1]),
            zip(sequence_word(w0), sequence_word(w1),),
        )
    )


@functools.lru_cache(maxsize=None)
def are_homophones(target_word, audio_word):
    try:
        return tp.are_token_homophones(target_word.token, audio_word.token)
    except model.exceptions.TokenAmbiguityError:
        return target_word.has_same_phonems_transcription(audio_word)


# TODO: changer le système de force_first_blank
@functools.lru_cache(maxsize=None)
def get_sequence_dictionary_homophones(
    target_phonem, audio_phonem, skip_force_blank=False
):
    w0, w1 = target_phonem.word, audio_phonem.word
    return list(
        itertools.takewhile(
            lambda ws: are_homophones(*ws),
            zip(
                sequence_word(w0, skip_force_blank), sequence_word(w1, False),
            ),
        )
    )


def has_at_least_one_node(base_nodes, total, rating):
    return base_nodes * rating >= total


def compute_nodes_left(base_nodes, total, rating):
    return base_nodes * rating / total


def association_sequence_from_words(words):
    return map(
        lambda x: model.association.association_builder(*x),
        itertools.chain(
            *map(lambda w: zip(w[0].phonems, w[1].phonems), words)
        ),
    )
