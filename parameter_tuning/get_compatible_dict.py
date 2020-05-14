import os

import logic.text_parser as tp


def generate_compatible_dictionary(speach_to_text_dict, generated_dict_path):
    """Leans speach to text dictionary to keep only words present in SM dictionary"""

    def filter_line(line):
        """Tokenizes the word and checks if it is present in original dict"""

        word = line.split()[0]
        token = word.split("(")[0].upper()

        if token[0] == "-":
            token = token[1:]

        return token in tp.get_dict()

    stt_dict = open(speach_to_text_dict)

    # Reads dictionary
    stt_dict = stt_dict.readlines()

    # Only keep words e can find in the original dictionary
    stt_dict = list(filter(filter_line, stt_dict))

    try:
        os.remove(generated_dict_path)
    except FileNotFoundError:
        pass

    with open(generated_dict_path, "w") as filehandle:
        for line in stt_dict:
            filehandle.write(line)

    # .env/lib/python3.6/site-packages/speech_recognition/pocketsphinx-data/fr-FR/pronounciation-dictionary.dict
