import argparse
import os
import random
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

DEFAULT_SEED = 0


# assuming french for now
def main(sentence, video_urls, seed=DEFAULT_SEED):
    random.seed(seed)

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


DESCRIPTION = "CLI Interface to build a sentence from a video"

SEED_HELP = f"change the seed used in phonem association's score attribution (default: {DEFAULT_SEED})"
TARGET_SENTENCE_HELP = "a sentence you want to hear from the video"
VIDEO_URL_HELP = "a YouTube url of the wanted video"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "-s", "--seed", default=DEFAULT_SEED, help=SEED_HELP,
    )
    parser.add_argument(
        "sentence",
        metavar="TARGET_SENTENCE",
        action="store",
        help=TARGET_SENTENCE_HELP,
    )
    parser.add_argument(
        "video_urls",
        metavar="VIDEO_URL",
        nargs="+",
        action="store",
        help=VIDEO_URL_HELP,
    )

    args = parser.parse_args()

    print(main(args.sentence, args.video_urls, args.seed))
