import re

from num2words import num2words

import config
from utils import replace_numbers

PHONEM_DICT = None


def get_dict():
    global PHONEM_DICT
    if PHONEM_DICT is None:
        dict_path = config.get_property("dict_path")

        # Opens the dictionary file and puts it in a dict
        with open(dict_path) as f:
            PHONEM_DICT = dict(x.rstrip().split(None, 1) for x in f)

    return PHONEM_DICT


def from_token_to_phonem(token):
    if token == "SP":
        return "sp"
    return get_dict()[token].split()


def transform_numbers(text):
    text = re.sub(
        r"(\d+)",
        lambda x: num2words(x.group(1), lang=config.get_property("lang")),
        text,
    )
    return text


def split_text(text):
    text = re.sub(r"\s*([^\s\w])\s*", " \\1 ", text)
    return text.split(" ")


def from_word_to_token(word):
    if word == ".":
        return "SP"

    return word.upper()
