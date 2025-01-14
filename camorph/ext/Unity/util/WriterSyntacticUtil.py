import itertools
import re

import yaml
import numpy as np

from ..model.UnityCamera import UnityCamera
from ..model.UnityGameObject import UnityGameObject
from ..model.UnityTransform import UnityTransform
from camorph.lib.model.Camera import Camera


def build_file(cam_array: list[Camera]):
    out_game_objs = []
    out_cams = []
    out_transforms = []
    out_txt = "%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n"
    id_gen = itertools.count(1)
    for cam in cam_array:
        gid = next(id_gen)
        cid = next(id_gen)
        tid = next(id_gen)
        u_game_obj = UnityGameObject(gid, cid, tid, cam.name)
        u_cam = UnityCamera(cid, gid, cam.focal_length_mm[0], cam.sensor_size, float(np.degrees(cam.fov[0])), cam.projection_type)
        u_transform = UnityTransform(cam.t, cam.r, tid, gid)
        out_game_objs.append(dict(GameObject=u_game_obj))
        out_cams.append(dict(Camera=u_cam))
        out_transforms.append(dict(Transform=u_transform))
    out_txt += yaml.dump(out_game_objs, default_flow_style=None)
    out_txt += (yaml.dump(out_cams))
    out_txt += (yaml.dump(out_transforms))
    out_txt = re.sub(r" {4}", "  ", out_txt)
    out_txt = re.sub(r"- (.*)(!u)%21(\d*)([\S\s]*?)\n *id: *(\d*)", "--- \g<2>!\g<3> &\g<5>\n\g<1>\g<4>", out_txt)
    return out_txt
