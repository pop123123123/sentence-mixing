import os
import shutil
from sys import argv

import textgrid
import youtube_dl

import config
import logic.video_processing as video_processing
import model.target as target
from phonem_finding import get_best_phonem_combos
from serialize import load, save


# assuming french for now
def main(sentence, video_urls, skip=False):
    # transcribe sentence to pseudo-phonetic string
    target_sentence = target.TargetSentence(sentence)

    videos = video_processing.preprocess_and_align(video_urls)

    return target_sentence, videos


if __name__ == "__main__":
    # format: exe sentence url1 url2 ...
    if len(argv) >= 3:
        if argv[1] == "skip":
            print(main(argv[2], argv[3:], skip=True))
        else:
            print(main(argv[1], argv[2:]))
