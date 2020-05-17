from itertools import groupby

from sentence_mixing.model.abstract import Phonem

BORDERS = {
    (True, True, True, True): "┼",
    (True, True, True, False): "├",
    (True, True, False, True): "┴",
    (True, True, False, False): "└",
    (True, False, True, True): "┤",
    (True, False, True, False): "│",
    (True, False, False, True): "┘",
    (True, False, False, False): "╵",
    (False, True, True, True): "┬",
    (False, True, True, False): "┌",
    (False, True, False, True): "─",
    (False, True, False, False): "╶",
    (False, False, True, True): "┐",
    (False, False, True, False): "╷",
    (False, False, False, True): "╴",
    (False, False, False, False): " ",
}

RATING_STEP = [1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 0]
RATINGS = [
    ("step_1_random", "Random"),
    ("step_1_duration", "Duration"),
    ("step_2_audio_score", "Wave ampl"),
    ("step_2_same_word", "Homophone"),
    ("step_2_word_sequence", "Word seq"),
    ("step_2_phonem_sequence_backward", "Word seq back"),
    ("step_2_phonem_sequence", "Ph sequence"),
    ("step_2_same_phonem", "Transcri"),
    ("step_3_audio_spectral", "Wave freq"),
    ("step_3_audio_amplitude", "Wave amplitude"),
    ("step_3_same_word_previous_phonems", "Previous"),
    ("total", "Total"),
]


def center_in_string(s, n, fill=" "):
    assert len(s) <= n
    left = True
    while len(s) < n:
        if left:
            s = fill + s
        else:
            s += fill
        left = not left
    return s


def combo_displayer(combo):
    phonems = [ch.association.audio_phonem for ch in combo.get_choices()]
    phonems = list(
        zip(
            phonems,
            [
                (
                    ch.association.target_phonem.word,
                    [ch.get_split_score()[k] for k, _ in RATINGS[:-1]],
                )
                for ch in combo.get_choices()
            ],
        )
    )
    phonems_transcriptions = [p.transcription for p, _ in phonems]
    phonems_scores = [score for _, (_, score) in phonems]

    segments_s = [f"{round(p.start, 2)}-{round(p.end, 2)}" for p, _ in phonems]

    COL = BORDERS[(True, False, True, False)]
    LINE = BORDERS[(False, True, False, True)]
    CROSS = BORDERS[tuple(4 * [True])]

    legend_size = max(map(lambda x: len(x[1]), RATINGS[:-1])) + 2
    padding = " " * (legend_size + 1)

    strings = []
    strings.append(COL.join(segments_s))
    strings.append(CROSS.join([len(seg) * LINE for seg in segments_s]))

    for i, _ in enumerate(RATINGS[:-1]):
        strings.append(
            COL.join(
                [
                    center_in_string(str(round(score[i], 2)), len(s))
                    for s, score in zip(segments_s, phonems_scores)
                ]
            )
        )
    strings.append(
        COL.join(
            [
                center_in_string(str(round(sum(score), 2)), len(s))
                for s, score in zip(segments_s, phonems_scores)
            ]
        )
    )
    strings.append(
        COL.join(
            [
                center_in_string(p, len(s))
                for s, p in zip(segments_s, phonems_transcriptions)
            ]
        )
    )
    strings.append(
        strings[1].replace(CROSS, BORDERS[(False, True, True, True)])
    )

    len_by_ws = [
        (w, sum(len(s) + 1 for s, _ in g) - 1)
        for w, g in groupby(zip(segments_s, phonems), key=lambda x: x[1][1][0])
    ]
    strings.append(
        COL.join([center_in_string(w.token, l) for w, l in len_by_ws])
    )
    strings.append("".join([CROSS if c == COL else LINE for c in strings[-1]]))
    strings.append(
        COL.join([center_in_string(w.original_word, l) for w, l in len_by_ws])
    )
    strings.append(
        strings[-2].replace(CROSS, BORDERS[(False, True, True, True)])
    )
    strings.insert(
        0,
        strings[-1].replace(
            BORDERS[(False, True, True, True)],
            BORDERS[(True, True, False, True)],
        ),
    )

    length = 5 + len(RATING_STEP)

    strings.reverse()
    strings = [
        (
            str(RATING_STEP[length - i])
            + RATINGS[length - i][1].rjust(legend_size)
            if 5 < i <= length
            else padding
        )
        + BORDERS[(i != 0, s[0] == LINE, i + 1 != len(strings), False)]
        + s
        + BORDERS[(i != 0, False, i + 1 != len(strings), s[0] == LINE)]
        for i, s in enumerate(strings)
    ]
    return "\n".join(strings)
