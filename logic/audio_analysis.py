import numpy as np
from scipy import signal

import logic.parameters


def cross_power_spectral_density_sum(x, y, fs):
    _, Pxy = signal.csd(x[:, 0], y[:, 0], fs, nperseg=1024)
    return np.log(np.abs(Pxy).sum())


def resample(x, current_rate, new_rate):
    return signal.resample(x, int(new_rate * x.shape[0] / current_rate))


def resample_highest_rate(data):
    rate = max(data, key=lambda x: x[0])[0]
    data = [(rate, resample(x, r, rate)) for r, x in data]
    return data


def rate_silence(data):
    """
    Compute a silence indicator between 0 (silent) and 1 (saturated).
    """
    rate, data = data
    average_amplitude = (
        1 - (np.average(np.sqrt(np.average((data / (1 << 15)) ** 2, axis=0))))
    ) ** 2
    return average_amplitude


def _soft_rectangle_function(x, a, b, alpha):
    return (np.tanh(alpha * (x - a)) - np.tanh(alpha * (x - b))) / 2


def rate_duration(audio_seg, inf, sup):
    return (
        _soft_rectangle_function(
            audio_seg.get_length(), inf, sup, logic.parameters.ALPHA
        )
        * 2
        - 1
    )
