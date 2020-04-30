#!/usr/bin/env python3

import config

def get_phonems(text, sentence_splitter=False):
    """
    Transforms sentence to an array of array of phonems

    Arguments:
    - text: a text to parse. It can contain one or more sentence.
    - sentence_splitter: if set to True, uses '.' as sentence separator

    Returns:
    an array of array of phonems
    The first dimension is the sentence (dot separated), the second are the phonems

    Example:
    text = "Je suis l'Homme cool. Prosternez vous"
    sentence_splitter = True

    The function returns:
    [
        ['Z', 'deux', 's', 'huit', 'i', 'l', 'O', 'm', 'k', 'u', 'l'],
        ['p', 'R', 'o', 's', 't', 'E', 'R', 'n', 'e', 'v', 'u']
    ]
    """
    dict_path = config.get_property("dict_path")

    try:
        # Opens the dictionary file and puts it in a dict
        with open(dict_path) as f:
            phonem_dict = dict(x.rstrip().split(None, 1) for x in f)

            # If sentence_splitter mode is on, splits on dots
            if sentence_splitter:
                sentences = text.split(".")
            else:
                sentences = [text]

            # First transformation: transforms the sentences by:
            # -removing punctuation
            # -isolating apostrophes
            # -turning to uppercase
            # -splitting on spaces
            def _format_string(sentence):
                sentence =  sentence.replace(".", " SP ").replace("!", "").replace(",", "").replace("?", "").replace(";", "")
                sentence = sentence.replace("'", "' ")
                sentence = sentence.strip()
                sentence = sentence.upper()
                return sentence.split()

            sentences = list(map(_format_string, sentences))

            # Second transformation: replaces all the ords by arrays of its phonems
            def _to_phonem(sentence):
                def _word_to_phonem(word):
                    return phonem_dict[word].split()
                return list(map(_word_to_phonem, sentence))

            sentences = list(map(_to_phonem, sentences))

            # Third transformation: flattens all the array of phonems to a single one
            def _big_flatten(sentence):
                final_array = [phonem for phonem_array in sentence for phonem in phonem_array]
                return final_array

            sentences = list(map(_big_flatten, sentences))
    except EnvironmentError:
        print("File specified in property 'dict_path' of JSON config file was not found.")
        exit(1)

    return sentences
