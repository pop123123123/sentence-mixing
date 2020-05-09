import math

import logic.global_audio_data
import logic.parameters
import logic.utils as utils
from model.choice import Choice, Combo
from model.exceptions import PhonemError


def compute_children(target_phonem, nodes_left, choice):
    total = 0
    chosen = []

    association_candidates = logic.global_audio_data.get_candidates(
        target_phonem
    )

    modif = logic.parameters.START_MODIF
    # Rating
    for association in association_candidates:
        computed_rate = association.get_total_score()

        step_3_rate = []
        if choice is not None:
            step_3_rate = choice.compute_child_step_3_score(association)
        else:
            step_3_rate = [0, 0]
        computed_rate += sum(step_3_rate)
        # not enough nodes left
        computed_rate *= modif
        if not utils.has_at_least_one_node(nodes_left, total, computed_rate):
            # not trivial
            break

        modif /= logic.parameters.RATE_POWER
        total += computed_rate
        chosen.append((association, step_3_rate, computed_rate))

    if total == 0:
        raise PhonemError(target_phonem)

    return [
        Choice(
            choice,
            association,
            math.ceil(
                logic.utils.compute_nodes_left(
                    nodes_left, total, computed_rate,
                )
            ),
            *rate
        )
        for association, rate, computed_rate in chosen
    ]


def get_n_best_combos(sentence, videos, n=100):
    logic.global_audio_data.set_videos(videos)

    target_phonems = utils.get_phonems(sentence.words)

    roots = compute_children(target_phonems[0], logic.parameters.NODES, None)

    combos = []
    for combo in roots:
        combos.extend(combo.get_combos())
    combos.sort(key=lambda c: c.get_score(), reverse=True)

    return combos[:n]
