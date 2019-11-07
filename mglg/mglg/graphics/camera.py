import numpy as np

# TODO: not very useful right now, but could be moveable in the future


class Camera(object):
    def __init__(self, view=np.eye(4, dtype=np.float32), projection=None):
        self.vp = np.dot(view, projection).astype(np.float32)
