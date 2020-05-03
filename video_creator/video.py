import os

from moviepy.editor import VideoFileClip, concatenate_videoclips


def create_video_file(total_timestamps, paths):
    # TODO: enlever cette atrocité
    videos = {}
    for phonem in total_timestamps:
        if not phonem.get_audio_path() in videos:
            vid_path = next(
                p
                for p in paths
                if os.path.basename(phonem.get_audio_path()).split(".")[0]
                == os.path.basename(p).split(".")[0]
            )

            clip = VideoFileClip(vid_path)

            videos[phonem.get_audio_path()] = clip

    clips = []
    for seg in total_timestamps:
        clip = videos[seg.get_audio_path()]
        clips.append(
            clip.subclip(seg.get_start_timestamp(), seg.get_end_timestamp())
        )
    concatenate_videoclips(clips).write_videofile("out.mp4")
