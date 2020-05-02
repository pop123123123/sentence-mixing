from main import main
from serialize import load, save
from video_creator.audio import concat_wav

import os

def get_sentence(text):
  if text is not None:
    print('Previous sentences:\n', text)
  return input('Enter a sentence: ')

def loop_interface(audio_command, skip_first, links):
  total_timestamps = []
  total_text = ""
  timestamps_buffer = []
  timestamps_buffer_sentence = []
  skip = skip_first

  sentence = get_sentence(None)

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
        timestamps_buffer_sentence.append(sentence)
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

      concat_wav(timestamps)

      os.system(audio_command)

      if timestamps_buffer_sentence:
          print("Stashed audios:")
          for i, stashed_sentence in enumerate(timestamps_buffer_sentence):
            print(i, ".", stashed_sentence)
          print("")

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
  return total_timestamps, total_text
