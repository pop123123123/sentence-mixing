class Scorable:
    """Interface implemented by all the objects that carry a score"""

    def get_total_score(self):
        """Computes final score for a storable"""

        scores = self.get_splited_score()
        return sum(scores.values())

    def get_splited_score(self):
        """Retrieves dict stored detailed score"""

        raise NotImplementedError()

    def set_multiply_factor(factor):
        """Retrieves dict stored detailed score"""
        raise NotImplementedError()
