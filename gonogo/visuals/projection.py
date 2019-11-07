import math
import numpy as np


def ortho(left, right, bottom, top, znear, zfar):
    """From glumpy project.
    Create orthographic projection matrix

    Parameters
    ----------
    left : float
        Left coordinate of the field of view.
    right : float
        Right coordinate of the field of view.
    bottom : float
        Bottom coordinate of the field of view.
    top : float
        Top coordinate of the field of view.
    znear : float
        Near coordinate of the field of view.
    zfar : float
        Far coordinate of the field of view.

    Returns
    -------
    M : array
        Orthographic projection matrix (4x4).
    """
    assert(right != left)
    assert(bottom != top)
    assert(znear != zfar)

    M = np.zeros((4, 4), dtype=np.float32)
    M[0, 0] = +2.0 / (right - left)
    M[3, 0] = -(right + left) / float(right - left)
    M[1, 1] = +2.0 / (top - bottom)
    M[3, 1] = -(top + bottom) / float(top - bottom)
    M[2, 2] = -2.0 / (zfar - znear)
    M[3, 2] = -(zfar + znear) / float(zfar - znear)
    M[3, 3] = 1.0
    return M


def height_ortho(width, height):
    # width & height should be in pixels (width & height of fullscreen)
    xmin, xmax = -0.5, 0.5
    ymin, ymax = -0.5, 0.5

    # aspect fixed to 1
    xmin /= height/width
    xmax /= height/width

    znear = -1000
    zfar = 1000
    return ortho(xmin, xmax, ymin, ymax, znear, zfar)
