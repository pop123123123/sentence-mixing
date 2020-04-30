import json

config_errmsg = {
  'align_exe': 'the path to the Montreal align executable',
  'dict_path': 'the path to the phonem dictionary',
  'trained_model': 'the path to the trained model',
  'lang': 'the lang of the subtitles (used to convert numbers into plain text)'
}

config = None
def _load_config():
  global config
  try:
    with open('config.json') as f:
      config = json.load(f)
  except EnvironmentError:
    raise FileNotFoundError("No configuration file found. Please create and fill a 'config.json' file.")

def get_property(name):
  if config is None:
    _load_config()
  try:
    return config[name]
  except KeyError:
    raise KeyError(f'Please add the {name} property to your config.json containing {config_errmsg[name]}.')
