import os, tempfile, config
from pathlib import Path
from scipy.io import wavfile
import webvtt
import datetime
import base64
from utils import replace_numbers_string
from subtitle import Subtitle

def _read_subs(path):
  """Parses subtitles into an array of tuples ((x, y), z) where x = start, y = end, z = text"""

  def _get_sec(time_str):
    h, m, s = time_str.split(':')
    return float(h)*3600+float(m)*60+float(s)

  return [Subtitle(_get_sec(caption.start),
            _get_sec(caption.end),
           replace_numbers_string(caption.text.split('\n')[-1]))
          for caption in webvtt.read(path)]

def _split_audio_in_files(subs, audio_path, video_name):
  """Saves each sub in a separate audio file and text file"""

  # Arbitrary name
  folder_name = config.get_property('folder')
  Path(folder_name).mkdir(parents=True, exist_ok=True)

  video_hashed_name = base64.b64encode(video_name.encode("utf-8"))
  video_hashed_name = str(video_hashed_name, "utf-8")

  for i, sub in enumerate(subs):
      sub.create_audio(os.path.join(folder_name, video_hashed_name + "." + str(i)+".wav"), audio_path)
      sub.save_sub(os.path.join(folder_name, video_hashed_name + '.' + str(i)+".lab"))

  return folder_name

def _concat_wav(segments, audio_path):
  rate, data = wavfile.read(audio_path)
  import numpy as np
  new_clip = data[0:1]
  for segment in segments:
    start_frame = int(segment[0]*rate)
    end_frame = int(segment[1]*rate)

    new_clip = np.concatenate((new_clip, data[start_frame:end_frame]))

  wavfile.write("out.wav", rate, new_clip)

def extract_subs(audio_path, subs_path):
  """Extracts little subs from vtt file and saves it into multiple files"""

  video_name = os.path.basename(audio_path)

  subs = _read_subs(subs_path)
  _split_audio_in_files(subs, audio_path, video_name)
  return subs


def align_phonems():
  """Launches the aligner"""

  folder = config.get_property('folder')
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

  return out_dir
