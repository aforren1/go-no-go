
import glob
import os
from collections import OrderedDict
from warnings import warn
import csv
from ast import literal_eval

from pip._vendor import pytoml as toml

from .blessed_gen import Blessed, Fixed, Normal, TgtColumn, Uniform, Choice, Criterion, PiecewiseUniform, NonzeroNormal, NonzeroUniform


def resolve_settings(recipe_path, default_path='settingsstuff/defaults/'):
    defaults = {}
    # load default recipe for left_right (example)
    for fn in glob.glob(default_path + '*.toml'):
        with open(fn) as f:
            defaults.update(toml.load(f))

    # load overridden version
    # seems like the order matters, not particular keys
    with open(recipe_path) as f:
        dat_over = toml.load(f)

    # join default recipe with overridden version,
    # keeping the changes from the overridden
    out_dict = OrderedDict()

    for key in dat_over.keys():
        dat_over[key]['block_key'] = key
        exp_name = dat_over[key]['name']
        if exp_name not in defaults.keys():
            # no defaults available, terminate early
            raise ValueError('Defaults not found for experiment %s, is there a name key?' % key)
        out_dict[key] = defaults[exp_name].copy()
        # override defaults now
        out_dict[key].update(dat_over[key])

    # convert to list for consumption (dictionary version is less convenient)
    out_dict = list(out_dict.values())
    proto_block = []  # what we actually return (list of settings dicts)

    # generate all the trial tables now, based off settings
    # pull locals (or globals? maybe if this ends up being a function)
    locs = globals()
    loc_keys = locs.keys()
    filename = None  # set to None by default, and only fill in if the key is there
    name = None
    trials = None
    for block_num, block in enumerate(out_dict):
        out_set = {}
        for key in block:
            setting = block[key]  # retrieve the value
            if key.lower() == 'file':
                filename = setting  # process file last
            elif key.lower() == 'trials':
                # trials may be overridden by file later
                trials = setting
            elif key.lower() == 'name':
                # name needs no gen
                name = setting
                out_set['name'] = name
            elif key.lower() == 'multi':
                # multi-setting generator
                pass
            # if dictionary, then we have a {fun: 'function', kwargs: {foo...}} setup
            elif isinstance(setting, dict):
                # we'll be strict about this sort of thing for now
                if 'fun' not in setting.keys():
                    raise ValueError("""For fancy generators, the blessed class must be specified in `fun`.""")
                blessed_gen_name = setting['fun']
                lowkeys = [l.lower() for l in loc_keys]
                # retrieve the blessed generator
                # a little tricky b/c we try not to enforce matching case
                try:
                    blessed_gen = next(locs[x] for x in loc_keys if x.lower() == blessed_gen_name.lower())
                except StopIteration:
                    raise ValueError('Specified generator "%s" not amongst the Blessed.' % blessed_gen_name)
                # we don't strictly *need* kwargs, but tell the user it may be funky
                try:
                    kwargs = setting['kwargs']
                except KeyError:
                    warn('No kwargs found for %s, may fail?' % blessed_gen_name)
                    kwargs = {}
                # TODO: append frame period, number of trials to kwargs here?
                # We don't instantiate just yet; we let the BlockHandler do that
                # doing it later lets us overwrite things that files may nuke, like
                # number of trials
                # we also need to give kwargs all the shared lists
                out_set[key.lower()] = (blessed_gen, kwargs)
            else:  # some sort of scalar
                out_set[key.lower()] = (Fixed, {'value': setting})

        if name is None:
            raise ValueError('Must specify the name of the experiment.')
        # done processing all generators, stuff
        # now if we have a file, use that to modify number of trials & overwrite redundant things
        if filename is not None:
            # fancy pants stuff for file import
            fn, extension = os.path.splitext(filename)
            if extension != '.csv':
                warn(('If file in block %i is a not a csv, further steps may fail '
                      '(Unless this file *is* comma separated).') % block_num)

            datafile = read_csv(filename)  # try to read the file (using our own csv machinery, not pandas)
            # TODO: is there a way to verify datafile.keys?
            # I suppose later in the process we can check against the settings
            # the experiment is expecting
            for key in datafile.keys():
                # even if the key already exists, we'll nuke it
                out_set[key.lower()] = (TgtColumn, {'column': datafile[key]})
                trials = len(datafile[key])
        if trials is None:
            warn(('I recommend setting the number of trials either directly in the TOML '
                  'file or indirectly by specifying a `file` key. '
                  'Setting trials to be 10, tops. '
                  'This warning was for block %i.' % block_num))
            trials = 10
        out_set['trials'] = trials
        block['trials'] = trials  # update plain dict
        proto_block.append(out_set)
    # now we should have {'key': (GenClass, kwargs)} per block
    # again, we delay instantiation so that we can plug in shared lists
    return proto_block, out_dict


def read_csv(filename):
    with open(filename, 'r') as csf:
        reader = csv.DictReader(csf)
        out = {k: [] for k in reader.fieldnames}
        for row in reader:
            for key in row.keys():
                out[key].append(literal_eval(row[key].replace(' ', '')))
    return out


if __name__ == '__main__':
    from pprint import pprint
    from gonogo.settings.block_handler import BlockHandler
    from gonogo.settings.resolve import resolve_settings
    xx, out_dict = resolve_settings('recipes/test_specific.toml', 'recipes/defaults/')
    # part2 is instantiating everything
    block_handlers = [BlockHandler(x, out_dict) for x in xx]
