import functools
import itertools

import logic.analyze_step_2
import logic.parameters as params
import logic.utils
from model.scorable import Scorable


@functools.lru_cache(maxsize=None)
def association_builder(target_phonem, audio_phonem):
    return Association(target_phonem, audio_phonem)


class Association(Scorable):
    """Storage class regrouping target and audio phonem and associating a step 2 score"""

    def __init__(self, target_phonem, audio_phonem):
        self.target_phonem = target_phonem
        self.audio_phonem = audio_phonem

        self._step_2_same_phonem_score = (
            target_phonem.transcription == audio_phonem.transcription
        ) * params.SCORE_SAME_TRANSCRIPTION

        self._step_2_same_word_score = (
            logic.utils.are_homophones(target_phonem.word, audio_phonem.word)
            * params.SCORE_SAME_AUDIO_WORD
        )

    @property
    def _step_2_word_sequence_score(self):
        if (
            self.target_phonem.get_index_in_word()
            == self.audio_phonem.get_index_in_word()
        ):
            return logic.analyze_step_2.rating_word_by_phonem_length(
                len(list(self.sequence_dictionary_homophones_phonems()))
            )
        return 0

    @property
    def _step_2_phonem_sequence_score(self):
        return logic.analyze_step_2.rating_sequence_by_phonem_length(
            max(len(list(self.sequence_same_phonems())) - 1, 0)
        )

    @property
    def _step_2_phonem_sequence_backward_score(self):
        return logic.analyze_step_2.rating_sequence_by_phonem_length(
            max(len(list(self.sequence_same_phonems(reverse=True))) - 1, 0)
        )

    @property
    @functools.lru_cache(maxsize=None)
    def _step_2_audio_score(self):
        score = 0
        if self.target_phonem.word.token == "<BLANK>":
            score = (
                logic.audio_analysis.rate_silence(self.audio_phonem.get_wave())
                * params.SCORE_SILENCE_AMPLITUDE
            )
            score += (
                logic.audio_analysis.rate_duration(self.audio_phonem, 0.1, 0.2)
                * params.SCORE_DURATION
            )
        return score

    def __repr__(self):
        return f"<Association {self.target_phonem, self.audio_phonem}>"

    def get_splited_score(self):
        step_2_scores = {
            "step_2_audio_score": self._step_2_audio_score,
            "step_2_same_phonem": self._step_2_same_phonem_score,
            "step_2_same_word": self._step_2_same_word_score,
            "step_2_word_sequence": self._step_2_word_sequence_score,
            "step_2_phonem_sequence": self._step_2_phonem_sequence_score,
            "step_2_phonem_sequence_backward": self._step_2_phonem_sequence_backward_score,
        }
        return {**self.audio_phonem.get_splited_score(), **step_2_scores}

    def sequence_dictionary_homophones_phonems(self):
        """
        This method returns a list of associations containing audio phonems corresponding to
        homophone words.
        We force the skip_force_blank argument to True to force get_sequence to evaluate <BLANK>
        only words.
        """

        return logic.utils.association_sequence_from_words(
            logic.utils.get_sequence_dictionary_homophones(
                self.target_phonem, self.audio_phonem, True
            )
        )

    def sequence_aligner_homophones_phonems(self):
        return logic.utils.association_sequence_from_words(
            logic.utils.get_sequence_aligner_homophones(
                self.target_phonem, self.audio_phonem
            )
        )

    @functools.lru_cache(maxsize=None)
    def sequence_same_phonems(self, reverse=False):
        return list(
            itertools.takewhile(
                lambda association: association.target_phonem.transcription
                == association.audio_phonem.transcription,
                logic.utils.sequence_association(self, reverse=reverse),
            )
        )

    @functools.lru_cache(maxsize=None)
    def sequence_same_phonems_last_word_truncated(self):
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
