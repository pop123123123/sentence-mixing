import argparse
import os
import random
from sys import argv

import textgrid
import youtube_dl

import sentence_mixing.config as config
import sentence_mixing.logic.analyze as analyze
import sentence_mixing.logic.parameters as params
import sentence_mixing.logic.video_processing as video_processing
import sentence_mixing.model.target as target
from sentence_mixing.serialize import load, save


def prepare_sm_config_file(config_path):
    config.set_config_path(config_path)


def prepare_sm_config_dict(config_dict):
    config.set_config_dict(config_dict)


def get_videos(video_urls):
    if not config.is_ready():
        raise Exception(
            "Please, set config file before launching get_videos by calling prepare_sm_config_file or prepare_sm_config_dict"
        )

    (videos,) = load()
    if (
        type(videos) != list
        or len(videos) != len(video_urls)
        or any(map(lambda t: t[0].url != t[1], zip(videos, video_urls)))
    ):
        videos = video_processing.preprocess_and_align(video_urls)
        save(videos)
    return videos


# assuming french for now
def process_sm(
    sentence, videos, seed=params.DEFAULT_SEED, interrupt_callback=None
):
    if not config.is_ready():
        raise Exception(
            "Please, set config file before launching process_sm by calling prepare_sm"
        )

    random.seed(seed)

    # transcribe sentence to pseudo-phonetic string
    target_sentence = target.TargetSentence(sentence)

    combos = analyze.get_n_best_combos(
        target_sentence, videos, interrupt_callback=interrupt_callback
    )
    return combos
