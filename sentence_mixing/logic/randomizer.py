import random

import sentence_mixing.logic.parameters as params


def noise_score(base_score, sigma=None):
    """
    Adds a gaussian noise on a given score

    Arguments:
    base_score - mean of gaussian score
    sigma - variance of gaussian score. Default is 1/5 of base_score
    """

    if not sigma:
        sigma = base_score * 0.2

    return random.gauss(base_score, sigma)


def random_basic_score():
    """Returns a random basic score following an gaussian distribution"""

    return random.gauss(0, params.RANDOM_SPAN)
