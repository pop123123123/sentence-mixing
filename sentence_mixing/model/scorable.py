import functools


class Scorable:
    """Interface implemented by all the objects that carry a score"""

    @functools.lru_cache(maxsize=None)
    def get_total_score(self):
        """Computes final score for a storable"""

        scores = self.get_split_score()
        return sum(scores.values())

    @functools.lru_cache(maxsize=None)
    def get_split_score(self):
        """Cached and public version"""
        return self._get_split_score()

    def _get_split_score(self):
        """Retrieves dict stored detailed score"""

        raise NotImplementedError()
