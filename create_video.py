from main import main
import youtube_dl, os
from moviepy.editor import VideoFileClip, concatenate_videoclips
from serialize import load, save

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
    while sentence != '':
      timestamps = []

      edit = False
      valid = False
      while not valid:
        if edit:
          sentence = get_sentence(total_text)

        bad_sentence = True
        while bad_sentence:
          try:
            timestamps = main(sentence, links, skip=skip)
            bad_sentence = False
          except KeyError as e:
            print(e, 'not recognized')
            sentence = get_sentence(total_text)

        os.system(command)
        line = input("Enter 'y' to validate, 'e' to edit the sentence, otherwise just press enter: ")
        valid = line == 'y'
        edit = line == 'e'
        skip = True
        os.system('cls' if os.name == 'nt' else 'clear')

      total_timestamps.extend(timestamps)
      total_text += '\n' + sentence

      sentence = get_sentence(total_text)

    print('\n'*80)
    paths = dl_videos(links)
    clip = VideoFileClip(paths[0])
    clips = [clip.subclip(*seg) for seg in total_timestamps]
    concatenate_videoclips(clips).write_videofile("out.mp4")
    print(total_text)
