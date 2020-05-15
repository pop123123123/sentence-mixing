import numpy as np
from scipy.io import wavfile


def concat_segments(phonems):
    # TODO resample to the highest rate
    segments = [phonem.get_wave()[1] for phonem in phonems]
    return phonems[0].get_wave()[0], np.concatenate(segments)


def concat_wav(path, phonems):
    rate, new_clip = concat_segments(phonems)

    wavfile.write(path, rate, new_clip)
