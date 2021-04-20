# Sentence mixing

This library is used to analyze and smartly reorder phonemes of an audio sequence to form any desired sentence.
The goal of this library is to generate Sentence Mixing Youtube poops ([example](https://www.youtube.com/watch?v=ZGCoKsPXgkw)).

Entry file is ```sentence_mixer.py```.
Here are examples of applications based on the library:
- [CLI application](https://github.com/pop123123123/CLI_sentence_mixing)
- [GUI application (unstable)](https://github.com/pop123123123/SentenceMixingMaker)

## MFA

SM library is using [Montreal Forced Aligner](https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner), a powerful tool used to timestamp words and phonemes in a subtitled audio file.

### Installing MFA

1. Download [release executable version 1.1.0 Beta 2](https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner/releases/tag/v1.1.0-beta.2)
2. Extract it as ```Montreal-Forced-Aligner```

## JSON config file

To use the library, you have to provide a json configuration file.
Here are all the fields to add into it:

- ```dict_path```: Path to dictionnary file. This dictionnary associates every words of a language to associated phonemes
- ```align_exe```: MFA executable file
- ```trained_model```: pre-trained model MFA will use. Should be a ZIP file
- ```lang```: three languages are supported for the moment: ```fr```, ```en``` and ```de```
- ```dict_consonant_vowel_path```: Path to dictionary declaring the consonant and vowel phonemes
- ```folder```: Folder where the Youtube subtitles will be stored

This config file should be passed through the function ```prepare_sm_config_file```

### Recommended config.json

Example for French language:
- ```dict_path```: choose ```fr/fr.dict``` dictionary in [SM-Dictionaries](https://github.com/nbusser/SM-Dictionaries) repo
- ```align_exe```: ```Montreal-Forced-Aligner/bin/mfa_align```
- ```trained_model```: choose [french prosodylab model](https://github.com/MontrealCorpusTools/mfa-models/raw/master/acoustic/french_prosodylab.zip) among [MFA pretrained model](https://montreal-forced-aligner.readthedocs.io/en/latest/pretrained_models.html)
- ```lang```: ```fr```
- ```dict_consonant_vowel_path```: choose ```fr/fr_consonant_vowel.dict``` consonant vowel dict in [SM-Dictionaries](https://github.com/nbusser/SM-Dictionaries) repo

## Add an unsupported language

Please refer to this section of [SM-Dictionaries](https://github.com/nbusser/SM-Dictionaries/blob/master/README.md#add-a-new-language).
