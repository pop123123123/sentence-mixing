import os
import shutil
from sys import argv

import textgrid
import youtube_dl

import config
import logic.analyze
import logic.video_processing as video_processing
import model.target as target
from phonem_finding import get_best_phonem_combos
from serialize import load, save


# assuming french for now
def main(sentence, video_urls):
    # transcribe sentence to pseudo-phonetic string
    target_sentence = target.TargetSentence(sentence)

    (videos,) = load()
    if (
        type(videos) != list
        or len(videos) != len(video_urls)
        or any(map(lambda t: t[0].url != t[1], zip(videos, video_urls)))
    ):
        videos = video_processing.preprocess_and_align(video_urls)
        save(videos)

    combos = logic.analyze.get_n_best_combos(target_sentence, videos)
    return combos


if __name__ == "__main__":
    # format: exe sentence url1 url2 ...
    if len(argv) >= 3:
        print(main(argv[1], argv[2:]))
