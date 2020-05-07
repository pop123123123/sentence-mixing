import logic.utils as utils
from logic.global_audio_data import get_candidates
from model.choice import Choice, Combo


def get_best_first_associations(target_phonem):
    associations = get_candidates(target_phonem)
    raise NotImplementedError()
    return associations


def get_n_best_combos(sentence, videos, n=100):

    target_phonems = utils.get_phonems(sentence.words)

    best_assos = get_best_first_associations(target_phonems[0])
    roots = [Choice(None, asso, 0, 0) for asso in best_assos]

    combos = [root.get_combos() for root in roots]

    return combos
