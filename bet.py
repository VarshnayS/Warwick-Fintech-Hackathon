import whalescore

class Bet:
    def __init__(self, id, question, volume, startDate, compute_speculation=True):
        self.id = id
        self.question = question
        self.volume = volume
        self.startDate = startDate

                # analytics fields
        self.speculation_ratio = None
        self.whale_ratio = None

        self.getWhale()

        if compute_speculation:
            self.compute_speculation_ratio()

    def compute_speculation_ratio(self):
        """
        Lazy import to avoid circular dependencies
        """
        try:
            from speculation import find_single_speculation_ratio
            self.speculation_ratio = find_single_speculation_ratio(self)
        except Exception:
            self.speculation_ratio = None

    def getWhale(self):
        self.whale_ratio = whalescore.single_whale_ratio(self.id)