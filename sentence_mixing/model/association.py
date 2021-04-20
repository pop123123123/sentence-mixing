import functools
import itertools

import sentence_mixing.logic.analyze_step_2 as step_2
import sentence_mixing.logic.audio_analysis as audio_analysis
import sentence_mixing.logic.parameters as params
import sentence_mixing.logic.utils as utils
from sentence_mixing.model.scorable import Scorable


@functools.lru_cache(maxsize=None)
def association_builder(target_phonem, audio_phonem, randomizer):
    """Cached association constructor"""

    return Association(target_phonem, audio_phonem, randomizer)


class Association(Scorable):
    """
    Storage class regrouping target and audio phonem and associating a step 2 score
    It also constains a step 2 score, rating the association of phonems.
    """

    def __init__(self, target_phonem, audio_phonem, randomizer):
        self.target_phonem = target_phonem
        self.audio_phonem = audio_phonem
        self.randomizer = randomizer

        self._step_2_same_phonem_score = (
            target_phonem.transcription == audio_phonem.transcription
        ) * params.SCORE_SAME_TRANSCRIPTION

        self._step_2_same_word_score = (
            utils.are_homophones(target_phonem.word, audio_phonem.word)
            * params.SCORE_SAME_AUDIO_WORD
        )

    @property
    def _step_2_word_sequence_score(self):
        """Rates a common sequence of word between target and audio"""

        if (
            self.target_phonem.get_index_in_word()
            == self.audio_phonem.get_index_in_word()
        ):
            return step_2.rating_word_by_phonem_length(
                len(list(self.sequence_dictionary_homophones_phonems())),
                self.randomizer
            )
        return 0

    @property
    def _step_2_phonem_sequence_score(self):
        """Rates a common sequence of phonem between target and audio"""

        return step_2.rating_sequence_by_phonem_length(
            max(len(list(self.sequence_same_phonems())) - 1, 0),
            self.randomizer
        )

    @property
    def _step_2_phonem_sequence_backward_score(self):
        """
        Rates a common sequence of phonem between target and audio.
        This rate is computed in the reverse order and is complementary to
        _step_2_phonem_sequence_score.
        """

        return step_2.rating_sequence_by_phonem_length(
            max(len(list(self.sequence_same_phonems(reverse=True))) - 1, 0),
            self.randomizer
        )

    @property
    def _step_2_audio_score(self):
        """
        Rates the audio content of a phonem.
        For the <BLANK> tokens, checks if the audio_word is silent and also checks its duration.
        """

        score = 0
        if self.target_phonem.word.token == "<BLANK>":
            score = (
                audio_analysis.rate_silence(self.audio_phonem)
                * params.SCORE_SILENCE_AMPLITUDE
            )
            score += (
                audio_analysis.rate_duration(self.audio_phonem, 0.1, 0.2)
                * params.SCORE_DURATION
            )
        return score

    def __repr__(self):
        return f"<Association {self.target_phonem, self.audio_phonem}>"

    def _get_split_score(self):

        step_2_scores = {
            "step_2_audio_score": self._step_2_audio_score,
            "step_2_same_phonem": self._step_2_same_phonem_score,
            "step_2_same_word": self._step_2_same_word_score,
            "step_2_word_sequence": self._step_2_word_sequence_score,
            "step_2_phonem_sequence": self._step_2_phonem_sequence_score,
            "step_2_phonem_sequence_backward": self._step_2_phonem_sequence_backward_score,
        }
        return {**self.audio_phonem.get_split_score(), **step_2_scores}

    def sequence_dictionary_homophones_phonems(self):
        """
        This method returns a list of associations containing audio phonems corresponding to
        homophone words.
        We force the skip_force_blank argument to True to force get_sequence to evaluate <BLANK>
        only words.
        """

        return utils.association_sequence_from_words(
            utils.get_sequence_dictionary_homophones(
                self.target_phonem, self.audio_phonem, True
            ), self.randomizer
        )

    def sequence_aligner_homophones_phonems(self):
        """
        Retrieves associations corresponding to homophones.
        Two words are declared as homophones if they contain the same phonems as the Montreal audio
        phonem decomposition of the word.
        """

        return utils.association_sequence_from_words(
            utils.get_sequence_aligner_homophones(
                self.target_phonem, self.audio_phonem
            ), self.randomizer
        )

    @functools.lru_cache(maxsize=None)
    def sequence_same_phonems(self, reverse=False):
        """
        Returns the sequence of identical phonem between target and audio, starting from self
        association.

        Keyword arguments:
        reverse - determines the direction of checking.
                  if True, checks from the end of a word to the begining.
        """
        return list(
            itertools.takewhile(
                lambda association: association.target_phonem.transcription
                == association.audio_phonem.transcription,
                utils.sequence_association(self, self.randomizer, reverse=reverse),
            )
        )

    @functools.lru_cache(maxsize=None)
    def sequence_same_phonems_last_word_truncated(self):
        """
        Returns the sequence of identical phonem between target and audio, starting from self
        association.
        Only takes full words: if the common sequence finishes in the middle of the word, trunks
        it to the end of last full word.

        Example:
        Target: "trique fructifier"
        In audio, you can find: "géométrique frugale"
        self: ['t', 't']

        This function returns phonems associated to "trique", even if "fructifier" and "frugale"
        have the same phonem sequence 'f', 'r', 'u'.
        """

        try:
            target_last_end_phonem_word_index = next(
                i
                for i, asso in reversed(
                    list(enumerate(self.sequence_same_phonems()))
                )
                if asso.target_phonem == asso.target_phonem.word.phonems[-1]
            )
            audio_last_end_phonem_word_index = next(
                i
                for i, asso in reversed(
                    list(enumerate(self.sequence_same_phonems()))
                )
                if asso.audio_phonem == asso.audio_phonem.word.phonems[-1]
            )
            return list(self.sequence_same_phonems())[
                : 1
                + min(
                    target_last_end_phonem_word_index,
                    audio_last_end_phonem_word_index,
                )
            ]
        except StopIteration:
            return []

    @functools.lru_cache(maxsize=None)
    def sequence_same_phonems_first_word_truncated(self):
        """
        Returns the sequence of identical phonem between target and audio, starting from self
        association. Breaks when a new word is reached.
        """

        return list(
            map(
                lambda x: x[1],
                itertools.takewhile(
                    lambda x: x[0] == 0
                    or (
                        x[1].target_phonem.get_index_in_word() > 0
                        and x[1].audio_phonem.get_index_in_word() > 0
                    ),
                    enumerate(self.sequence_same_phonems()),
                ),
            )
        )
