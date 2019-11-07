import os.path as op
from timeit import default_timer
import numpy as np
import moderngl as mgl

from drop3.visuals.window import ExpWindow as Win
from drop3.visuals.projection import height_ortho
from mglg.graphics.drawable import DrawableGroup
from mglg.graphics.shaders import FlatShader, ImageShader, ParticleShader, StippleShader, TextShader
from mglg.graphics.shape2d import Square, Circle, Arrow, Polygon, Cross
from mglg.graphics.camera import Camera
from mglg.graphics.image2d import Image2D, texture_cache
from mglg.graphics.particle2d import ParticleBurst2D
from mglg.graphics.stipple2d import StippleArrow
from mglg.graphics.text2d import FontManager, Text2D

win = Win()
ortho = height_ortho(win.width, win.height)
context = mgl.create_context(330)
context.line_width = 3.0
prog = FlatShader(context)
img_prog = ImageShader(context)
part_prog = ParticleShader(context)
stip_prog = StippleShader(context)
text_prog = TextShader(context)

sqr = Square(context, prog, scale=(0.15, 0.1), fill_color=(0.7, 0.9, 0.2, 1), rotation=45)
circle = Circle(context, prog, scale=(0.15, 0.1), fill_color=(0.2, 0.9, 0.7, 1))
arrow = Arrow(context, prog, scale=(0.15, 0.1), fill_color=(0.9, 0.7, 0.2, 1))
circle.position.x += 0.2
arrow.position.x -= 0.2
sqr2 = Square(context, prog, scale=(0.05, 0.05), fill_color=(0.1, 0.1, 0.1, 0.6))
poly = Polygon(context, prog, segments=7, scale=(0.08, 0.08), position=(-0.2, -0.2),
               fill_color=(0.9, 0.2, 0.2, 0.5), outline_color=(0.1, 0.1, 0.1, 1))
crs = Cross(context, prog, fill_color=(0.2, 0.1, 0.9, 0.7), is_outlined=False,
            scale=(0.12, 0.10), position=(0.3, 0.3))

check_path = op.join(op.dirname(__file__), 'check_small.png')
check = Image2D(context, img_prog, check_path, position=(-0.2, 0.3),
                scale=(0.1, 0.1), rotation=70)

check2 = Image2D(context, img_prog, check_path, position=(0.5, 0),
                 scale=(0.05, 0.05), rotation=0)
print(texture_cache)
# check that they *do* share the same vertex buffer
assert sqr.vao_fill == sqr2.vao_fill

particles = ParticleBurst2D(context, part_prog, scale=(0.025, 0.025), num_particles=1e5)

stiparrow = StippleArrow(context, stip_prog, win.width, win.height, scale=(0.1, 0.1),
                         position=(0.2, -0.3), pattern=0xadfa)

# bump up font size for crisper look
font_path = op.join(op.dirname(__file__), 'UbuntuMono-B.ttf')
font = FontManager.get(font_path, size=128)
bases = Text2D(context, text_prog, win.width, win.height,
               scale=(0.1, 0.1), color=(1, 0.1, 0.1, 0.7),
               text='\u2620Tengo un gatito pequeñito\u2620', font=font, position=(0, -0.4))
bases2 = Text2D(context, text_prog, win.width, win.height,
                scale=(0.05, 0.05), color=(0.1, 1, 0.1, 1),
                text='\u2611pequeño\u2611', font=font, position=(-0.4, 0), rotation=90)

dg = DrawableGroup([sqr, sqr2, circle, arrow, poly, crs])
pix = DrawableGroup([check, check2])
prt = DrawableGroup([particles])
stp = DrawableGroup([stiparrow])
txt = DrawableGroup([bases, bases2])

cam = Camera(projection=ortho)

counter = 0
vals = []
for i in range(300):
    counter += 2
    sqr2.position.xy = np.sin(counter/200)/2
    sqr2.rotation = counter
    sqr.rotation = -counter
    arrow.rotation = counter
    circle.rotation = counter
    stiparrow.rotation = -counter
    if not particles.visible:
        particles.reset()
        particles.visible = True
    t0 = default_timer()
    dg.draw(cam)
    pix.draw(cam)
    prt.draw(cam)
    stp.draw(cam)
    txt.draw(cam)
    vals.append(default_timer() - t0)
    win.flip()
    if win.dt > 0.03:
        print(win.dt)

win.close()
#fix, ax = plt.subplots(tight_layout=True)
# ax.hist(vals)
# plt.show()
print('mean: %f, std: %f' % (np.mean(vals), np.std(vals)))
