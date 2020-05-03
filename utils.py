from num2words import num2words

import config


def replace_numbers(text_array):
    """
    Replaces numbers to plain text following the language given in JSON conf file

    Arguments:
    - text_array: array of strings

    Returns:
    transformation of text_array with numbers replaced in plain text
    """

    transformed = [
        num2words(int(word), lang=config.get_property("lang"))
        .replace("-", " ")
        .split(" ")
        if word.isdigit()
        else [word]
        for word in text_array
    ]

    final_array = []
    for words in transformed:
        for word in words:
            final_array.append(word)

    return final_array


def replace_numbers_string(text):
    """
    Replaces numbers to plain text following the language given in JSON conf file

    Arguments:
    - text: string

    Returns:
    transformation of text with numbers replaced in plain text
    """

    text = (
        text.replace(",", "")
        .replace(";", "")
        .replace(".", "")
        .replace("!", "")
        .replace("!", "")
    )

    return " ".join(replace_numbers(text.split(" ")))
