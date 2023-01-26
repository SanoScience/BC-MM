class Cost:
    def __init__(self, direct: float = 0, indirect_death: float = 0, indirect_others: float = 0):
        self.direct = direct
        self.indirect_death = indirect_death
        self.indirect_others = indirect_others
        self.total = self.direct + self.indirect_death + self.indirect_others

    def __add__(self, other):
        self.direct = self.direct + other.direct
        self.indirect_death = self.indirect_death + other.indirect_death
        self.indirect_others = self.indirect_others + other.indirect_others
        self.total = self.total + other.total
        return self

    def to_dict(self):
        return {
            "DIRECT": self.direct,
            "TOTAL": self.total,
            "INDIRECT_OTHERS": self.indirect_others,
            "INDIRECT_DEATH": self.indirect_death
        }
