import tempfile
from pathlib import Path

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

sentences = []
video_urls = []
NB_COMBOS = 5
FACTOR = 20


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


def rate_parameters(x):
    videos = main.get_videos(video_urls)
    data_folder = Path(tempfile.mkdtemp())
    change_parameters(x)
    r = sr.Recognizer()
    rates = []
    for s in sentences:
        # TODO seed ?
        combos = main.main(s, videos)
        for i, c in enumerate(combos[:5]):
            s += 1
            file_path = data_folder / f"{i}.wav"
            video_creator.audio.concat_wav(file_path, c.get_audio_phonems())
            with sr.AudioFile(file_path) as source:
                audio = r.record(source)
            recognized_sentence = r.recognize_sphinx(audio, language="fr-FR")
            rates.append(sentence_distance(s, recognized_sentence))
    return sum(rates) / len(rates)


def hamming(a, b):
    raise NotImplementedError()


def sentence_distance(original, recognized):
    original_phonems = []
    recognized_phonems = []

    d = hamming(original_phonems, recognized_phonems)

    return d
