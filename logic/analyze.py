import functools
import itertools
import math


def sequence_word(word):
    while word is not None:
        if word.token is not None:
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


def rating_word_by_phonem_length(x):
    return 100 * x


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


@functools.lru_cache(maxsize=None)
def rating(target_phonem, audio_phonem):
    score = 0

    # Parts of the same word
    score += get_word_similarity(target_phonem, audio_phonem)

    # Wave Context TODO

    # Same transcription
    if target_phonem.transcription == audio_phonem.transcription:
        score += SCORE_SAME_TRANSCRIPTION

    return score


@functools.lru_cache(maxsize=None)
def step_3_audio_rating(previousaudio_phonem, audio_phonem):
    # TODO audio matching
    return 0


NODES = 1 << 12
SCORE_THRESHOLD = 50

SCORE_SAME_AUDIO_WORD = 200


def get_n_best_combos(sentence, videos, n=10):
    audio_phonems = [
        p
        for v in videos
        for s in v.subtitles
        for w in s.words
        for p in w.phonems
    ]
    target_phonems = list(
        itertools.chain(*map(lambda w: w.phonems, sentence.words))
    )
    target_phonems_indices = {ph: i for i, ph in enumerate(target_phonems)}
    # Rate all associations

    # split, then call get_best_combos with subset of words from
    # the split sentence

    @functools.lru_cache(maxsize=None)
    def get_candidates(target_phonem):
        return sorted(
            audio_phonems, key=lambda x: rating(target_phonem, x), reverse=True
        )

    def get_best_combos(audio_chosen, t_p, nodes_left):
        total = 0
        rates = []

        candidates = get_candidates(t_p)

        # Rating
        for audio_phonem in candidates:
            rate = rating(t_p, audio_phonem)
            if len(audio_chosen) > 0:
                rate += step_3_audio_rating(audio_chosen[-1], audio_phonem)
                rate += (
                    audio_chosen[-1].word == audio_phonem.word
                ) * SCORE_SAME_AUDIO_WORD

            # not enough nodes left
            if nodes_left * rate < (total + rate):
                # not trivial
                break

            total += rate
            rates.append(rate)

        combos = []
        # Exploration
        for audio_phonem, rate_chosen in zip(candidates, rates):
            new_chosen = audio_chosen + [audio_phonem]

            nodes = math.ceil(nodes_left * rate_chosen / total)
            next_target_phonem = target_phonems[
                target_phonems_indices[t_p] + 1
            ]
            # Phonem skipping if word similarity found
            if (
                t_p.word.token == audio_phonem.word.token
                and t_p.get_index_in_word() == audio_phonem.get_index_in_word()
                and get_same_tokens(t_p.word, audio_phonem.word)[-1][
                    0
                ].phonems[-1]
                != t_p
            ):
                n = target_phonems_indices[next_target_phonem]
                for _, audio_word in get_same_tokens(
                    t_p.word, audio_phonem.word
                ):
                    if audio_word == audio_phonem.word:
                        # add current word left phonems
                        # Should be within bounds, otherwise get back on paper
                        new_chosen.extend(
                            audio_word.phonems[
                                audio_phonem.get_index_in_word() + 1 :
                            ]
                        )
                    else:
                        # add next word(s) phonems
                        new_chosen.extend(audio_word.phonems)
                last_target_word = get_same_tokens(
                    t_p.word, audio_phonem.word
                )[-1][0]
                # update current phonem
                next_target_phonem = last_target_word.phonems[-1]
                rate_chosen *= (
                    target_phonems_indices[next_target_phonem] - n + 1
                )
            # stop condition
            if target_phonems[-1] == next_target_phonem:
                combos.append((new_chosen, rate_chosen))
            else:
                for chosen, rate in get_best_combos(
                    new_chosen, next_target_phonem, nodes
                ):
                    combos.append((chosen, rate + rate_chosen))

        return combos

    combos = get_best_combos([], target_phonems[0], NODES)
    combos = sorted(combos, key=lambda c: c[1], reverse=True)
    return list(map(lambda c: c[0], combos[:n]))
