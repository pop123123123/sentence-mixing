import functools
import math

import logic.analyze_step_1 as step_1
import logic.analyze_step_2 as step_2
import logic.analyze_step_3 as step_3
import logic.parameters as params
import logic.randomizer as rnd
import logic.text_parser as tp
import logic.utils as utils
from model.abstract import Phonem, Sentence, Word
from model.exceptions import PhonemError


def step_1_and_step_2_rating(target_phonem, audio_phonem):
    return step_1.step_1_rating(audio_phonem) + step_2.step_2_rating(
        target_phonem, audio_phonem
    )


def get_n_best_combos(sentence, videos, n=100):
    audio_phonems = [
        p
        for v in videos
        for s in v.subtitles
        for w in s.words
        for p in w.phonems
    ]

    target_phonems = utils.get_phonems(sentence.words)

    # Rate all associations

    # split, then call get_best_combos with subset of words from
    # the split sentence

    @functools.lru_cache(maxsize=None)
    def get_candidates(target_phonem):
        return sorted(
            audio_phonems,
            key=lambda x: step_1_and_step_2_rating(target_phonem, x),
            reverse=True,
        )

    def get_best_combos(
        audio_chosen, t_p, nodes_left, associated_target_words
    ):
        total = 0
        rates = []

        candidates = get_candidates(t_p)

        modif = params.START_MODIF
        # Rating
        for audio_phonem in candidates:
            rate = step_1_and_step_2_rating(t_p, audio_phonem)

            rate += step_3.step_3_rating(audio_chosen, audio_phonem)

            rate *= modif
            # not enough nodes left
            if nodes_left * rate < (total + rate):
                # not trivial
                break

            modif *= params.RIGHT_PRIVILEGE
            total += rate
            rates.append(rate)

        if total == 0:
            raise PhonemError(t_p)

        rates = [r ** params.RATE_POWER for r in rates]
        total = sum(rates)

        combos = []
        # Exploration
        for audio_phonem, rate_chosen in zip(candidates, rates):
            new_chosen = audio_chosen.copy()
            new_associated = associated_target_words.copy()
            new_scores = []

            nodes = math.ceil(nodes_left * rate_chosen / total)
            next_target_phonem = t_p.next_in_seq()
            # Phonem skipping if word similarity found
            if (
                t_p.word.token == audio_phonem.word.token
                and t_p.word.token != "<BLANK>"
                and t_p.get_index_in_word() == audio_phonem.get_index_in_word()
            ):
                n = 0
                for t_w, audio_word in utils.get_same_tokens(
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
                    new_scores.extend([rate_chosen] * n_phon)
                last_target_word = utils.get_same_tokens(
                    t_p.word, audio_phonem.word
                )[-1][0]

                # update current phonem
                next_target_phonem = last_target_word.phonems[-1].next_in_seq()
                if next_target_phonem is None:
                    combos.append((new_chosen, new_associated, new_scores))
                    continue
            else:
                new_chosen += [audio_phonem]
                new_associated += [t_p.word]
                new_scores += [rate_chosen]
            # stop condition
            if target_phonems[-1] == next_target_phonem:
                combos.append((new_chosen, new_associated, new_scores))
            else:
                for chosen, associated, rate in get_best_combos(
                    new_chosen, next_target_phonem, nodes, new_associated
                ):
                    combos.append((chosen, associated, rate + new_scores))

        return combos

    combos = None
    if len(target_phonems) == 1:
        combos = [
            (
                [a_p],
                [target_phonems[0].word],
                [step_1_and_step_2_rating(target_phonems[0], a_p)],
            )
            for a_p in get_candidates(target_phonems[0])[:n]
        ]
    else:
        combos = get_best_combos([], target_phonems[0], params.NODES, [])
        combos = sorted(combos, key=lambda c: sum(c[2]), reverse=True)
    return combos
