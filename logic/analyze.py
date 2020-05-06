import functools
import itertools
import math
import random

import logic.text_parser as tp
from model.abstract import Phonem, Sentence, Word
from model.exceptions import PhonemError


def noise_score(base_score, sigma=None):
    if not sigma:
        sigma = base_score * 0.2

    return random.gauss(base_score, sigma)


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
def get_same_tokens(target_phonem, audio_phonem):
    w0, w1 = target_phonem, audio_phonem
    assert w0.token == w1.token
    return list(
        itertools.takewhile(
            lambda ws: ws[0].token == ws[1].token,
            zip(sequence_word(w0), sequence_word(w1),),
        )
    )


RATING_LENGTH_SAME_PHONEM = 80
RATING_LENGTH_SAME_WORD = 100


def rating_sequence_by_phonem_length(x):
    return noise_score(RATING_LENGTH_SAME_PHONEM) * x


def rating_word_by_phonem_length(x):
    return noise_score(RATING_LENGTH_SAME_WORD) * x


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
        target_phonem.word.token == audio_phonem.word.token
        and target_phonem.get_index_in_word()
        == audio_phonem.get_index_in_word()
    ):
        n_same_tokens = sum(
            len(w.phonems)
            for w, _ in get_same_tokens(target_phonem.word, audio_phonem.word)
        )
        return rating_word_by_phonem_length(n_same_tokens)
    return 0


SCORE_SAME_TRANSCRIPTION = 200


MINIMAL_PHONEM_LENGTH = 0.1
MAXIMAL_MINIMAL_PHONEM_LENGH_MALUS = 1000

MAXIMAL_CONSONANT_LENGTH = 0.25
MAXIMAL_MAXIMAL_CONSONANT_LENGTH_MALUS = 1000

MAXIMAL_VOWEL_LENGTH = 0.5
MAXIMAL_MAXIMAL_VOWEL_LENGTH_MALUS = 1000


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
        math.sqrt(MAXIMAL_MINIMAL_PHONEM_LENGH_MALUS) / MINIMAL_PHONEM_LENGTH
    )
    malus = ((MINIMAL_PHONEM_LENGTH - length) * multiplier) ** 2

    c_v_dict = tp.get_consonant_vowel_dict()
    if c_v_dict[audio_phonem.transcription] == "CONSONANT":
        if length > MAXIMAL_CONSONANT_LENGTH:
            multiplier = (
                math.sqrt(MAXIMAL_MAXIMAL_CONSONANT_LENGTH_MALUS)
                / MAXIMAL_CONSONANT_LENGTH
            )
            malus += min(
                ((length - MAXIMAL_CONSONANT_LENGTH) * multiplier) ** 2,
                MAXIMAL_MAXIMAL_CONSONANT_LENGTH_MALUS,
            )
    elif c_v_dict[audio_phonem.transcription] == "VOWEL":
        if length > MAXIMAL_CONSONANT_LENGTH:
            multiplier = (
                math.sqrt(MAXIMAL_MAXIMAL_VOWEL_LENGTH_MALUS)
                / MAXIMAL_VOWEL_LENGTH
            )
            malus += min(
                ((length - MAXIMAL_VOWEL_LENGTH) * multiplier) ** 2,
                MAXIMAL_MAXIMAL_VOWEL_LENGTH_MALUS,
            )
    elif c_v_dict[audio_phonem.transcription] == "SPACE":
        pass

    return -malus


@functools.lru_cache(maxsize=None)
def rating(target_phonem, audio_phonem):
    score = 0

    # Apply malus on phonem length
    score += score_length(audio_phonem)

    # Parts of the same word
    score += get_word_similarity(target_phonem, audio_phonem)

    # Same phonem sequence
    score += get_phonem_similarity(target_phonem, audio_phonem)

    # Wave Context TODO

    # Same transcription
    if target_phonem.transcription == audio_phonem.transcription:
        score += noise_score(SCORE_SAME_TRANSCRIPTION)

    return score


@functools.lru_cache(maxsize=None)
def step_3_audio_rating(previous_audio_phonem, audio_phonem):
    # TODO audio matching
    return 0


def step_3_n_following_previous_phonems(audio_chosen, audio_phonem):
    n = 0
    previous_phonems = get_phonems(audio_chosen)
    audio_phonem = audio_phonem.previous_in_seq()
    while len(previous_phonems) > 0 and audio_phonem == previous_phonems.pop():
        audio_phonem = audio_phonem.previous_in_seq()
        n += 1
    return n


def get_last_phonem(audio):
    if isinstance(audio, Sentence):
        audio = audio.words[-1]
    if isinstance(audio, Word):
        audio = audio.phonems[-1]
    return audio


