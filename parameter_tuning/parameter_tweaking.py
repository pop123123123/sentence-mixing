import concurrent.futures
import tempfile
from pathlib import Path

import Levenshtein
import numpy as np
import speech_recognition as sr

import logic.parameters as params
import main
import video_creator.audio

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
video_urls = [
    "https://www.youtube.com/watch?v=2tEBQhwCvY4",
    "https://www.youtube.com/watch?v=bW7KR_ApuXQ",
    "https://www.youtube.com/watch?v=MEV6BHQaTnw",
]
NB_COMBOS = 5
FACTOR = 1000


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
    combos = main.main(s, videos)
    print(f'rating "{s}"')
    r = sr.Recognizer()
    rates = []

    for c in combos[:NB_COMBOS]:
        rate, wave = video_creator.audio.concat_segments(c.get_audio_phonems())
        wave = (
            np.sum(wave, axis=1).reshape((-1,)).astype("int16").copy(order="C")
        )
        audio = sr.AudioData(wave, rate, 2)
        recognized_sentence = r.recognize_sphinx(audio, language="fr-FR")
        rates.append(sentence_distance(s, recognized_sentence))

    print(f"returning from {s}")
    return rates


def rate_parameters(x):
    videos = main.get_videos(video_urls)
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
    original_phonems = []
    recognized_phonems = []

    d = levenshtein_distance(original_phonems, recognized_phonems)

    return d
