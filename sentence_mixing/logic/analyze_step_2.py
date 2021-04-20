import sentence_mixing.logic.parameters as params

def rating_sequence_by_phonem_length(x, randomizer):
    return randomizer.noise_score(params.RATING_LENGTH_SAME_PHONEM) * x


def rating_word_by_phonem_length(x, randomizer):
    return randomizer.noise_score(params.RATING_LENGTH_SAME_WORD) * x
