import random

import logic.parameters as params


def noise_score(base_score, sigma=None):
    if not sigma:
        sigma = base_score * 0.2

    return random.gauss(base_score, sigma)


def random_basic_score():
    return random.uniform(0, params.MAX_DEFAULT_RATE)
