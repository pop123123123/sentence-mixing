import sys

import numpy as np
import scipy.optimize

import parameter_tuning.parameter_tweaking
import parameter_tuning.speech_to_text_dict as stt_dict


def optimize(max_iter):
    initial = parameter_tuning.parameter_tweaking.get_parameters()
    scipy.optimize.minimize(
        parameter_tuning.parameter_tweaking.rate_parameters,
        initial,
        bounds=[(0, 1)] * 12,
        options={"maxiter": max_iter, "eps": 1e-3, "disp": True},
        callback=lambda x: print(x),
    )


if __name__ == "__main__":
    stt_dict.generate_compatible_dictionary()
    optimize(int(sys.argv[1]))
