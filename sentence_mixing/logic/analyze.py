import math

import sentence_mixing.logic.global_audio_data as global_audio_data
import sentence_mixing.logic.parameters as params
import sentence_mixing.logic.utils as utils
from sentence_mixing.model.choice import Choice, Combo
from sentence_mixing.model.exceptions import Interruption, PhonemError

audio_data = None


def compute_children(target_phonem, nodes_left, choice, randomizer):
    """
    This function choses several audio_phonems for a given target_phonem.
    Sequentially choses an association, then decreasing a score modifier.
    Once the score of the next association is too low, stops the function and returns the children.

    Argument:
    target_phonem - target phonem for which we try to find a convenient audio_phonem
    nodes_left - number of remaining nodes
                 When this number of resources is too low, stop exploring the children
    choice - choice that called this function
             None when selecting the root choices

    randomizer - object used to guarantee determinism

    Returns:
    a list of children Choice corresponding to the selected associations

    Raises:
    PhonemError - the best scored association has a score of 0. The phonem was not found in audio
    """

    steps_left = target_phonem.word.sentence.get_phonem_size() - target_phonem.word.sentence.get_phonem_index(
        target_phonem
    )
    total = 0
    chosen = []

    # Get all associations, sorted by decreasing scores
    association_candidates = audio_data.get_candidates(
        target_phonem, randomizer
    )

    # This modif will be used to attenuate score
    modif = params.START_MODIF

    for group in utils.grouper(
        association_candidates, params.ANALYSE_CHUNK_SIZE
    ):
        candidates = None
        if choice is not None:
            candidates = sorted(
                [
                    (asso, choice.compute_child_step_3_score(asso))
                    for asso in group
                    if asso is not None
                ],
                key=lambda x: x[0].get_total_score() + sum(x[1]),
                reverse=True,
            )
        else:
            candidates = zip(
                filter(lambda x: x is not None, group),
                [[0, 0, 0]] * params.ANALYSE_CHUNK_SIZE,
            )

        # Rating
        for association, step_3_rate in candidates:
            computed_rate = association.get_total_score()

            computed_rate += sum(step_3_rate)
            computed_rate *= modif

            # Not enough nodes left
            if not utils.has_at_least_one_node(
                nodes_left, total + computed_rate, computed_rate, steps_left
            ):
                # not trivial
                break

            # After each association pick, highly decreasesa score modifier
            modif /= params.RATE_POWER
            total += computed_rate
            chosen.append((association, step_3_rate, computed_rate))
        else:
            # if didn't break, don't break
            continue
        break

    # Total score is null: we assume that the desired phonem was not found in the audio subtitles
    if total == 0:
        raise PhonemError(target_phonem)

    chosen, total = utils.recompute_scores(chosen, nodes_left, steps_left)

    return [
        Choice(
            choice,
            association,
            utils.compute_nodes_left(nodes_left, total, computed_rate,),
            *rate,
            randomizer,
        )
        for association, rate, computed_rate in chosen
    ]


def get_n_best_combos(
    sentence, videos, randomizer, n=100, interrupt_callback=None
):
    """
    Computes best n combos for a given sentence and set of videos

    All the algorithm bases on score values.

    Scores are assigned in three different steps:
    -Step 1: the audio phonems are scored individually
    -Step 2: the target phonem and audio phonem associations are score individually
    -Step 3: an association is scored comparatively to all previous chosen associations

    Steps 1 and 2 are computed exhaustively.
    However, step 3 cannot be computed exchaustively: the number of association combos is well
    to high.

    To counter this problem, we use a limited number of "nodes" Choices.
    """
    global audio_data

    audio_data = global_audio_data.audioDataFactory(videos)

    target_phonems = utils.get_phonems(sentence.words)

    roots = compute_children(target_phonems[0], params.NODES, None, randomizer)

    combos = []
    for combo in roots:
        if interrupt_callback is not None:
            if interrupt_callback():
                raise Interruption(interrupt_callback)

        combos.extend(combo.get_combos())

    combos.sort(key=lambda c: c.get_score(), reverse=True)

    return combos[:n]
