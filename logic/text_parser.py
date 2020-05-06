import functools
import re

from num2words import num2words

import config


@functools.lru_cache(maxsize=None)
def get_dict():
    """Retrieves the dictionary and parses it to a python dict"""

    dict_path = config.get_property("dict_path")

    # Opens the dictionary file and puts it in a dict
    with open(dict_path) as f:
        phonem_dict = dict(x.rstrip().split(None, 1) for x in f)

    return phonem_dict


@functools.lru_cache(maxsize=None)
def get_consonant_vowel_dict():
    """
    Retrieves the consonant-vowel dictionary and parses it to a reverse python dict
    Python dict structure: phonem -> phonem_category

    Three categories available: CONSONANT, VOWEL, SPACE
    """

    dict_path = config.get_property("dict_consonant_vowel_path")

    with open(dict_path) as f:
        consonant_vowel_dict = dict(
            [
                [elem, line.split()[0]]
                for line in f
                for elem in line.split()[1:]
            ]
        )

    return consonant_vowel_dict


@functools.lru_cache(maxsize=None)
def get_all_phonems():
    """Retrieves a list of all phonems relying on the consonant-vowel dictionary"""

    with open(config.get_property("dict_consonant_vowel_path")) as f:
        return [phonem for line in f for phonem in line.split()[1:]]


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
    text = re.sub(r"\s*(\w')\s*", "\\1 ", text)
    text = re.sub(r"\s*([^\s\w'])\s*", " \\1 ", text)
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

    if word == "":
        return "<BLANK>"

    if not word.replace("'", "a").isalnum():
        return "<TRASH>"

    return word.upper()


def from_token_to_phonem(token):
    """Returns a phonem transcription list corresponding to a given word token"""

    if token == "SP":
        return ["sp"]

    if token == "<BLANK>":
        return ["sp"]

    if token == "<TRASH>":
        return None

    return get_dict()[token].split()
