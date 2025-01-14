import yaml
from numpy.core.records import ndarray
from pyquaternion import Quaternion

from camorph.lib.utils import math_utils


class UnityTransform(yaml.YAMLObject):
    yaml_tag = r'!u!4'
    def __init__(self, t: ndarray, r: Quaternion,  id, game_object_id):
        self.id = id
        self.m_ObjectHideFlags = 0
        self.m_CorrespondingSourceObject = dict(fileID=0)
        self.m_PrefabInstance = dict(fileID=0)
        self.m_PrefabAsset = dict(fileID=0)
        self.m_GameObject = dict(fileID=game_object_id)
        self.m_LocalRotation = dict(x=float(r.x), y=float(r.y), z=float(r.z), w=float(r.w))
        self.m_LocalPosition = dict(x=float(t[0]), y=float(t[1]), z=float(t[2]))
        self.m_LocalScale = dict(x=1, y=1, z=1)
        self.m_Children = []
        self.m_Father = dict(fileID=0)
        self.m_RootOrder = 0
        e = math_utils.quaternion_to_euler(r)
        self.m_LocalEulerAnglesHint = dict(x=e[0], y=e[1], z=e[2])
