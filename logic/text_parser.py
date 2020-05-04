import re
from functools import lru_cache

from num2words import num2words

import config


@lru_cache(maxsize=None)
def get_dict():
    """Retrieves the dictionary and parses it to a python dict"""

    dict_path = config.get_property("dict_path")

    # Opens the dictionary file and puts it in a dict
    with open(dict_path) as f:
        phonem_dict = dict(x.rstrip().split(None, 1) for x in f)

    return phonem_dict


def transform_numbers(text):
    """Substitutes all numbers to plain text in given text"""

    text = re.sub(
        r"(\d+)",
        lambda x: num2words(x.group(1), lang=config.get_property("lang")),
        text,
    )
    return text


def split_text(text):
    """
    Formats the given text to isolate words by:
    - transforming numbers to plain text
    - isolating the punctuation symbols with spaces before and/or after
    - splits on whitespaces
    """

    text = transform_numbers(text)
    text = re.sub(r"\s*([^\s\w])\s*", " \\1 ", text)
    return text.split(" ")


def from_word_to_token(word):
    """
    Formats a word to turn it into a token:
    - handles special symbols such as dots
    - puts text in uppercase
    """

    punctuation = [".", "?", "!", ",", ";", ":"]
    if word in punctuation:
        return "SP"

    if not word.isalnum():
        return None

    return word.upper()


def from_token_to_phonem(token):
    """Returns a phonem transcription list corresponding to a given word token"""

    if token == "SP":
        return ["sp"]

    return get_dict()[token].split()
