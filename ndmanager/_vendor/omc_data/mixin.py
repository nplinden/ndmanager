import numpy as np



class EqualityMixin:
    """A Class which provides a generic __eq__ method that can be inherited
    by downstream classes.
    """

    def __eq__(self, other):
        if isinstance(other, type(self)):
            for key, value in self.__dict__.items():
                if isinstance(value, np.ndarray):
                    if not np.array_equal(value, other.__dict__.get(key)):
                        return False
                else:
                    return value == other.__dict__.get(key)
        else:
            return False

        return True
