# blessed generators
# RNG seed should be set per element, not globally (so there's not
# perfect correspondence between two gaussians, e.g.)
import numpy as np
from numpy.random import RandomState


class Blessed(object):

    def __init_subclass__(cls, dynamic=False, **kwargs):
        # only dynamic ones will be checked for completion
        super().__init_subclass__(**kwargs)
        cls.dynamic = dynamic

    def __init__(self, seed=1, general_settings=[], block_settings=[], user_data=[], previous_trials=[]):
        # general settings are settings like
        # user_data and previous_trials are lists directly
        # shared with the BlockHandler (i.e. a "reference"),
        # where these are actually updated
        self.rng = RandomState(seed)
        self.general_settings = general_settings
        self.block_settings = block_settings
        self.user_data = user_data
        self.previous_trials = previous_trials

    def next(self):
        # return the next value from the generator
        pass


class Fixed(Blessed):
    def __init__(self, value, **kwargs):
        super().__init__(**kwargs)
        self.value = value

    def next(self):
        return self.value


class Uniform(Blessed):
    def __init__(self, low, high, **kwargs):
        super().__init__(**kwargs)
        self.low, self.high = low, high

    def next(self):
        return self.rng.uniform(self.low, self.high, None)


class NonzeroUniform(Uniform):
    def next(self):
        proposed = 0
        count = 0
        while proposed == 0:
            proposed = self.rng.uniform(self.low, self.high, None)
            count += 1
            if count > 100:
                raise ValueError('Too many iterations.')
        return proposed


class Normal(Blessed):
    def __init__(self, loc, scale, **kwargs):
        super().__init__(**kwargs)
        self.loc, self.scale = loc, scale

    def next(self):
        return self.rng.normal(self.loc, self.scale, None)


class NonzeroNormal(Normal):
    def next(self):
        proposed = 0
        count = 0
        while proposed == 0:
            proposed = self.rng.normal(self.loc, self.scale, None)
            count += 1
            if count > 100:
                raise ValueError('Too many iterations.')
        return proposed


class Choice(Blessed):
    def __init__(self, options, probs, **kwargs):
        super().__init__(**kwargs)
        self.options, self.probs = options, probs

    def next(self):
        return self.rng.choice(self.options, p=self.probs)

# was thinking about making this a 'dynamic'
# one (so that it fits in with the other
# early termination ones), but I think
# it should just set the number of trials
# elsewhere and remain fixed


class TgtColumn(Blessed):
    def __init__(self, column, **kwargs):
        super().__init__(**kwargs)
        self.counter = 0
        self.column = column

    def next(self):
        row = self.column[self.counter]
        self.counter += 1
        return row


class Criterion(Blessed, dynamic=True):
    def __init__(self, values=[0.75, 0.5], consecutive=4, **kwargs):
        super().__init__(**kwargs)
        self.consecutive = consecutive  # consecutive correct expected
        self.index = 0  # which t_max to read from
        self.counter = 0
        try:
            iter(values)
        except TypeError:
            raise ValueError('t_max should be iterable (e.g. a list)')
        self.values = values

    def next(self):
        return self.values[self.index]

    def should_finish(self):
        # last n correct
        if self.user_data and self.user_data[-1]['correct_choice']:
            self.counter += 1
        else:
            self.counter = 0
        if self.counter >= self.consecutive:
            self.index += 1
            self.counter = 0
        return self.index >= len(self.values)


class PiecewiseUniform(Blessed):
    # breaks[0] is lower bound, breaks[-1] is upper bound
    # len(probs) = len(breaks) - 1 pieces
    # include on lower bound, exclude on upper bound: [0.05, 0.1)
    def __init__(self, breaks=[0.05, 0.1, 0.35, 0.5], probs=[0.1, 0.7, 0.2],
                 **kwargs):
        if len(breaks) - 1 != len(probs):
            raise ValueError('`probs` should be of length n-1, where n = len(breaks).')
        if sum(probs) != 1:
            raise ValueError('`probs` should sum to 1.')
        super().__init__(**kwargs)
        self.intervals = [[breaks[i], breaks[i + 1]] for i in range(len(breaks) - 1)]
        self.probs = probs

    def next(self):
        # first, pick the interval
        interval_choice = self.rng.choice(len(self.intervals), p=self.probs)
        # then generate value
        interval = self.intervals[interval_choice]
        return self.rng.uniform(low=interval[0], high=interval[1])
