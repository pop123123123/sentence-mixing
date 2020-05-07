class Scorable:
    """Interface implemented by all the objects that carry a score"""

    def get_total_score(self):
        """Computes final score for a storable"""

        scores = self.get_splited_score()
        return sum([score for _, score in scores.items()])

    def get_splited_score(self):
        """Retrieves dict stored detailed score"""

        raise NotImplementedError()