NODES = 1 << 12
SCORE_THRESHOLD = 50
RIGHT_PRIVILEGE = 0.8

SCORE_SAME_AUDIO_WORD = 200


def get_phonems(words_or_phonems):
    return list(
        itertools.chain(
            *map(
                lambda w: w.phonems if isinstance(w, Word) else [w],
                words_or_phonems,
            )
        )
    )


MAX_DEFAULT_RATE = 500


def get_n_best_combos(sentence, videos, n=100):
    audio_phonems = [
        p
        for v in videos
        for s in v.subtitles
        for w in s.words
        for p in w.phonems
    ]
    target_phonems = get_phonems(sentence.words)
    # Rate all associations

    # split, then call get_best_combos with subset of words from
    # the split sentence

    @functools.lru_cache(maxsize=None)
    def get_candidates(target_phonem):
        return sorted(
            audio_phonems, key=lambda x: rating(target_phonem, x), reverse=True
        )

    def get_best_combos(
        audio_chosen, t_p, nodes_left, associated_target_words
    ):
        total = 0
        rates = []

        candidates = get_candidates(t_p)

        rate = random.uniform(0, MAX_DEFAULT_RATE)

        modif = 1.0
        # Rating
        for audio_phonem in candidates:
            rate = rating(t_p, audio_phonem)
            if len(audio_chosen) > 0:
                last_phonem = get_last_phonem(audio_chosen[-1])
                rate += step_3_audio_rating(last_phonem, audio_phonem)
                rate += (
                    RATING_LENGTH_SAME_PHONEM
                    * step_3_n_following_previous_phonems(
                        audio_chosen, audio_phonem
                    )
                )
                rate += (
                    t_p.word.token == audio_phonem.word.token
                ) * noise_score(SCORE_SAME_AUDIO_WORD)

            rate *= modif
            # not enough nodes left
            if nodes_left * rate < (total + rate):
                # not trivial
                break

            modif *= RIGHT_PRIVILEGE
            total += rate
            rates.append(rate)

        if total == 0:
            raise PhonemError(t_p)

        rates = [r ** 2 for r in rates]
        total = sum(rates)

        combos = []
        # Exploration
        for audio_phonem, rate_chosen in zip(candidates, rates):
            new_chosen = audio_chosen.copy()
            new_associated = associated_target_words.copy()

            nodes = math.ceil(nodes_left * rate_chosen / total)
            next_target_phonem = t_p.next_in_seq()
            # Phonem skipping if word similarity found
            if (
                t_p.word.token == audio_phonem.word.token
                and t_p.word.token != "<BLANK>"
                and t_p.get_index_in_word() == audio_phonem.get_index_in_word()
            ):
                n = 0
                for t_w, audio_word in get_same_tokens(
                    t_p.word, audio_phonem.word
                ):
                    n_phon = 0
                    if (
                        audio_word == audio_phonem.word
                        and audio_phonem.get_index_in_word() != 0
                    ):
                        # add current word left phonems
                        new_chosen.extend(
                            audio_word.phonems[
                                audio_phonem.get_index_in_word() :
                            ]
                        )
                        n_phon = (
                            len(audio_word.phonems)
                            - audio_phonem.get_index_in_word()
                        )
                    else:
                        # add next word(s) phonems
                        new_chosen.append(audio_word)
                        n_phon = len(audio_word.phonems)
                    n += n_phon
                    new_associated.extend([t_w] * n_phon)
                last_target_word = get_same_tokens(
                    t_p.word, audio_phonem.word
                )[-1][0]

                # update current phonem
                next_target_phonem = last_target_word.phonems[-1].next_in_seq()
                rate_chosen *= n
                if next_target_phonem is None:
                    combos.append((new_chosen, new_associated, rate_chosen))
                    continue
            else:
                new_chosen += [audio_phonem]
                new_associated += [t_p.word]
            # stop condition
            if target_phonems[-1] == next_target_phonem:
                combos.append((new_chosen, new_associated, rate_chosen))
            else:
                for chosen, associated, rate in get_best_combos(
                    new_chosen, next_target_phonem, nodes, new_associated
                ):
                    combos.append((chosen, associated, rate + rate_chosen))

        return combos

    combos = None
    if len(target_phonems) == 1:
        combos = [
            ([a_p], [target_phonems[0].word], [rating(target_phonems[0], a_p)])
            for a_p in get_candidates(target_phonems[0])[:n]
        ]
    else:
        combos = get_best_combos([], target_phonems[0], NODES, [])
        combos = sorted(combos, key=lambda c: c[2], reverse=True)
    return combos
