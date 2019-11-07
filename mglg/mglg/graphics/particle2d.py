# https://github.com/moderngl/moderngl/blob/master/examples/particle_system.py
import numpy as np
import moderngl as mgl
from mglg.graphics.camera import Camera
from mglg.graphics.drawable import Drawable2D


def random_on_circle(radius, size):
    r = radius * np.sqrt(np.random.uniform(0, 1, size=size))
    theta = np.random.uniform(0, 2*np.pi, size=size)
    return r, theta

# TODO: GL_STREAM_COPY?


class ParticleBurst2D(Drawable2D):
    # make sure to set scale in the init, else the initial particle positiions will
    # be pretty wild...

    # three buffers-- one for the initial state,
    # two for doing computation
    # one buffer for static things (size, color)
    # I think this sort of thing is called "transform feedback"
    def __init__(self, context: mgl.Context, shader,
                 num_particles=1e5, *args, **kwargs):
        super().__init__(context, shader, *args, **kwargs)
        self.context = context  # we need to keep a reference to the shader around
        # for copying buffers & whatnot
        self._tracker = 1.0
        num_particles = int(num_particles)
        self.num_particles = num_particles
        color_size = np.zeros(num_particles, dtype=[('color_size', np.float32, 4)])
        # first three elements are RGB, last one is particle (i.e. GL_POINT) size
        # this is static, and we don't need to do any extra computations
        color_size['color_size'][:, 0] = np.random.uniform(0.9, 1.0, num_particles)
        color_size['color_size'][:, 1] = np.random.uniform(0.0, 1.0, num_particles)
        color_size['color_size'][:, 2] = np.random.uniform(0.0, 0.1, num_particles)
        color_size['color_size'][:, 3] = np.random.uniform(0.1, 4.0, num_particles)

        # first three elements are vertex XYZ, last one is alpha
        # think about this-- should we just delay until ready to draw the first time?
        # if the scale isn't set immediately, then end up with garbage?
        pos_alpha = np.zeros(num_particles, dtype=[('vertices_alpha', np.float32, 8)])
        r, theta = random_on_circle(self.scale.y * 0.2, num_particles)
        pos_alpha['vertices_alpha'][:, 0:2] = np.array([np.cos(theta) * r, np.sin(theta) * r]).T
        pos_alpha['vertices_alpha'][:, 3] = np.random.uniform(0.5, 1.0, num_particles)
        # it looks like the moderngl example allocates 2x the amount, so the first 4
        # are from the current timestep and the last 4 are from the previous timestep
        # then during rendering, the previous timestep is ignored (treated as padding)

        r_accel, theta_accel = random_on_circle(0.08, self.num_particles)

        accel = np.zeros(num_particles, dtype=[('accel', np.float32, 4)])
        accel['accel'][:, :2] = np.array([r_accel * np.cos(theta_accel),
                                          r_accel * np.sin(theta_accel)]).T
        accel = context.buffer(accel.view(np.ubyte))
        # vbo_render is what ends up being rendered
        # vbo_trans is an intermediary for transform feedback
        # vbo_orig is the original state, which we use to "reset" the explosion
        # without writing new data to the GPU
        color_size2 = context.buffer(color_size.view(np.ubyte))
        self.vbo_render = context.buffer(pos_alpha.view(np.ubyte))
        self.vbo_trans = context.buffer(reserve=self.vbo_render.size)
        self.vbo_orig = context.buffer(reserve=self.vbo_render.size)

        self.vao_trans = context.vertex_array(shader.transform,
                                              [
                                                  (self.vbo_render, '4f 4f', 'in_pos_alpha', 'in_prev_pos_alpha'),
                                                  (accel, '4f', 'accel')
                                              ])
        # self.vao_trans = context.simple_vertex_array(..., self.vbo_trans, ???)
        self.vao_render = context.vertex_array(shader.render,
                                               [
                                                   (self.vbo_render, '4f 4x4', 'vertices_alpha'),
                                                   (color_size2, '4f', 'color_size')
                                               ])
        # set the data of the original state
        context.copy_buffer(self.vbo_orig, self.vbo_render)
        context.point_size = 2.0  # TODO: set point size as intended

    def draw(self, camera: Camera):
        if self.visible:
            self._tracker -= 0.012  # at some point, change to invisible so we don't do excess work
            if self._tracker < 0:
                self.visible = False
            np.dot(self.model_matrix, camera.vp, self.mvp)
            self.shader.render['mvp'].write(self._mvp_ubyte_view)
            # update particles
            self.vao_trans.transform(self.vbo_trans, mgl.POINTS)
            # copy transformed data
            self.context.copy_buffer(self.vbo_render, self.vbo_trans)
            # draw
            self.vao_render.render(mgl.POINTS)

    def reset(self):
        # TODO: to get a non-totally-repeating effect, rotate the particles by n degrees
        self.context.copy_buffer(self.vbo_render, self.vbo_orig)  # dest, src
        self._tracker = 1.0
