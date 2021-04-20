import functools
import itertools

import sentence_mixing.logic.parameters as parameters
import sentence_mixing.logic.text_parser as tp
import sentence_mixing.model as model
from sentence_mixing.model.abstract import Word


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


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


def sequence_association(start_association, randomizer, reverse=False):
    return map(
        lambda phs: model.association.association_builder(*phs, randomizer),
        zip(
            sequence_phonem(start_association.target_phonem, reverse=reverse),
            sequence_phonem(start_association.audio_phonem, reverse=reverse),
        ),
    )


def sequence_phonem(phonem, reverse=False):
    while phonem is not None:
        yield phonem

        if not reverse:
            phonem = phonem.next_in_seq()
        else:
            phonem = phonem.previous_in_seq()


def sequence_word(word, force_first_blank=False):
    """
    This is a generator used to retrieve each word in a sentence, from the word given in parameter
    until the end of the sentence

    This function ignores <BLANK> token, which are artificial words added between each original
    words of a target sentence.

    Parameters:
    word - Word object where the sequence starts
    force_first_blank - used to force the function to return the first word if it is <BLANK>.
                        This is necessary to prevent first phonem of a word to 'steal' the <BLANK>.
                        Example:
                            - TargetSentence: "la <BLANK> puissance"
                            - In the subtitles, we can find full word "puissance"

                            If this system is not used, the best combo will associate phonem 'p'
                            (which is the first phonem of "puissance"), to word <BLANK> when
                            checking to the longest homophone sequence.
    """

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


@functools.lru_cache(maxsize=None)
def get_sequence_dictionary_homophones(
    target_phonem, audio_phonem, skip_force_blank=False
):
    """Retrieves the longest homophones sequence"""

    w0, w1 = target_phonem.word, audio_phonem.word
    return itertools.takewhile(
        lambda ws: are_homophones(*ws),
        # For audio word, we force the first <BLANK> token skipping to false
        # <BLANK> token words are only contained in token word
        zip(sequence_word(w0, skip_force_blank), sequence_word(w1, False),),
    )


def has_at_least_one_node(base_nodes, total, rating, steps_left):
    return (base_nodes - 1) * rating >= total * steps_left


def compute_nodes_left(base_nodes, total, rating):
    return (base_nodes - 1) * rating / total


def association_sequence_from_words(words, randomizer):
    return map(
        lambda x: model.association.association_builder(*x, randomizer),
        itertools.chain(
            *map(lambda w: zip(w[0].phonems, w[1].phonems), words)
        ),
    )


def recompute_scores(asso_scores, nodes_left, steps_left):
    sor = sorted(
        [(t, t[0].get_total_score() + sum(t[1])) for t in asso_scores],
        key=lambda x: x[1],
        reverse=True,
    )

    chosen = []
    total = 0
    modif = parameters.START_MODIF
    for asso_score, computed_rate in sor:
        computed_rate *= modif

        # Not enough nodes left
        if not has_at_least_one_node(
            nodes_left, total + computed_rate, computed_rate, steps_left
        ):
            # not trivial
            break

        # After each association pick, highly decreasesa score modifier
        modif /= parameters.RATE_POWER
        total += computed_rate
        chosen.append((asso_score[0], asso_score[1], computed_rate))
    # print(nodes_left, chosen)
    return chosen, total
