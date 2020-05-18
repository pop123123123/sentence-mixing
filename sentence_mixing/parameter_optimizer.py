import sys

import numpy as np
import scipy.optimize

import sentence_mixing.parameter_tuning.parameter_tweaking
import sentence_mixing.parameter_tuning.speech_to_text_dict as stt_dict
import sentence_mixing.sentence_mixer as sm


def optimize(max_iter, config_path):
    sm.prepare_sm(config_path)
    stt_dict.generate_compatible_dictionary()

    initial = (
        sentence_mixing.parameter_tuning.parameter_tweaking.get_parameters()
    )
    scipy.optimize.minimize(
        sentence_mixing.parameter_tuning.parameter_tweaking.rate_parameters,
        initial,
        bounds=[(0, 1)] * 12,
        options={"maxiter": max_iter, "eps": 1e-3, "disp": True},
        callback=lambda x: print(x),
    )
