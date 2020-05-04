import re
from functools import lru_cache

from num2words import num2words

import config


@lru_cache(maxsize=None)
def get_dict():
    dict_path = config.get_property("dict_path")

    # Opens the dictionary file and puts it in a dict
    with open(dict_path) as f:
        phonem_dict = dict(x.rstrip().split(None, 1) for x in f)

    return phonem_dict


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
    text = transform_numbers(text)
    text = re.sub(r"\s*([^\s\w])\s*", " \\1 ", text)
    return text.split(" ")


def from_word_to_token(word):
    if word == ".":
        return "SP"

    return word.upper()
