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
        lambda phs: model.choice.association_builder(*phs),
        zip(
            sequence_phonem(start_association.target_phonem),
            sequence_phonem(start_association.audio_phonem),
        ),
    )


def sequence_phonem(phonem):
    while phonem is not None:
        yield phonem
        phonem = phonem.next_in_seq()


def sequence_word(word):
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


@functools.lru_cache(maxsize=None)
def get_sequence_dictionary_homophones(target_phonem, audio_phonem):
    w0, w1 = target_phonem.word, audio_phonem.word
    return list(
        itertools.takewhile(
            lambda ws: are_homophones(*ws),
            zip(sequence_word(w0), sequence_word(w1),),
        )
    )


def has_at_least_one_node(base_nodes, total, rating):
    return base_nodes * rating >= total


def compute_nodes_left(base_nodes, total, rating):
    return base_nodes * rating / total


def association_sequence_from_words(words):
    return map(
        lambda x: model.choice.association_builder(*x),
        itertools.chain(
            *map(lambda w: zip(w[0].phonems, w[1].phonems), words)
        ),
    )
