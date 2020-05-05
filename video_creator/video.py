import os

from moviepy.editor import VideoFileClip, concatenate_videoclips


def create_video_file(total_phonems, paths):
    clips = [phonem.get_video_clip() for phonem in total_phonems]
    concatenate_videoclips(clips).write_videofile("out.mp4")
