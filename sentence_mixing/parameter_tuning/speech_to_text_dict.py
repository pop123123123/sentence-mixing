import functools
import os
import re

import config

import sentence_mixing.logic.text_parser as tp


@functools.lru_cache(maxsize=1)
def get_speech_to_text_dict():
    """Retrieves the dictionary and parses it to a python dict"""

    dict_path = config.get_property("stt_tmp_dict_path")

    if not os.path.exists(dict_path):
        raise FileNotFoundError(
            "Temporary dictionary not found. Please run generate_compatible_dictionary()"
        )

    # Opens the dictionary file and puts it in a dict
    with open(dict_path) as f:
        phonem_dict = dict()
        previous = None
        for line in f:
            split = line.split(maxsplit=1)
            k, v = split[0], split[1]
            if k == previous:
                phonem_dict[k] = None
            else:
                phonem_dict[k] = v
            previous = k

    return phonem_dict


def generate_compatible_dictionary():
    """Leans speech to text dictionary to keep only words present in SM dictionary"""

    def filter_line(line):
        """Tokenizes the word and checks if it is present in original dict"""

        word = line.split()[0]
        token = word.split("(")[0].upper()

        if token[0] == "-":
            token = token[1:]

        return token in tp.get_dict()

    stt_dict = open(config.get_property("stt_full_dict_path"))

    # Reads dictionary
    stt_dict = stt_dict.readlines()

    # Only keep words e can find in the original dictionary
    stt_dict = list(filter(filter_line, stt_dict))

    tmp_dict_file = config.get_property("stt_tmp_dict_path")
    try:
        os.remove(tmp_dict_file)
    except FileNotFoundError:
        pass

    with open(tmp_dict_file, "w") as filehandle:
        for line in stt_dict:
            filehandle.write(line)


def sentence_to_phonem_list(sentence):
    sentence = sentence.lower()

    # Removing punctuation symbols
    sentence = re.sub(r"\s*([^\s\w'])\s*", "", sentence)

    # Isolating apostrophes
    sentence = re.sub(r"(\w')\s*", "\\1 ", sentence)

    stt_dict = get_speech_to_text_dict()

    phonems = [
        phonem
        for word in sentence.split()
        for phonem in stt_dict[word].split()
    ]

    return phonems
