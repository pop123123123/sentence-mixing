import os

from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips


def create_video_file(total_phonems, path, logger="bar"):
    clips = [phonem.get_video_clip() for phonem in total_phonems]
    concatenate_videoclips(clips).write_videofile(path, logger=logger)
