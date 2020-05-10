import logic.parameters as params
import logic.randomizer as rnd


def rating_sequence_by_phonem_length(x):
    return rnd.noise_score(params.RATING_LENGTH_SAME_PHONEM) * x


def rating_word_by_phonem_length(x):
    return rnd.noise_score(params.RATING_LENGTH_SAME_WORD) * x
