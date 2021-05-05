import json

config_errmsg = {
    "align_exe": "the path to the Montreal align executable",
    "g2p_exe": "the path to the Montreal g2p executable",
    "g2p_model": "the path to the Montreal g2p model",
    "dict_path": "the path to the phonem dictionary",
    "dict_consonant_vowel_path": "the path to the consonant-voyel phonem classifier dict",
    "trained_model": "the path to the trained model",
    "lang": "the lang of the subtitles (used to convert numbers into plain text)",
    "folder": "the folder where the sub chunks will be stored",
    "stt_model_path": "path to speech to text model folder",
    "stt_full_dict_path": "path to speech to text original dictionary",
    "stt_tmp_dict_path": "path where the compatible dictionary should be generated",
}

config = None
config_path = None


def set_config_path(path):
    global config
    config_path = path

    try:
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)
    except EnvironmentError:
        raise FileNotFoundError(
            "No configuration file found. Please create and fill a 'config.json' file."
        )


def set_config_dict(config_dict):
    global config
    config = config_dict


def is_ready():
    return config is not None


def get_property(name):
    try:
        return config[name]
    except KeyError:
        raise KeyError(
            f"Please add the {name} property to your config.json containing {config_errmsg[name]}."
        )


def set_temp_property(name, value):
    global config
    if name in config:
        raise KeyError(f"Property {name} already exists")

    config[name] = value
