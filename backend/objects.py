import numpy as np

MAX_COORDINATE = 16

class BaseObject:
    """
    Базовый объект, который представляет из себя программу
    """
    def TikZ(self):
        """
        :return: строку-программу в TikZ формате
        """
        return "\n".join(self.evaluate())

    def noisyTikZ(self):
        """
        :return: строку-программу в TikZ формате
        """
        return "\n".join(self.noisyEvaluate())

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return str(self)

    def __ne__(self, other):
        return str(self) != str(other)