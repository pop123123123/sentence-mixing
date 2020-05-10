import math

import logic.global_audio_data
import logic.parameters
import logic.utils as utils
from model.choice import Choice, Combo
from model.exceptions import PhonemError


def compute_children(target_phonem, nodes_left, choice):
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

    Returns:
    a list of children Choice corresponding to the selected associations

    Raises:
    PhonemError - the best scored association has a score of 0. The phonem was not found in audio
    """

    total = 0
    chosen = []

    # Get all associations, sorted by decreasing scores
    association_candidates = logic.global_audio_data.get_candidates(
        target_phonem
    )

    # This modif will be used to attenuate score
    modif = logic.parameters.START_MODIF

    # Rating
    for association in association_candidates:
        computed_rate = association.get_total_score()

        step_3_rate = []
        if choice is not None:
            step_3_rate = choice.compute_child_step_3_score(association)
        else:
            # For root nodes, we have no step 3 score
            step_3_rate = [0, 0]
        computed_rate += sum(step_3_rate)
        computed_rate *= modif

        # Not enough nodes left
        if not utils.has_at_least_one_node(nodes_left, total, computed_rate):
            # not trivial
            break

        # After each association pick, highly decreasesa score modifier
        modif /= logic.parameters.RATE_POWER
        total += computed_rate
        chosen.append((association, step_3_rate, computed_rate))

    # Total score is null: we assume that the desired phonem was not found in the audio subtitles
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

    logic.global_audio_data.set_videos(videos)

    target_phonems = utils.get_phonems(sentence.words)

    roots = compute_children(target_phonems[0], logic.parameters.NODES, None)

    combos = []
    for combo in roots:
        combos.extend(combo.get_combos())
    combos.sort(key=lambda c: c.get_score(), reverse=True)

    return combos[:n]
