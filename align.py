import os, tempfile, config

def _read_subs(path):
  # TODO
  return [(0, 'This is a subtitle example')]

def _split_audio_in_files(subs, audio_path):
  # TODO
  return 'folder'

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