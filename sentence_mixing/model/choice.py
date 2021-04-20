import functools

import sentence_mixing.logic.analyze
import sentence_mixing.logic.analyze_step_3 as step_3
import sentence_mixing.logic.parameters as params
from sentence_mixing.model.scorable import Scorable


class Choice(Scorable):
    """
    This class represents a node in the decision tree.

    Also contains a step 3 score, rating the association comparatively to all parent associations.

    Class attributes:
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
        audio_spectral_score,
        audio_amplitude_score,
        previous_score,
        randomizer,
    ):
        self.parent = parent
        self.nodes_left = nodes_left
        self.children = []

        self.association = current_association

        self._audio_spectral_score = audio_spectral_score
        self._audio_amplitude_score = audio_amplitude_score
        self._previous_score = previous_score

        self.randomizer = randomizer

    def get_self_and_previous_choices(self):
        """This is a generator used to retrieve the current Choice and all its parents"""

        choice = self
        while choice is not None:
            yield choice
            choice = choice.parent

    @functools.lru_cache(maxsize=None)
    def _create_children(self):
        """
        Creates choice children
        This function is decomposed in two parts:
        -skip checking
        -normal workflow

        Skip checking:
            First, it tries to spot if an homophonous word sequence matching target can be found
            from the current audio phonem.

            If a skip occurs, the function creates SkippedChoice typed children instead of regular
            Choice typed children.

            Example:
                -TargetSentence: "Les <BLANK> puissances <BLANK> de"
                -In the audio subtitles, you can find "puissance deux"
                -self.assocation = ['p', 'p']

                The function, by checking the audio words followed by audio phonem 'p', will spot
                a two consecutives homophones sequence, common in target and audio:
                "puissances de" for target and "puissance deux" for audio.

                These two sequences are considered as homophones because they contains strictly
                the same phonems. Please note that <BLANK> token is skipped while looking for
                word sequence (check the functionlogic.utils.get_sequence() for more details).

                The function will then force the choice all the phonems of "puissance de" by
                SkippedChoice children.


            Then, it applies the same logic for identical phonem sequences.
            A common sequence ends at the end of the current word.

            Example:
                -TargetSentence: "Ma <BLANK> trique <BLANK> sauce"
                -In audio subtitles, you can find the word "géométrique saucisse"
                -self.association = ['t', 't']

                The function will check if a common phonem sequence can be found between audio and
                target phonem.
                It will find a common sequence, starting from current audio and target phonem 't':
                phonems 't', 'r', 'i', 'k' ("trique").

                Warning: despite "sauce" and "saucisse" contains common phonems at the begginging
                        ('s', 'o', 's'), it will not be included in previous sequence ("trique"),
                        because it is not part of the same word !

                        Of course, when self.association will contains phonems ['s', 's'], this
                        function will detect the common phonem sequence 's', 'o', 's'.


        Normal workflow:

            If no skip opportunity was found, the function will simply try to get the best
            association for its children.
            Normal workflow is handled by logic.analyze() function. Check it for more details.
        """

        # Leaf child
        if self.association.target_phonem.next_in_seq() is None:
            return []

        # Check for word skipping
        if self.association.target_phonem.get_index_in_word() == 0:
            # Checks homophones basing on the dictionary
            dictionary_homophones_phonems = list(
                self.association.sequence_dictionary_homophones_phonems()
            )
            # Checks homophones basing on audio word's list of phonems
            aligner_homophones_phonems = list(
                self.association.sequence_aligner_homophones_phonems()
            )

            # If at least a one-word-length sequence has be found
            if len(dictionary_homophones_phonems) > 2:
                return [
                    SkippedChoice(
                        self,
                        dictionary_homophones_phonems[1:],
                        self.randomizer,
                    )
                ]
            # If the word sequence contains a word of only two phonem
            elif len(dictionary_homophones_phonems) == 2:
                return [
                    Choice(
                        self,
                        dictionary_homophones_phonems[1],
                        self.nodes_left,
                        *self.compute_child_step_3_score(
                            dictionary_homophones_phonems[1]
                        ),
                        self.randomizer,
                    )
                ]

            # If at least a one-word-length sequence has be found
            elif len(aligner_homophones_phonems) > 2:
                return [
                    SkippedChoice(
                        self, aligner_homophones_phonems[1:], self.randomizer
                    )
                ]
            # If the word sequence contains a word of only two phonem
            elif len(aligner_homophones_phonems) == 2:
                return [
                    Choice(
                        self,
                        aligner_homophones_phonems[1],
                        self.nodes_left,
                        *self.compute_child_step_3_score(
                            aligner_homophones_phonems[1]
                        ),
                        self.randomizer,
                    )
                ]

        # Check for phonem skipping
        same_phonems = (
            self.association.sequence_same_phonems_first_word_truncated()
        )
        # A common phonem sequence has been found
        if len(same_phonems) > 2:
            return [SkippedChoice(self, same_phonems[1:], self.randomizer)]
        elif len(same_phonems) == 2:
            return [
                Choice(
                    self,
                    same_phonems[1],
                    self.nodes_left,
                    *self.compute_child_step_3_score(same_phonems[1]),
                    self.randomizer,
                )
            ]

        # Normal workflow
        target_phonem = self.association.target_phonem.next_in_seq()
        return sentence_mixing.logic.analyze.compute_children(
            target_phonem, self.nodes_left, self, self.randomizer
        )

    def get_combos(self):
        """Recursively creates children and returns a list of combos created from leaf nodes"""

        self.children = self._create_children()

        if len(self.children) == 0:
            return [Combo(self)]

        return sum((child.get_combos() for child in self.children), [])

    def _get_split_score(self):
        step_3_scores = {
            "step_3_audio_spectral": self._audio_spectral_score,
            "step_3_audio_amplitude": self._audio_amplitude_score,
            "step_3_same_word_previous_phonems": self._previous_score,
        }
        return {**self.association.get_split_score(), **step_3_scores}

    def compute_child_step_3_score(self, association):
        """
        Computes step 3 score for a given association.
        This score depends on the previous chosen associations.

        Assume that self has a parent.
        """

        previous_associations = []
        previous_associations.extend(
            c.association for c in self.get_self_and_previous_choices()
        )

        all_associations = [association] + previous_associations

        rate = []

        if association.target_phonem.get_type() == "VOWEL":
            rate.append(
                step_3.step_3_audio_spectral_rating(
                    step_3.get_last_vowel(previous_associations),
                    association.audio_phonem,
                )
                * params.RATING_SPECTRAL_SIMILARITY
            )
        else:
            rate.append(0)

        if association.target_phonem.transcription != "sp":
            rate.append(
                step_3.step_3_audio_amplitude_rating(
                    (previous_associations), association,
                )
                * -params.RATING_AMPLITUDE_DIFFERENCE
            )
        else:
            rate.append(0)

        rate.append(
            params.RATING_LENGTH_SAME_PHONEM
            * step_3.step_3_n_following_previous_phonems(all_associations)
        )

        return rate


class SkippedChoice(Choice):
    """
    This subclass of Choice is used when a skip is performed.
    It represent a filiform portion of the tree.

    For example, if a Choice detected a the following common phonem sequence 't', 'r', 'i', 'k',
    a sequence of 4 SkippedChoice will be created.

    Class attributes:
    _associations_list - stack of all the remaining phonems of the skipped sequence.
                         With the previous example: first SkippedChoice will have association list
                         of 'r', 'i', 'k', second will have 'i', 'k'...
    """

    def __init__(self, parent, associations_list, randomizer):
        Choice.__init__(
            self,
            parent,
            associations_list[0],
            parent.nodes_left,
            *parent.compute_child_step_3_score(associations_list[0]),
            randomizer,
        )
        self._associations_list = associations_list[1:]

    def _create_children(self):
        """
        In opposite to _create_children() method of Choice, _create_children() method of
        SkippedChoice doesn't perform any analyze but only creates a children with the next
        phonem in the skipped sequence (associations_list).

        When the skip is finished (_associations_list is empty): creates a regular Choice
        """

        if len(self._associations_list) > 1:
            return [
                SkippedChoice(self, self._associations_list, self.randomizer)
            ]
        else:
            score = self.compute_child_step_3_score(self._associations_list[0])
            return [
                Choice(
                    self,
                    self._associations_list[0],
                    self.nodes_left,
                    *score,
                    self.randomizer,
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
