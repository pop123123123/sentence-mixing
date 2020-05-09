import functools

import logic.analyze_step_3
import logic.global_audio_data
import logic.parameters as params
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
            elif len(dictionary_homophones_phonems) == 2:
                return [
                    Choice(
                        self,
                        dictionary_homophones_phonems[1],
                        self.nodes_left,
                        *self.compute_child_step_3_score(
                            dictionary_homophones_phonems[1]
                        ),
                    )
                ]

            elif len(aligner_homophones_phonems) > 2:
                return [SkippedChoice(self, aligner_homophones_phonems[1:])]
            elif len(aligner_homophones_phonems) == 2:
                return [
                    Choice(
                        self,
                        aligner_homophones_phonems[1],
                        self.nodes_left,
                        *self.compute_child_step_3_score(
                            aligner_homophones_phonems[1]
                        ),
                    )
                ]

        # Check for phonem skipping
        same_phonems = (
            self.association.sequence_same_phonems_first_word_truncated()
        )
        if len(same_phonems) > 2:
            return [SkippedChoice(self, same_phonems[1:])]
        elif len(same_phonems) == 2:
            return [
                Choice(
                    self,
                    same_phonems[1],
                    self.nodes_left,
                    *self.compute_child_step_3_score(same_phonems[1]),
                )
            ]

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
        associations = [association] + [
            c.association for c in self.get_self_and_previous_choices()
        ]

        if len(associations) > 1:
            rate = []

            rate.append(
                logic.analyze_step_3.step_3_audio_rating(
                    logic.analyze_step_3.get_last_vowel(associations),
                    association.audio_phonem,
                )
                * params.RATING_SPECTRAL_SIMILARITY
            )

            rate.append(
                params.RATING_LENGTH_SAME_PHONEM
                * logic.analyze_step_3.step_3_n_following_previous_phonems(
                    associations
                )
            )

            return rate
        return [0, 0]


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
