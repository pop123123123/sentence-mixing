class PhonemGroup():
    #TODO: the phonem array is immutable. is it ok ?
    #TODO: it asserts that all the phonems comes from the same video. We've got to think about it
    #TODO: asserts that all the phonems in the group are consecutives
    def __init__(self, phonems, original_word=""):
        if not isinstance(phonems, list):
            phonems = [phonems]

        if not all(p.get_audio_path() == phonems[0].get_audio_path() for p in phonems):
            raise Exception("All the phonems doesn't come from the same audio file")

        self._phonems = []
        self._phonems.extend(phonems)
        self._phonems.sort(key=lambda x: x.get_start_timestamp())

        self._original_word = original_word

    def get_start_timestamp(self):
        return self._phonems[0].get_start_timestamp()

    def get_end_timestamp(self):
        return self._phonems[-1].get_end_timestamp()

    def get_related_audio_path(self):
        return self._phonems[0].get_audio_path()

    def get_phonem_list(self):
        return ' '.join([phonem.get_phonem() for phonem in self._phonems])

    def get_original_word(self):
        return self._original_word

    def get_phonems(self):
        return self._phonems
