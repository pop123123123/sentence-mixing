from itertools import groupby

from model.abstract import Phonem

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
    phonems = [
        [seg] if isinstance(seg, Phonem) else seg.phonems for seg in combo[0]
    ]
    phonems = [p for ps in phonems for p in ps]
    phonems = list(zip(phonems, zip(*combo[1:])))
    phonems_transcriptions = [p.transcription for p, _ in phonems]
    phonems_scores = [score for _, (_, score) in phonems]

    segments_s = [f"{round(p.start, 2)}-{round(p.end, 2)}" for p, _ in phonems]

    COL = BORDERS[(True, False, True, False)]
    LINE = BORDERS[(False, True, False, True)]
    CROSS = BORDERS[tuple(4 * [True])]

    strings = []
    strings.append(COL.join(segments_s))
    strings.append(CROSS.join([len(seg) * LINE for seg in segments_s]))

    strings.append(
        COL.join(
            [
                center_in_string(str(round(score, 2)), len(s))
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

    strings.reverse()
    strings = [
        BORDERS[(i != 0, s[0] == LINE, i + 1 != len(strings), False)]
        + s
        + BORDERS[(i != 0, False, i + 1 != len(strings), s[0] == LINE)]
        for i, s in enumerate(strings)
    ]
    return "\n".join(strings)
