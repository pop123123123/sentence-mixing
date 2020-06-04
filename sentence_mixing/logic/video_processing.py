import base64
import os
import shutil
import tempfile
from itertools import groupby
from pathlib import Path

import textgrid
import youtube_dl
from scipy.io import wavfile

import sentence_mixing.config as config
import sentence_mixing.logic.text_parser as tp
import sentence_mixing.model.audio as audio
from sentence_mixing.model.video import Video


def _create_videos(video_urls):
    """Builds basic video objects by downloading videos"""

    paths = _dl_videos(video_urls)

    # TODO: modifier le "" pour mettre l'extension de la vidéo
    return [
        Video(url, base_path, subtitles_extension)
        for url, (base_path, subtitles_extension) in zip(video_urls, paths)
    ]


class Logger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def _dl_videos(urls):
    """
    Downloads audio and subs for videos at the given urls

    Arguments:
    - urls: iterable of youtube urls of the wanted videos

    Returns:
    A list of tuples (path, subtitle_file_extension) matching the given urls
    """

    paths = []
    for url in urls:
        ydl_opts = {
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["fr"],
            "outtmpl": ".downloads/%(id)s.%(title)s.%(ext)s",
            "format": "bestaudio/best",
            "logger": Logger(),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "192",
                }
            ],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            filename = ydl.prepare_filename(ydl.extract_info(url))
            ydl.download([url])
            base_path = os.path.splitext(filename)[0]
            # TODO: rendre le .fr.vtt dynamique en fonction de la langue des sous-titres
            paths.append((base_path, ".fr.vtt"))
    return paths


def _create_subs(videos):
    """Adds a list of basic subtitle object for each given video by parsing subtitle file"""

    subtitle_files = [(video, video.get_subtitle_file()) for video in videos]

    for video, subtitle_file in subtitle_files:
        for caption in subtitle_file:
            video.add_subtitle(_parse_caption(video, caption))


def _parse_caption(video, caption):
    """Parses a webvtt caption to an AudioSubtitle object"""

    def _get_sec(time_str):
        h, m, s = time_str.split(":")
        return float(h) * 3600 + float(m) * 60 + float(s)

    # TODO: revoir le \n
    text = tp.transform_numbers(caption.text.split("\n")[-1])
    start = _get_sec(caption.start)
    end = _get_sec(caption.end)

    return audio.SubtitleLine(text, start, end, video)


def _split_audio_in_files(video):
    """
    Saves each SubtitleLine in a separate audio file and text file in order to be processed by
    Montreal aligner
    """

    folder_name = config.get_property("folder")
    shutil.rmtree(folder_name, True)
    Path(folder_name).mkdir(parents=True, exist_ok=True)

    video_hashed_name = video.get_hashed_basename()

    rate, data = video.get_audio_wave()

    for i, sub in enumerate(video.subtitles):
        sub_base_name = os.path.join(folder_name, video_hashed_name + str(i))

        start_frame = int(sub.start * rate)
        end_frame = int(sub.end * rate)

        sub_audio_data = data[start_frame:end_frame]
        wavfile.write(sub_base_name + ".wav", rate, sub_audio_data)

        with open(sub_base_name + ".lab", "w") as subfile:
            subfile.write(sub.original_text)


def _align_phonems():
    """
    Launches the aligner

    Returns the temporary directory containing the analysis results
    """

    folder = config.get_property("folder")
    speakers = 1

    align_exe = config.get_property("align_exe")
    dict_path = config.get_property("dict_path")
    trained_model = config.get_property("trained_model")
    out_dir = tempfile.mkdtemp()
    temp_dir = tempfile.mkdtemp()

    command = f'{align_exe} "{folder}" "{dict_path}" "{trained_model}" "{out_dir}" -t "{temp_dir}" -s {str(speakers)} -q'

    ret = os.system(command)
    assert ret == 0

    return out_dir


def _parse_align_result(textgrid_path, subtitle):
    """
    Retrieves and parses the result of the aligner and enriches given subtitle objet by creating
    associated AudioWords and AudioPhonem
    """

    if not os.path.exists(textgrid_path):
        return 0
    t = textgrid.TextGrid.fromFile(textgrid_path)

    words = t[0]

    phonems = t[1]
    i_phonems = 0

    for word in words:
        original_word = word.mark
        start = word.bounds()[0] + subtitle.start
        end = word.bounds()[1] + subtitle.start
        token = tp.from_word_to_token(word.mark)

        audio_word = audio.AudioWord(
            subtitle, token, original_word, start, end
        )
        subtitle.add_word(audio_word)

        while (
            i_phonems < len(phonems)
            and phonems[i_phonems].bounds()[0] < word.bounds()[1]
        ):
            # If the phonem is included in the word
            if phonems[i_phonems].bounds()[0] >= word.bounds()[0]:
                transcription = phonems[i_phonems].mark
                start_phon = phonems[i_phonems].bounds()[0] + subtitle.start
                end_phon = phonems[i_phonems].bounds()[1] + subtitle.start

                # Only creates phonem if it is exploitable
                # Excludes phonems whose transcription like 'sil', 'spn', ''
                if transcription in tp.get_all_phonems():
                    audio_word.add_phonem(
                        audio.AudioPhonem(
                            audio_word, transcription, start_phon, end_phon
                        )
                    )
            i_phonems += 1


def preprocess_and_align(video_urls):
    """
    Build all the model objects for several video urls by downloading videos and analysing the
    videos using Montreal aligner.

    Argument:
    video_urls - list containing youtube videos url

    Returns a list containing all the video objects
    """

    # Creates basic Video objects
    videos = _create_videos(video_urls)
    # TODO maybe get all the data analyzed at once (waav resampling needed)

    # Prepares the aligner
    for video in videos:
        # Enriches Video objects with SubtitleLine objects
        _create_subs([video])

        _split_audio_in_files(video)
        # Launches the aligner
        out_dir = _align_phonems()

        # Enriches Video objects with AudioWords and AudioPhonem objects
        for i, subtitle in enumerate(video.subtitles):
            textgrid_path = os.path.join(
                out_dir, video.get_hashed_basename() + str(i) + ".TextGrid"
            )
            _parse_align_result(textgrid_path, subtitle)

    return videos
