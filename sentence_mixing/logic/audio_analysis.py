import functools

import numpy as np
from scipy import signal

import sentence_mixing.logic.parameters as params


def cross_power_spectral_density_sum(x, y, fs):
    _, Pxy = signal.csd(x[:, 0], y[:, 0], fs, nperseg=1024)
    return np.log(np.abs(Pxy).sum())


def resample(x, current_rate, new_rate):
    return signal.resample(x, int(new_rate * x.shape[0] / current_rate))


def resample_highest_rate(data):
    rate = max(data, key=lambda x: x[0])[0]
    data = [(rate, resample(x, r, rate)) for r, x in data]
    return data


@functools.lru_cache(maxsize=None)
def get_normalized_rms(audio_phonem):
    rate, data = audio_phonem.get_wave()
    return np.average(
        np.sqrt(np.average((data / (1 << 15)) ** 2, axis=-2)), axis=-1
    )


def rate_silence(audio_phonem):
    """
    Compute a silence indicator between 0 (silent) and 1 (saturated).
    """
    average_amplitude = (
        1 - get_normalized_rms(audio_phonem)
    ) ** params.SILENCE_POWER
    return average_amplitude


def rate_amplitude_similarity(previous_audio_segs, audio_seg):
    amplitudes = np.array([get_normalized_rms(w) for w in previous_audio_segs])
    powers = np.arange(
        1, 1 + min(params.AMPLITUDE_STEPS_BACK, len(previous_audio_segs)),
    )
    current_amplitude = get_normalized_rms(audio_seg)
    return float(np.sum(np.abs(amplitudes - current_amplitude) ** powers))


def _soft_rectangle_function(x, a, b, alpha):
    return (np.tanh(alpha * (x - a)) - np.tanh(alpha * (x - b))) / 2


def rate_duration(audio_seg, inf, sup):
    return (
        _soft_rectangle_function(
            audio_seg.get_length(), inf, sup, params.ALPHA
        )
        * 2
        - 1
    )
