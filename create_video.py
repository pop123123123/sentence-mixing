from main import main
import youtube_dl, os
from moviepy.editor import VideoFileClip, concatenate_videoclips
from serialize import load, save
from scipy.io import wavfile

def _concat_wav(segments):
  import numpy as np

  audio_files_dict = {}
  for phonem in segments:
    if not phonem.get_audio_path() in audio_files_dict:
      rate, data = wavfile.read(phonem.get_audio_path())

      if len(np.shape(data)) == 1 or data.shape[1] == 1:
        data = np.stack((data, data), axis=1)

      audio_files_dict[phonem.get_audio_path()] = (rate, data)


  new_clip = data[0:1]
  for segment in segments:
    rate, data = audio_files_dict[segment.get_audio_path()]

    start_frame = int(segment.get_start_timestamp()*rate)
    end_frame = int(segment.get_end_timestamp()*rate)

    new_clip = np.concatenate((new_clip, data[start_frame:end_frame]))

  wavfile.write("out.wav", rate, new_clip)


def dl_videos(urls):
  paths = []
  for url in urls:
    ydl_opts = {
      'outtmpl': 'downloads/%(title)s.%(ext)s',
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
      filename = ydl.prepare_filename(ydl.extract_info(url))
      if not os.path.exists(filename):
        ydl.download([url])
      paths.append(filename)
  return paths

def get_sentence(text):
  if text is not None:
    print('Previous sentences:\n', text)
  return input('Enter a sentence: ')

from sys import argv
if __name__ == "__main__":
  # format: exe command (skip) sentence url1 url2 ...
  if len(argv) >= 3:
    command = argv[1]
    argv = argv[1:]

    skip = argv[1] == 'skip'
    if skip:
      argv = argv[1:]

    total_timestamps = []
    total_text = ""
    sentence = get_sentence(None)
    links = argv[1:]

    timestamps_buffer = []
    while sentence != '':
      timestamps = []

      edit = False
      store = False
      valid = False
      load_audio_index = None
      while not valid:
        if edit:
          sentence = get_sentence(total_text)

        # Stores previous audio in buffer
        if store:
          timestamps_buffer.append(timestamps)
          store = False

        if load_audio_index is not None:
          timestamps = timestamps_buffer[load_audio_index]
          load_audio_index = None
        else:
          bad_sentence = True
          while bad_sentence:
            try:
              timestamps = main(sentence, links, skip=skip)
              bad_sentence = False
            except KeyError as e:
              print(e, 'not recognized')
              sentence = get_sentence(total_text)

        _concat_wav(timestamps)

        os.system(command)

        line = input("Enter 'y' to validate, 'e' to edit the sentence, 's' to store this audio in the buffer, 'l' + index for loading previously stored audio, otherwise just press enter: ")
        valid = line == 'y'
        edit = line == 'e'
        store = line == 's'

        if line.startswith("l "):
            index = line.split(" ")[1]
            if index.isdigit():
              index = int(index)
              if -1 < index < len(timestamps_buffer):
                load_audio_index = index
                print(load_audio_index)

        skip = True
        os.system('cls' if os.name == 'nt' else 'clear')

      total_timestamps.extend(timestamps)
      total_text += '\n' + sentence

      save(total_timestamps, total_text, name='video.json')
      sentence = get_sentence(total_text)

    print('\n'*80)
    paths = dl_videos(links)

    #TODO: enlever cette atrocité
    videos = {}
    for phonem in total_timestamps:
      if not phonem.get_audio_path() in videos:
        vid_path = next(p for p in paths 
             if os.path.basename(phonem.get_audio_path()).split('.')[0] == os.path.basename(p).split('.')[0])

        clip = VideoFileClip(vid_path)

        videos[phonem.get_audio_path()] = clip

    clips = []
    for seg in total_timestamps:
        clip = videos[seg.get_audio_path()]
        clips.append(clip.subclip(seg.get_start_timestamp(), seg.get_end_timestamp()))
    concatenate_videoclips(clips).write_videofile("out.mp4")
    print(total_text)

