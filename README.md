# Sentence mixing

This library is used to analyze and smartly reorder phonems of an audio sequence to form any desired sentence.  
The goal of this library is to generate Sentence Mixing Youtube poops ([example](https://www.youtube.com/watch?v=ZGCoKsPXgkw)).  

Entry file is ```sentence_mixer.py```.  
Here is are examples of applications based on the library:
- [CLI application](https://github.com/pop123123123/CLI_sentence_mixing)
- [GUI application (unstable)](https://github.com/pop123123123/SentenceMixingMaker)

## MFA

SM library is using [Montreal Forced Aligner](https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner), a powerful tool used to timestamp words and phonems in a subtitled audio file.  

### Installing MFA

MFA is kind of hard to install. You can download the builded release, but to use it, you should have python3.6.  

Otherwise, we prepared a tutorial to build it from source:

1. Download [release source code 1.0.1](https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner/releases/tag/v1.0.1)
2. Extract it as ```Montreal-Forced-Aligner```
3. Install all python modules listed in ```requirements.txt```
4. Install [kaldi](https://github.com/kaldi-asr/kaldi) (available in pacman's repo Arch4edu)
5. In folder ```Montreal-Forced-Aligner/freezing```, run ```freeze.sh```
6. In folder ```Montreal-Forced-Aligner/thirdparty```, run the following command: ```python kaldibinaries.py /opt/kaldi```
7. Copy every file from ```/opt/kaldi/src/featbin``` to ```Montreal-Forced-Aligner/thirdparty/bin```
8. Move ```align.py``` from ```Montreal-Forced-Aligner/aligner/command_line``` to ```Montreal-Forced-Aligner/```

## JSON config file

To use the library, you have to provide a json configuration file.
Here are all the fields to add into it:

- ```dict_path```: Path to dictionnary file. This dictionnary associates every words of a language to associated phonems
- ```align_exe```: MFA executable file 
- ```trained_model```: pre-trained model MFA will use. Should be a ZIP file.
- ```lang```: language. Only 'fr' is supported now
- ```dict_consonant_vowel_path```: Path to dictionary declaring the consonant and vowel phonems
- ```folder```: Folder where the Youtube subtitles will be stored

This config file should be passed through the function ```prepare_sm_config_file```

### Recommended config.json

- ```dict_path```: For french users, use ```fr.dict``` from [SM-Dictionaries](https://github.com/nbusser/SM-Dictionaries) repo
- ```align_exe```: Write a tiny shell script that
    1. Adds ```Montreal-Forced-Aligner/thirdparty/bin/``` to your path
    2. Runs ```python Montreal-Forced-Aligner/align.py $@```
- ```trained_model```: Choose one of the [MFA pretrained model](https://montreal-forced-aligner.readthedocs.io/en/latest/pretrained_models.html). For french users, use [prosodylab version](https://github.com/MontrealCorpusTools/mfa-models/raw/master/acoustic/french_prosodylab.zip).
- ```dict_consonant_vowel_path```: For french users, use ```fr_consonant_vowel.dict``` from [SM-Dictionaries](https://github.com/nbusser/SM-Dictionaries) repo

