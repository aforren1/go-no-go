
from . blessed_gen import Blessed
# generational_values is dictionary of key: (Blessed, kwarg) pairs
# Blessed are not yet instantiated


class BlockHandler(object):
    def __init__(self, blessed_dict, plain_dict, general_settings=None):
        # trials sets the upper bound of number of trials
        # TODO: does block_settings do any work??
        bdict = blessed_dict.copy()
        self.text_dict = plain_dict
        self.keys = blessed_dict.keys()
        self.general_settings = [] if general_settings is None else general_settings
        self.block_settings = []
        self.user_data = []
        self.previous_trials = []
        self.counter = 0
        self.trials = None  # should be set by blessed_dict
        self.name = ''  # should be set by blessed_dict
        self.any_dynamic = False  # shortcut to see if we should check adaptive processes
        # all adaptive processes are currently "soft", in that they wait until
        # *all* other adaptive processes are finished until terminating

        for key in bdict.keys():
            bdkey = bdict[key]
            if isinstance(bdkey, tuple) and issubclass(bdkey[0], Blessed):
                blessed_gen = bdkey[0]
                blessed_kwargs = bdkey[1]
                bdict[key] = blessed_gen(general_settings=self.general_settings,
                                         block_settings=self.block_settings,
                                         user_data=self.user_data,
                                         previous_trials=self.previous_trials,
                                         **blessed_kwargs)
                if bdict[key].dynamic:
                    self.any_dynamic = True
            # deal with special magic values
            elif key in ['name', 'trials']:
                setattr(self, key, bdkey)
        for key in ['name', 'trials']:
            bdict.pop(key, None)
        self.trial_by_trial_settings = bdict

    def next(self):
        # generate the next dictionary, and store a copy in previous_trials
        output = {}
        tbts = self.trial_by_trial_settings
        for key in tbts:
            output[key] = tbts[key].next()

        self.previous_trials.append(output.copy())
        self.counter += 1
        return output

    def update_user_data(self, user_dict: dict):
        self.user_data.append(user_dict.copy())

    def should_finish(self):
        # first, if we've exceeded the number of
        # trials, terminate regardless
        if self.counter >= self.trials:
            return True
        # otherwise, check to see if all dynamic
        # ones are satisfied
        if self.any_dynamic:
            tbts = self.trial_by_trial_settings
            for key in tbts:
                if tbts[key].dynamic:
                    if not tbts[key].should_finish():
                        return False
            return True
        return False

# should go in this order:
# init()
# while True:
#     next()
#     update_user_data()
#     should_finish()
