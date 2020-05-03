class Word():
    def __init__(self, token, original_word):
        self._token = token
        self._original_word = original_word

    def get_token(self):
        return self._token

    def get_original_word(self):
        return self._original_word
