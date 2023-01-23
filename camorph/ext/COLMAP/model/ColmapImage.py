import numpy as np
from pyquaternion import Quaternion


class ColmapImage:
    img_id: int
    q: Quaternion
    t: np.ndarray
    cam_id: int
    name: str

    def __init__(self, img_id, q, t, cam_id, name):
        self.img_id = img_id
        self.q = q
        self.t = t
        self.cam_id = cam_id
        self.name = name