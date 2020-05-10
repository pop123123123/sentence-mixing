"""This module contains all the parameters used to compute the combos"""

# Step 1

MINIMAL_PHONEM_LENGTH = 0.1
MAXIMAL_MINIMAL_PHONEM_LENGH_MALUS = 1000

MAXIMAL_CONSONANT_LENGTH = 0.25
MAXIMAL_MAXIMAL_CONSONANT_LENGTH_MALUS = 1000

MAXIMAL_VOWEL_LENGTH = 0.5
MAXIMAL_MAXIMAL_VOWEL_LENGTH_MALUS = 1000

# Step 2

RATING_LENGTH_SAME_PHONEM = 80
RATING_LENGTH_SAME_WORD = 100
SCORE_SAME_TRANSCRIPTION = 200
SCORE_SILENCE_AMPLITUDE = 200
SCORE_DURATION = 400

# Step 3

RATING_SPECTRAL_SIMILARITY = 50

# Other

NODES = 1 << 12
ALPHA = 1
SCORE_THRESHOLD = 50
RIGHT_PRIVILEGE = 0.8

SCORE_SAME_AUDIO_WORD = 200
RANDOM_SPAN = 50

START_MODIF = 1.0
RATE_POWER = 1.1
