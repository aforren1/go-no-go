# TODO: switch to GLFW so we don't have to go through this
# Pyglet calls some fixed-function OpenGL stuff on creation,
# which leads to an error with a core context. We need to
# disable error checking in the other GL interfaces we interact
# with (pyglet for windowing, pyopengl for IMGUI)
try:  # numpy >= 1.17.0, for the sake of pyinstaller
    # https://github.com/numpy/numpy/issues/14163
    import numpy.random.entropy
    import numpy.random.bounded_integers
    import numpy.random.common
except ModuleNotFoundError:
    pass
import os
import sys

import OpenGL
import pyglet

OpenGL.ERROR_CHECKING = False
pyglet.options['debug_gl'] = False

# figure out if we're a script or exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)
else:
    raise ValueError('No idea if this is running as a script or under pyinstaller!')

if __name__ == '__main__':
    from multiprocessing import freeze_support
    import os
    import shutil
    import sys
    from hashlib import md5
    import platform
    import json
    import hid
    from datetime import datetime
    from serial.tools import list_ports
    from warnings import warn
    from inspect import isclass
    from pkg_resources import get_distribution
    from gonogo.visuals.window import ExpWindow as Window
    from gonogo.scenes.loading import Loading
    from gonogo.settings.block_handler import BlockHandler
    from gonogo.settings.resolve import resolve_settings
    # must import implemented blocks here
    from gonogo.scenes import *
    from gonogo.utils import camel_to_snake, snake_to_camel, rush
    from gonogo.scenes.done import Done
    from gonogo import __version__

    from toon.input import MpDevice, mono_clock
    from gonogo.devices.custom import Custom
    from gonogo.devices.keyboard import Keyboard
    import pip._vendor.pytoml as toml

    # first, we'll get a window + context up ASAP
    # this takes a certain amount of time (~750-1000ms)
    freeze_support()  # TODO: can this just live somewhere in toon?
    can_rush = rush(True)  # test if rush will have an effect
    rush(False)
    win = Window()

    # instantiate the device
    hids = any([e['vendor_id'] == 0x16c0 for e in hid.enumerate()])
    ports = list_ports.comports()
    serials = next((p.device for p in ports if p.pid == 1155),
                   None)  # M$ calls it a microsoft device
    if not hids and serials is None:
        warn('Special device not attached, falling back to keyboard.')
        device = MpDevice(Keyboard(keys=['k', 'l'], clock=mono_clock.get_time))
        device_type = 'keyboard'
    else:
        device = MpDevice(Custom(clock=mono_clock.get_time))
        device_type = 'custom'

    # next, we'll pull up the IMGUI dialog window to get
    # the subject ID, language (EN/ES),
    recipe_dir = os.path.join(application_path, 'recipes/')
    loading = Loading(win, recipe_dir=recipe_dir, can_rush=can_rush)
    user_settings = loading.run(device, device_type)
    win._win.set_exclusive_mouse(True)
    win._win.set_mouse_visible(False)
    user_settings['device_type'] = device_type

    # user_settings is a dictionary with (TODO: fix/change):
    # 1. `id`: participant id (TODO: should we sanitize this more? strip whitespace, lowercase, ...)
    # 2. `recipe`: TOML file which specifies the order of events
    # 3. `recipe_dir`: source of recipes (will fix)
    # 4. `spanish`: translate subsequent instructions to spanish?
    # 5. `data_dir`: location of saved data (ends up being data_dir/subject/*)
    # TODO: we'll fix the spots now, see block.py for getting path to application
    # defaults should be in 'recipes/defaults/'
    user_settings['recipe_dir'] = recipe_dir
    user_settings['data_dir'] = os.path.join(application_path, 'data/')

    # dump the recipe into a folder
    now = datetime.now().strftime('%y%m%d_%H%M%S')
    user_settings['datetime'] = now
    subj_path = os.path.join(user_settings['data_dir'], user_settings['id'],
                             'blocks_' + now)
    user_settings['subj_path'] = subj_path
    # this shouldn't exist yet, as this date & time have never existed
    os.makedirs(subj_path)
    # copy the recipe file directly to the base path
    shutil.copy2(user_settings['recipe'], subj_path)
    # now make a json copy
    with open(user_settings['recipe'], 'r') as f:
        dct = toml.load(f)
    strip_name = os.path.splitext(os.path.basename(user_settings['recipe']))[0]
    json_name = os.path.join(subj_path, strip_name)
    with open(json_name + '.json', 'w+') as f:
        json.dump(dct, f, indent=2)

    # write the recipe-level settings file
    dct_md5 = md5(json.dumps(dct).encode('utf-8')).hexdigest()
    recipe_level_sets = {
        'recipe_md5': dct_md5,
        'os': platform.platform(),
        'py_version': platform.python_version(),
        'rush_allowed': can_rush,
        'fps': int(1/win.frame_period),
        'gpu': win.context.info['GL_RENDERER'],
        'device': device_type,
        'language': user_settings['spanish'],
        'drop_version': __version__
    }
    set_name = os.path.join(subj_path, 'settings.json')
    with open(set_name, 'w+') as f:
        json.dump(recipe_level_sets, f, indent=2)

    # make BlockHandlers for every block specified
    default_recipes = os.path.join(user_settings['recipe_dir'], 'defaults/')
    # resolved is the proto-block-handler, resolved_dict is the plain list of
    # dictionaries that can be re-saved to a file somewhere
    bh_material, resolved_dict = resolve_settings(user_settings['recipe'], default_recipes)

    # part 2: usable block_handlers
    block_handlers = [BlockHandler(x, y) for x, y in zip(bh_material, resolved_dict)]

    # instantiate all blocks being used so we can get the slow stuff out of the way
    block_dict = {}
    # find experiments that have been imported
    lc = locals()
    existing_exps = {k: lc[k] for k in lc.keys() if isclass(lc[k]) and issubclass(lc[k], Block)}
    del existing_exps['Block']  # remove the base class

    # NOW we do the instantiation
    blocks = []
    tot = len(block_handlers)
    for count, bh in enumerate(block_handlers):
        # extract the class
        stc = snake_to_camel(bh.name)
        exp_cls = existing_exps[stc]
        prac_cls = lc[stc + 'Instr']
        # instantiate the classes (one for instructions, one for block)
        blocks.append(prac_cls(win, bh, device, user_settings, number=count+1, total=tot))
        blocks.append(exp_cls(win, bh, device, user_settings))

    done = Done(win)
    for block in blocks:
        win._win.set_mouse_position(-2, -2)
        block.run()
    # parting words (final scores, encouraging words, ...)

    done.run()
    win.close()
