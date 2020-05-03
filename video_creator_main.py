#!/usr/bin/env python3

import argparse
import concurrent.futures

from video_creator.download import dl_video
from video_creator.interface import loop_interface
from video_creator.video import create_video_file


def main(audio_command, skip_first, urls):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = executor.map(dl_video, urls)

        total_timestamps, total_text = loop_interface(
            audio_command, skip_first, urls
        )

        paths = list(futures)

    create_video_file(total_timestamps, paths)

    return total_text


DEFAULT_AUDIO_COMMAND = 'tycat "{}"'

DESCRIPTION = "CLI Interface to create sentence mixing videos."

AUDIO_COMMAND_HELP = f"a command to launch a playback of an audio file passed as a format parameter (default: {DEFAULT_AUDIO_COMMAND})"
VIDEO_URL_HELP = "a YouTube url of the wanted video"
SKIP_ANALYSIS_HELP = "tell the generator to skip the analysis (default: false)"

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "-c",
        "--audio-command",
        default=DEFAULT_AUDIO_COMMAND,
        help=AUDIO_COMMAND_HELP,
    )
    parser.add_argument(
        "video_urls",
        metavar="VIDEO_URL",
        nargs="+",
        action="store",
        help=VIDEO_URL_HELP,
    )
    parser.add_argument(
        "-s",
        "--skip",
        dest="skip_first_analysis",
        action="store_true",
        default=False,
        help=SKIP_ANALYSIS_HELP,
    )

    args = parser.parse_args()

    print(main(args.audio_command, args.skip_first_analysis, args.video_urls))
