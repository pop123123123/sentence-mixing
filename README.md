# Sentence mixing

This library is used to analyze and smartly reorder phonems of an audio sequence to form any desired sentence.
The goal of this library is to generate Sentence Mixing Youtube poops ([example](https://www.youtube.com/watch?v=ZGCoKsPXgkw)).

Entry file is ```sentence_mixer.py```.
Here are examples of applications based on the library:
- [CLI application](https://github.com/pop123123123/CLI_sentence_mixing)
- [GUI application (unstable)](https://github.com/pop123123123/SentenceMixingMaker)

## MFA

SM library is using [Montreal Forced Aligner](https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner), a powerful tool used to timestamp words and phonems in a subtitled audio file.

### Installing MFA

1. Download [release executable version 1.1.0 Beta 2](https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner/releases/tag/v1.1.0-beta.2)
2. Extract it as ```Montreal-Forced-Aligner```

## JSON config file

To use the library, you have to provide a json configuration file.
Here are all the fields to add into it:

- ```dict_path```: Path to dictionnary file. This dictionnary associates every words of a language to associated phonems
- ```align_exe```: MFA executable file
- ```trained_model```: pre-trained model MFA will use. Should be a ZIP file
- ```lang```: language. Only 'fr' is supported now
- ```dict_consonant_vowel_path```: Path to dictionary declaring the consonant and vowel phonems
- ```folder```: Folder where the Youtube subtitles will be stored

This config file should be passed through the function ```prepare_sm_config_file```

### Recommended config.json

- ```dict_path```: For french users, use ```fr.dict``` from [SM-Dictionaries](https://github.com/nbusser/SM-Dictionaries) repo
- ```align_exe```: ```Montreal-Forced-Aligner/bin/mfa_align```
- ```trained_model```: Choose one of the [MFA pretrained model](https://montreal-forced-aligner.readthedocs.io/en/latest/pretrained_models.html). For french users, use [prosodylab version](https://github.com/MontrealCorpusTools/mfa-models/raw/master/acoustic/french_prosodylab.zip).
- ```dict_consonant_vowel_path```: For french users, use ```fr_consonant_vowel.dict``` from [SM-Dictionaries](https://github.com/nbusser/SM-Dictionaries) repo

