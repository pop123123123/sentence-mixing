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


def sequence_phonem(phonem):
    while phonem is not None:
        yield phonem
        phonem = phonem.next_in_seq()


@functools.lru_cache(maxsize=None)
def get_phonem_similarity(target_phonem, audio_phonem):
    p0, p1 = target_phonem, audio_phonem
    n_same_transcriptions = len(
        list(
            itertools.takewhile(
                lambda ps: ps[0].transcription == ps[1].transcription,
                zip(sequence_phonem(p0), sequence_phonem(p1),),
            )
        )
    )
    return rating_sequence_by_phonem_length(n_same_transcriptions)


@functools.lru_cache(maxsize=None)
def get_word_similarity(target_phonem, audio_phonem):
    if (
        tp.are_token_homophones(
            target_phonem.word.token, audio_phonem.word.token
        )
        and target_phonem.get_index_in_word()
        == audio_phonem.get_index_in_word()
    ):
        n_same_tokens = sum(
            len(w.phonems)
            for w, _ in utils.get_same_tokens(
                target_phonem.word, audio_phonem.word
            )
        )
        return rating_word_by_phonem_length(n_same_tokens)
    return 0


@functools.lru_cache(maxsize=None)
def get_word_phonem_similarity(target_phonem, audio_phonem):
    if (
        tp.from_token_to_phonem(target_phonem.word.token)
        == audio_phonem.word.phonems
        and target_phonem.get_index_in_word()
        == audio_phonem.get_index_in_word()
    ):
        n_same_tokens = sum(
            len(w.phonems)
            for w, _ in get_same_phonems_in_word(
                target_phonem.word, audio_phonem.word
            )
        )
        return rating_word_by_phonem_length(n_same_tokens)
    return 0


@functools.lru_cache(maxsize=None)
def get_same_phonems_in_word(target_phonem, audio_phonem):
    w0, w1 = target_phonem, audio_phonem
    assert tp.from_token_to_phonem(w0.token) == w1.phonems
    return list(
        itertools.takewhile(
            lambda ws: tp.from_token_to_phonem(ws[0].token) == ws[1].phonems,
            zip(utils.sequence_word(w0), utils.sequence_word(w1),),
        )
    )


@functools.lru_cache(maxsize=None)
def step_2_rating(target_phonem, audio_phonem):
    score = []

    # Parts of the same word
    score.append(get_word_similarity(target_phonem, audio_phonem))

    # Parts of the same
    score.append(get_word_phonem_similarity(target_phonem, audio_phonem))

    # Same phonem sequence
    score.append(get_phonem_similarity(target_phonem, audio_phonem))

    # Wave Context TODO

    # Same transcription
    score.append(
        (target_phonem.transcription == audio_phonem.transcription)
        * rnd.noise_score(params.SCORE_SAME_TRANSCRIPTION)
    )

    return score
