import os, tempfile, config
from pathlib import Path
from scipy.io import wavfile
import webvtt
import datetime

def _read_subs(path):
  """Parses subtitles into an array of tuples ((x, y), z) where x = start, y = end, z = text"""

  def _get_sec(time_str):
    h, m, s = time_str.split(':')
    return float(h)*3600+float(m)*60+float(s)

  return [((_get_sec(caption.start), _get_sec(caption.end)), caption.text)
          for caption in webvtt.read(path)]

def _split_audio_in_files(subs, audio_path):
  """Saves each sub in a separate audio file and text file"""

  # Arbitrary name
  folder_name = 'subs'
  Path(folder_name).mkdir(parents=True, exist_ok=True)

  rate, data = wavfile.read(audio_path)

  for i, sub in enumerate(subs):
    # Audio processing
    # Cuts the audio file at the proper frames
    # Saves the new audio to an individual file
    start_frame = int(sub[0][0]*rate)
    end_frame = int(sub[0][1]*rate)

    sub_audio_data = data[start_frame:end_frame]
    wavfile.write(os.path.join(folder_name, str(i)+".wav"), rate, sub_audio_data)

    # Writes the subtitle in a .lab file
    with open(os.path.join(folder_name, str(i)+".lab"), "w") as subfile:
      subfile.write(sub[1])

  return folder_name

def _concat_wav(segments, audio_path):
  rate, data = wavfile.read(audio_path)

  new_clip = []
  for segment in segments:
    start_frame = int(segment[0]*rate)
    end_frame = int(segment[1]*rate)

    new_clip += data[start_frame:end_frame]

  wavfile.write("out.wav")

def align_phonems(audio_path, subs_path):
  subs = _read_subs(subs_path)
  folder = _split_audio_in_files(subs, audio_path)
  speakers = 1

  align_exe = config.get_property('align_exe')
  dict_path = config.get_property('dict_path')
  trained_model = config.get_property('trained_model')
  out_dir = tempfile.mkdtemp()
  temp_dir = tempfile.mkdtemp()

  command = f'{align_exe} "{folder}" "{dict_path}" "{trained_model}" "{out_dir}" -t "{temp_dir}" -s {str(speakers)}'
  print(command)
  ret = os.system(command)
  # TODO: check ret

  return subs, out_dir
