import random


def noise_score(base_score, sigma=None):
    if not sigma:
        sigma = base_score * 0.2

    return random.gauss(base_score, sigma)
