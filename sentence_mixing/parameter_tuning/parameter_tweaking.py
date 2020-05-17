import concurrent.futures
import functools
import os
import tempfile
from pathlib import Path

import Levenshtein
import numpy as np
import pocketsphinx as ps

import sentence_mixing.config as config
import sentence_mixing.logic.audio_analysis
import sentence_mixing.logic.parameters as params
import sentence_mixing.parameter_tuning.speech_to_text_dict as stt_dict
import sentence_mixing.sentence_mixer as sm
import sentence_mixing.video_creator.audio

# minimal_phonem_range = [0, 0.03, 0.1]
# maximal_consonant_length_range = [0.10, 0.25, 0.5]
# maximal_vowel_length_range = [0.10, 0.25, 0.5]
# silence_power_range = [1, 2, 4]
# start_modif_range = [0.8, 1.0, 1.2]
# rate_poer_range = [0.9, 1.1, 1.3]


# maximal_minimal_phonem_length_malus_range = [500, 1000, 2000]
# maximal_maximal_consonant_length_malus_range = [500, 1000, 2000]
# maximal_maximal_vowel_length_malus_range = [500, 1000, 2000]
# rating_length_same_phonem_range = [80, 150, 250]
# rating_length_same_word_range = [100, 170, 300]
# score_same_transcription_range = [0, 200, 400]
# score_silence_amplitude_range = [0, 200, 400]
# score_duration_rang = [0, 200, 400]
# rating_spectral_similarity_range = [0, 50, 150]
# rating_amplitude_difference_range = [-500, -250, 0]
# score_same_audio_word_range = [80, 200, 500]
# random_span_range = [0, 50, 100]

sentences = ["l'abeille ça pique", "le confinement me prend la tête"]
video_urls = ["https://www.youtube.com/watch?v=-rTBodCtBAM"]
NB_COMBOS = 5
FACTOR = 1000


@functools.lru_cache(maxsize=1)
def get_decoder():
    """Returns speech to text decoder, created with proper path to models, weights and dict"""

    config.get_property("stt_model_path")

    stt_config = ps.Decoder.default_config()
    stt_config.set_string(
        "-hmm",
        os.path.join(config.get_property("stt_model_path"), "acoustic-model"),
    )  # set the path of the hidden Markov model (HMM) parameter files
    stt_config.set_string(
        "-lm",
        os.path.join(
            config.get_property("stt_model_path"), "language-model.lm.bin"
        ),
    )
    stt_config.set_string("-dict", config.get_property("stt_tmp_dict_path"))
    stt_config.set_string(
        "-logfn", os.devnull
    )  # disable logging (logging causes unwanted output in terminal)
    decoder = ps.Decoder(stt_config)

    return decoder


def get_parameters():
    return (
        np.array(
            [
                params.MAXIMAL_MINIMAL_PHONEM_LENGH_MALUS,
                params.MAXIMAL_MAXIMAL_CONSONANT_LENGTH_MALUS,
                params.MAXIMAL_MAXIMAL_VOWEL_LENGTH_MALUS,
                params.RATING_LENGTH_SAME_PHONEM,
                params.RATING_LENGTH_SAME_WORD,
                params.SCORE_SAME_TRANSCRIPTION,
                params.SCORE_SILENCE_AMPLITUDE,
                params.SCORE_DURATION,
                params.RATING_SPECTRAL_SIMILARITY,
                params.RATING_AMPLITUDE_DIFFERENCE,
                params.SCORE_SAME_AUDIO_WORD,
                params.RANDOM_SPAN,
            ]
        )
        / FACTOR
    )


def change_parameters(x):
    x = x * FACTOR
    params.MAXIMAL_MINIMAL_PHONEM_LENGH_MALUS = x[0]
    params.MAXIMAL_MAXIMAL_CONSONANT_LENGTH_MALUS = x[1]
    params.MAXIMAL_MAXIMAL_VOWEL_LENGTH_MALUS = x[2]
    params.RATING_LENGTH_SAME_PHONEM = x[3]
    params.RATING_LENGTH_SAME_WORD = x[4]
    params.SCORE_SAME_TRANSCRIPTION = x[5]
    params.SCORE_SILENCE_AMPLITUDE = x[6]
    params.SCORE_DURATION = x[7]
    params.RATING_SPECTRAL_SIMILARITY = x[8]
    params.RATING_AMPLITUDE_DIFFERENCE = x[9]
    params.SCORE_SAME_AUDIO_WORD = x[10]
    params.RANDOM_SPAN = x[11]


def rate_sentence(videos, s):
    # TODO seed ?
    print(f'generating combos for "{s}"')
    combos = sm.process_sm(s, videos)
    print(f'rating "{s}"')
    rates = []

    for c in combos[:NB_COMBOS]:
        rate, wave = sentence_mixing.video_creator.audio.concat_segments(
            c.get_audio_phonems()
        )
        wave = (
            sentence_mixing.logic.audio_analysis.resample(
                np.sum(wave, axis=1).reshape((-1,)), rate, 16000
            )
            .astype("int16")
            .copy(order="C")
        )

        decoder = get_decoder()

        decoder.start_utt()  # begin utterance processing
        decoder.process_raw(
            wave, False, True
        )  # process audio data with recognition enabled (no_search = False), as a full utterance (full_utt = True)
        decoder.end_utt()  # stop utterance processing

        recognized_sentence = decoder.hyp().hypstr

        rates.append(sentence_distance(s, recognized_sentence))

    print(f"returning from {s}")
    return rates


def rate_parameters(x):
    videos = sm.get_videos(video_urls)
    change_parameters(x)

    rates = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures_rates = executor.map(
            rate_sentence, [videos] * NB_COMBOS, sentences
        )
        for r in futures_rates:
            rates.extend(r)
    res = sum(rates) / len(rates)
    print(x, res)
    return res


def translate(seq, dic):
    return "".join(dic[c] for c in seq)


def levenshtein_distance(a, b):
    phonems = set(a).union(b)
    dic = {p: chr(i) for i, p in enumerate(phonems)}

    return Levenshtein.distance(translate(a, dic), translate(b, dic))


def sentence_distance(original, recognized):
    # Asume that generate_compatible_dictionary() has been called
    original_phonems = stt_dict.sentence_to_phonem_list(original)
    recognized_phonems = stt_dict.sentence_to_phonem_list(recognized)

    d = levenshtein_distance(original_phonems, recognized_phonems)

    return d
