import functools
import itertools
import math
import random


def noise_score(base_score, sigma=None):
    if not sigma:
        sigma = base_score * 0.2

    return random.gauss(base_score, sigma)


@functools.lru_cache(maxsize=None)
def get_same_tokens(starting_word0, starting_word1):
    w0, w1 = starting_word0, starting_word1
    return itertools.takewhile(
        lambda ws: ws[0].token == ws[1].token,
        zip(
            w0.sentence.words[w0.get_index_in_sentence() :],
            w1.sentence.words[w0.get_index_in_sentence() :],
        ),
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
    # Rate all associations

    # split, then call get_best_combos with subset of words from
    # the split sentence

    @functools.lru_cache(maxsize=None)
    def get_candidates(target_phonem):
        return sorted(
            audio_phonems, key=lambda x: rating(target_phonem, x), reverse=True
        )

    def get_best_combos(audio_chosen, nodes_left):
        import code

        # code.interact(local=locals())
        total = 0
        rates = []
        t_p = target_phonems[len(audio_chosen)]

        candidates = get_candidates(t_p)

        # Rating
        for audio_phonem in candidates:
            rate = rating(t_p, audio_phonem)
            if len(audio_chosen) > 0:
                rate += step_3_audio_rating(audio_chosen[-1], audio_phonem)
            rate += get_word_similarity(t_p, audio_phonem)

            total += rate

            # not enough nodes left
            if nodes_left * rate < total:
                break
            rates.append(rate)

        combos = []
        # Exploration
        for audio_phonem, rate_chosen in zip(candidates, rates):
            new_chosen = audio_chosen + [audio_phonem]
            if len(audio_chosen) + 1 == len(target_phonems):
                combos.append((new_chosen, rate_chosen))
            else:
                nodes = math.ceil(nodes_left * rate_chosen / total)
                # Phonem skipping if word similarity found
                if (
                    t_p.word.token == audio_phonem.word.token
                    and t_p.get_index_in_word()
                    == audio_phonem.get_index_in_word()
                ):
                    n = len(new_chosen)
                    for _, audio_word in get_same_tokens(
                        t_p.word, audio_phonem.word
                    ):
                        if audio_word == audio_phonem.word:
                            # Should be within bounds, otherwise get back on paper
                            new_chosen.extend(
                                audio_word.phonems[
                                    audio_phonem.get_index_in_word() + 1
                                ]
                            )
                        else:
                            new_chosen.extend(audio_word.phonems)
                    rate_chosen *= (len(new_chosen) - n) + 1

                for chosen, rate in get_best_combos(new_chosen, nodes):
                    combos.append((chosen, rate + rate_chosen))

        return combos

    combos = get_best_combos([], NODES)
    combos = sorted(combos, key=lambda c: c[1], reverse=True)
    return list(map(lambda c: c[0], combos[:n]))
