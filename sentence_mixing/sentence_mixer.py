import argparse
import os
import random
from sys import argv

import textgrid

import sentence_mixing.config as config
import sentence_mixing.logic.analyze as analyze
import sentence_mixing.logic.parameters as params
import sentence_mixing.logic.randomizer
import sentence_mixing.logic.video_processing as video_processing
import sentence_mixing.model.target as target
from sentence_mixing.logic.global_audio_data import audioDataFactory
from sentence_mixing.serialize import load, save


def prepare_sm_config_file(config_path):
    """Sets the global config dict with the json dict contained in config_path"""
    config.set_config_path(config_path)


def prepare_sm_config_dict(config_dict):
    """Set the global config dict with the dict config_dict"""
    config.set_config_dict(config_dict)


SEED = None
# Random snapshot
# Initialized during get_videos(), then used as reference by process_sm()
GET_VIDEO_RANDOM = {}


def get_global_randomizer(video_urls):
    hash_ = sum(hash(v) for v in video_urls)
    if hash_ not in GET_VIDEO_RANDOM:
        GET_VIDEO_RANDOM[hash_] = random.Random(SEED)
    return GET_VIDEO_RANDOM[hash_]


def get_global_randomizer_from_videos(videos):
    video_urls = [v.url for v in videos]
    return get_global_randomizer(video_urls)


def get_videos(video_urls, seed):
    """
    Builds full SM model from youtube video links.
    The associated youtube videos must have subtitles. Automatic subtitles
    works as well.

    Arguments:
    video_urls -- List[string]: youtube links of the input videos
    seed -- int: initialization seed for random number generation
    WARNING! THE SEED MUST BE THE SAME FOR ALL SUBEXECUTIONS

    Returns:
    A list of Video objects containing the full SM model.
    """

    # Initializing random generation snapshot
    global SEED
    SEED = seed
    rand = sentence_mixing.logic.randomizer.Randomizer(
        get_global_randomizer(video_urls)
    )

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
        videos = video_processing.preprocess_and_align(video_urls, rand)
        save(videos)
    # IMPORTANT: Used to advance the randomizer to next state before the
    # calls to process_sm
    audioDataFactory(videos).get_transcription_dict_audio_phonem()
    return videos


# assuming french for now
def process_sm(sentence, videos, interrupt_callback=None):
    """
    Reorders the phonems contained in videos model to sound like sentence

    Arguments:
    sentence -- string: the target sentence we want to build from the source
                videos
    videos -- List[model.Video]: contains all the SM model objects from the
              source videos

    Returns:
    A list of combos. A combo is a complete list of choices associating each
    phonem from the target sentence with a real phonem present in a video.
    The combos are stored by relevance. The first combo of the list is the most
    found relevant combination of phonems.
    """

    if not config.is_ready():
        raise Exception(
            "Please, set config file before launching process_sm by calling prepare_sm"
        )

    # This object is used to start random generation from GET_VIDEO_RANDOM
    # snapshot
    randomizer = sentence_mixing.logic.randomizer.Randomizer(
        get_global_randomizer_from_videos(videos)
    )

    # transcribe sentence to pseudo-phonetic string
    target_sentence = target.TargetSentence(sentence)

    combos = analyze.get_n_best_combos(
        target_sentence,
        videos,
        randomizer,
        interrupt_callback=interrupt_callback,
    )
    return combos
