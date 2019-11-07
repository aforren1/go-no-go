
if __name__ == '__main__':
    from gonogo.visuals.imgui_abstractions import imgui, ProgrammablePygletRenderer
    from gonogo.visuals.window import ExpWindow as Win
    from pprint import pprint
    import json

    win = Win()
    impl = ProgrammablePygletRenderer(win._win)

    filename = 'foo.json'
    style = imgui.get_style()

    while True:
        imgui.new_frame()
        imgui.show_style_editor()
        imgui.show_demo_window()
        imgui.set_next_window_size(200, 200)
        imgui.begin('Save dlg')
        imgui.input_text('filename', filename, 256)
        if imgui.button('Save settings', 100, 50):
            dct = {i: getattr(style, i) for i in dir(style) if not i.startswith('__') and not i.startswith('color') and not i.startswith('create')}
            dct['colors'] = {i: style.colors[getattr(imgui, i)] for i in dir(imgui) if i.startswith('COLOR_') and getattr(imgui, i) < imgui.COLOR_COUNT}
            with open(filename, 'w') as f:
                json.dump(dct, f)
            # save to filename

        if imgui.button('Load settings', 100, 50):
            with open(filename, 'r') as f:
                loaded = json.load(f)

            for name in dir(style):
                if not name.startswith('__') and not name.startswith('color') and not name.startswith('create'):
                    setattr(style, name, loaded[name])

            # set colors
            for name in dir(imgui):
                if name.startswith('COLOR_') and getattr(imgui, name) < imgui.COLOR_COUNT:
                    style.colors[getattr(imgui, name)] = loaded['colors'][name]

        imgui.end()
        imgui.render()
        impl.render(imgui.get_draw_data())
        win.flip()
