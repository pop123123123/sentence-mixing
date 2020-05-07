import functools

import logic.parameters as params
import logic.text_parser as tp
from model.scorable import Scorable


class Choice(Scorable):
    """
    This class represents a node in the decision tree

    Class parameters:
    parent - father node in the tree
    association - last association decided by parent
    _step_3_score - score of association for step 3
    children - children nodes in the tree
    """

    def __init__(self, parent, current_association, step_3_score_association):
        self.parent = parent
        self.children = []

        self.association = current_association

        self._step_3_score = step_3_score_association

    # TODO: cacher ou pas ?
    @functools.lru_cache(maxsize=None)
    def _create_children(self):
        """Creates choice children"""

        # TODO: déterminer si un skip est possible

        skip_associations = []

        if skip_associations:
            return SkippedChoice(self, skip_associations)

        # TODO: calculer le nombre de noeuds restants
        # TODO: analyser les possibilités et créer les meilleurs fils
        children = []

        return children

    def get_combos(self):
        """Recursively creates children and returns a list of combos created from leaf nodes"""

        self.children = self._create_children()

        if not self.children:
            return Combo(self)

        return [child.get_combos() for child in self.children]

    def get_splited_score(self):
        # TODO: recursion ?
        step_3_scores = {"step_3": self._step_3_score}
        return {**self.association.get_splited_score, **step_3_scores}


class SkippedChoice(Choice):
    def __init__(self, parent, associations_list):
        Choice.__init__(self, parent, associations_list[0], 0)
        self._associations_list = associations_list

    def _create_children(self):
        SkippedChoice(self, self._associations_list[1:])


class Association(Scorable):
    """Storage class regrouping target and audio phonem and associating a step 2 score"""

    def __init__(self, target_phonem, audio_phonem):
        self.target_phonem = target_phonem
        self.audio_phonem = audio_phonem

        # TODO: check et ajouter les autres
        self._same_phonem_score = (
            target_phonem.transcription == audio_phonem.transcription
        ) * params.SCORE_SAME_TRANSCRIPTION

        self._same_word_score = (
            tp.are_token_homophones(
                target_phonem.word.token, audio_phonem.word.token
            )
            * params.SCORE_SAME_AUDIO_WORD
        )

    def get_splited_score(self):
        step_2_scores = {
            "same_phonem": self._same_phonem_score,
            "same_word": self._same_word_score,
        }
        return {**self.audio_phonem.get_splited_score(), **step_2_scores}


class Combo:
    """Represents a complete combo"""

    def __init__(self, leaf_choice):
        self.leaf_choice = leaf_choice
