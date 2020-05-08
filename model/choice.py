import functools
import itertools
import math

import logic.analyze_step_2
import logic.analyze_step_3
import logic.global_audio_data
import logic.parameters as params
import logic.text_parser as tp
import logic.utils
from model.scorable import Scorable


class Choice(Scorable):
    """
    This class represents a node in the decision tree

    Class parameters:
    parent - father node in the tree
    association - last association decided by parent
    _audio_score - audio score of association (step 3 scoring)
    _previous_score - previous score of association (step 3 scoring)
    children - children nodes in the tree
    """

    def __init__(
        self,
        parent,
        current_association,
        nodes_left,
        audio_score,
        previous_score,
    ):
        self.parent = parent
        self.nodes_left = nodes_left
        self.children = []

        self.association = current_association

        self._audio_score = audio_score
        self._previous_score = previous_score

    def get_self_and_previous_choices(self):
        yield self
        if self.parent is not None:
            for c in self.parent.get_self_and_previous_choices():
                yield c

    @functools.lru_cache(maxsize=None)
    def _create_children(self):
        """Creates choice children"""
        # Leaf child
        if self.association.target_phonem.next_in_seq() is None:
            return []

        # Check for word skipping
        if self.association.target_phonem.get_index_in_word() == 0:
            dictionary_homophones_phonems = list(
                self.association.sequence_dictionary_homophones_phonems()
            )
            aligner_homophones_phonems = list(
                self.association.sequence_aligner_homophones_phonems()
            )

            if len(dictionary_homophones_phonems) > 2:
                return [SkippedChoice(self, dictionary_homophones_phonems[1:])]
            elif len(aligner_homophones_phonems) > 2:
                return [SkippedChoice(self, aligner_homophones_phonems[1:])]

        # Check for phonem skipping
        same_phonems = (
            self.association.sequence_same_phonems_first_word_truncated()
        )
        if len(same_phonems) > 2:
            return [SkippedChoice(self, same_phonems[1:])]

        # Normal workflow
        target_phonem = self.association.target_phonem.next_in_seq()
        return logic.analyze.compute_children(
            target_phonem, self.nodes_left, self
        )

    def get_combos(self):
        """Recursively creates children and returns a list of combos created from leaf nodes"""

        self.children = self._create_children()

        if len(self.children) == 0:
            return [Combo(self)]

        return sum((child.get_combos() for child in self.children), [])

    def get_splited_score(self):
        step_3_scores = {
            "step_3_audio_spectral": self._audio_score,
            "step_3_same_word_previous_phonems": self._previous_score,
        }
        return {**self.association.get_splited_score(), **step_3_scores}

    def compute_child_step_3_score(self, association):
        return logic.analyze_step_3.step_3_rating(
            [
                ch.association.audio_phonem
                for ch in self.get_self_and_previous_choices()
            ],
            association.audio_phonem,
        )


class SkippedChoice(Choice):
    def __init__(self, parent, associations_list):
        Choice.__init__(
            self,
            parent,
            associations_list[0],
            parent.nodes_left,
            *parent.compute_child_step_3_score(associations_list[0]),
        )
        self._associations_list = associations_list[1:]

    def _create_children(self):
        if len(self._associations_list) > 1:
            return [SkippedChoice(self, self._associations_list)]
        else:
            score = self.compute_child_step_3_score(self._associations_list[0])
            return [
                Choice(
                    self, self._associations_list[0], self.nodes_left, *score
                )
            ]


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
            tp.are_token_homophones(
                target_phonem.word.token, audio_phonem.word.token
            )
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
            len(list(self.sequence_same_phonems()))
        )

    def __repr__(self):
        return f"<Association {self.target_phonem, self.audio_phonem}>"

    def get_splited_score(self):
        step_2_scores = {
            "step_2_same_phonem": self._step_2_same_phonem_score,
            "step_2_same_word": self._step_2_same_word_score,
            "step_2_word_sequence": self._step_2_word_sequence_score,
            "step_2_phonem_sequence": self._step_2_phonem_sequence_score,
        }
        return {**self.audio_phonem.get_splited_score(), **step_2_scores}

    def sequence_dictionary_homophones_phonems(self):
        return logic.utils.association_sequence_from_words(
            logic.utils.get_sequence_dictionary_homophones(
                self.target_phonem, self.audio_phonem
            )
        )

    def sequence_aligner_homophones_phonems(self):
        return logic.utils.association_sequence_from_words(
            logic.utils.get_sequence_aligner_homophones(
                self.target_phonem, self.audio_phonem
            )
        )

    @functools.lru_cache(maxsize=None)
    def sequence_same_phonems(self):
        return list(
            itertools.takewhile(
                lambda association: association.target_phonem.transcription
                == association.audio_phonem.transcription,
                logic.utils.sequence_association(self),
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


class Combo:
    """Represents a complete combo"""

    def __init__(self, leaf_choice):
        self.leaf_choice = leaf_choice

    def __repr__(self):
        return f"<combo: {list(self.get_audio_phonems())} >"

    def get_score(self):
        return sum(
            ch.get_total_score()
            for ch in self.leaf_choice.get_self_and_previous_choices()
        )

    def get_audio_phonems(self):
        return [ch.association.audio_phonem for ch in self.get_choices()]

    def get_choices(self):
        return list(
            reversed(list(self.leaf_choice.get_self_and_previous_choices()))
        )
