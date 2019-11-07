import pyglet
import OpenGL
# disable error checking for the sake of testing individual units
# (but probably needs to be disabled globally very early on)
OpenGL.ERROR_CHECKING = False
pyglet.options['debug_gl'] = False
if True:  # hack to keep things from reordering (& not disabling error checking in time)
    import json
    import imgui
    from pkg_resources import resource_filename
    from imgui.integrations import compute_fb_scale

    from imgui.integrations.pyglet import PygletMixin
    from imgui.integrations.opengl import ProgrammablePipelineRenderer


class ProgrammablePygletRenderer(PygletMixin, ProgrammablePipelineRenderer):
    def __init__(self, window, attach_callbacks=True):
        super(ProgrammablePygletRenderer, self).__init__()
        window_size = window.get_size()
        viewport_size = window.get_viewport_size()

        self.io.display_size = window_size
        self.io.display_fb_scale = compute_fb_scale(window_size, viewport_size)
        # try to scale fonts in high DPI situations
        self.io.font_global_scale = 1.0/self.io.display_fb_scale[0]

        self._map_keys()

        if attach_callbacks:
            window.push_handlers(
                self.on_mouse_motion,
                self.on_key_press,
                self.on_key_release,
                self.on_text,
                self.on_mouse_drag,
                self.on_mouse_press,
                self.on_mouse_release,
                self.on_mouse_scroll,
                self.on_resize,
            )


def apply_style(filename):
    # load a style from JSON file
    style = imgui.get_style()
    with open(filename, 'r') as f:
        loaded = json.load(f)

    for name in dir(style):
        if not name.startswith('__') and not name.startswith('color') and not name.startswith('create'):
            setattr(style, name, loaded[name])

    # set colors
    for name in dir(imgui):
        if name.startswith('COLOR_') and getattr(imgui, name) < imgui.COLOR_COUNT:
            style.colors[getattr(imgui, name)] = loaded['colors'][name]


# shared context
imgui.create_context()

# load style
default_theme = resource_filename('gonogo', 'resources/themes/default.json')
apply_style(default_theme)
