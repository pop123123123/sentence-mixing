import numpy as np
from scipy.io import wavfile


def concat_wav(path, phonems):
    # TODO resample to the highest rate
    rate = phonems[0].get_wave()[0]
    segments = [phonem.get_wave()[1] for phonem in phonems]
    new_clip = np.concatenate(segments)

    wavfile.write(path, rate, new_clip)
