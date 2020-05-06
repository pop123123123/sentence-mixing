import argparse
import os

import logic.video_processing
import main
import video_creator.interface
from logic.display import combo_displayer
from serialize import load, save


def get_videos(video_urls):
    (videos,) = load("tester.pckl")
    if (
        type(videos) != list
        or len(videos) != len(video_urls)
        or any(map(lambda t: t[0].url != t[1], zip(videos, video_urls)))
    ):
        videos = preprocess_and_align(video_urls)
        save(videos, name="tester.pckl")
    return videos


def preprocess_and_align(video_urls):
    """
    Build all the model objects for several video urls by downloading videos and analysing the
    videos using Montreal aligner.

    Argument:
    video_urls - list containing youtube videos url

    Returns a list containing all the video objects
    """

    # Creates basic Video objects
    videos = logic.video_processing._create_videos(video_urls)

    # Enriches Video objects with SubtitleLine objects
    logic.video_processing._create_subs(videos)

    # Enriches Video objects with AudioWords and AudioPhonem objects
    for video in videos:
        for i, subtitle in enumerate(video.subtitles):
            textgrid_path = os.path.join(
                out_dir, video.get_hashed_basename() + str(i) + ".TextGrid"
            )
            logic.video_processing._parse_align_result(textgrid_path, subtitle)

    return videos


out_dir = None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", "--seed", default=main.DEFAULT_SEED, help=main.SEED_HELP,
    )
    parser.add_argument(
        "out_dir", action="store", help="textgrids directory",
    )
    parser.add_argument(
        "sentence",
        metavar="TARGET_SENTENCE",
        action="store",
        help=main.TARGET_SENTENCE_HELP,
    )
    parser.add_argument(
        "video_urls",
        metavar="VIDEO_URL",
        nargs="+",
        action="store",
        help=main.VIDEO_URL_HELP,
    )

    args = parser.parse_args()
    out_dir = args.out_dir

    videos = get_videos(args.video_urls)
    combos = main.main(args.sentence, videos, args.seed)
    for c in reversed(combos):
        print("total score:", sum(c[2]))
        print(combo_displayer(c))
    video_creator.audio.concat_wav(
        video_creator.interface.AUDIO_FILE_PATH, combos[0][0]
    )
