import numpy as np
from pyquaternion import Quaternion


def apply_transform_rec(cur_transform, transforms, translation=None, rotation=None):
    father_id = cur_transform['m_Father']['fileID']
    if translation is None and rotation is None:
        translation, rotation = get_translation_and_rotation(cur_transform)
    if father_id != 0:
        father = next(x for x in transforms if x['obj_id'] == cur_transform['m_Father']['fileID'])
        f_translation, f_rotation = get_translation_and_rotation(father)
        translation = translation
        translation = f_rotation.rotate(translation)
        translation = translation + f_translation
        rotation = f_rotation * rotation
        return apply_transform_rec(father, transforms, translation, rotation)
    else:
        return translation, rotation


def get_translation_and_rotation(transform):
    translation = np.asarray([transform['m_LocalPosition']['x'], transform['m_LocalPosition']['y'],transform['m_LocalPosition']['z']])
    rotation = Quaternion(transform['m_LocalRotation']['w'], transform['m_LocalRotation']['x'], transform['m_LocalRotation']['y'], transform['m_LocalRotation']['z'])
    return translation, rotation