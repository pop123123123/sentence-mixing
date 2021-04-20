import random

import sentence_mixing.logic.parameters as params
import sentence_mixing.sentence_mixer as sm

class Randomizer():
    """
    This classe's role is to isolate random generation flow from the module and
    to associate it to a particular execution of process_sm() function.
    This is mandatory to guarantee determinism in case of parallel execution
    of process_sm() or in case of external usage of random module.

    At the begining of the library's usage, get_videos() is called and ccreates
    a random.Random object giving a seed. This random.Random object is called
    sm.GET_VIDEOS_RANDOM. After the call of get_videos(), GET_VIDEOS_RANDOM
    is never used again.
    We then use this global module common variable as a basis for all the
    random operation done in the future-called process_sm().
    GET_VIDEOS_RANDOM is then just a snapshot of the random generation flow
    after the execution of get_videos().
    """

    def __init__(self, rand=None):
        """
        Initiates the Randomizer

        Arguments:
        rand - if the Randomizer is created at the begining of get_video, it
               simply uses the global GET_VIDEO_RANDOM random.Random object.
               Otherwise, it creates a new random.Random object taking the
               state of GET_VIDEO_RANDOM.
        """
        if rand is not None:
            self.rand = rand
        else:
            self.rand = random.Random()
            self.rand.setstate(sm.GET_VIDEO_RANDOM.getstate())

    def noise_score(self, base_score, sigma=None):
        """
        Adds a gaussian noise on a given score

        Arguments:
        base_score - mean of gaussian score
        sigma - variance of gaussian score. Default is 1/5 of base_score
        """

        if not sigma:
            sigma = base_score * 0.2

        return self.rand.gauss(base_score, sigma)


    def random_basic_score(self):
        """Returns a random basic score following an gaussian distribution"""

        return self.rand.gauss(0, params.RANDOM_SPAN)
