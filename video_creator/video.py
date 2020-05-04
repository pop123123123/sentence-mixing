import os

from moviepy.editor import VideoFileClip, concatenate_videoclips


def create_video_file(total_phonems, paths):
    # TODO: enlever cette atrocité
    videos = {}
    for phonem in total_phonems:
        if not phonem.word.sentence.video._get_audio_path() in videos:
            vid_path = next(
                p
                for p in paths
                if os.path.basename(
                    phonem.word.sentence.video._get_audio_path()
                ).split(".")[0]
                == os.path.basename(p).split(".")[0]
            )
            clip = VideoFileClip(vid_path)

            videos[phonem.word.sentence.video._get_audio_path()] = clip

    clips = []
    for phonem in total_phonems:
        clip = videos[phonem.word.sentence.video._get_audio_path()]
        clips.append(clip.subclip(phonem.start, phonem.end))
    concatenate_videoclips(clips).write_videofile("out.mp4")
