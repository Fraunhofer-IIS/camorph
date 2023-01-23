import sys

from pyquaternion import Quaternion

import utils.math_utils as math_utils

sys.path.append('<project directory>')
sys.path.append("../..")  # Adds higher directory to python modules path.

import numpy as np
from ..model import *


# semantic helpers
def build_hierarchy_tree(connections, objects, node):
    resolved_connections = []
    for con in connections:
        if con.cnames[1] == node.id:
            if con.cnames[0] in objects:
                child_node = FBXHierarchyNode(con.cnames[0])
                child_node.object = objects[con.cnames[0]]
                node.children.append(child_node)
                resolved_connections.append(con)

    for con in resolved_connections:
        connections.remove(con)

    for child in node.children:
        build_hierarchy_tree(connections, objects, child)

# compute chained transforms and add connected objects
def resolve_hierarchy(parent, transforms):
    for child in parent.children:
        obj = child.object[0]
        if obj is not None and obj.name == 'Model':
            properties70 = obj.Properties70[0]
            if 'Lcl Translation' in properties70:
                translation = np.array(properties70['Lcl Translation'][0].pvalue)
            else:
                translation = np.array([0, 0, 0])
            if 'Lcl Rotation' in properties70:
                rotation = math_utils.euler_to_rotation_matrix(
                    [np.radians(x) for x in properties70['Lcl Rotation'][0].pvalue])
            else:
                rotation = np.identity(3)
            if 'Lcl Scaling' in properties70:
                scale = np.array(properties70['Lcl Scaling'][0].pvalue)
            else:
                scale = np.array([1, 1, 1])

            # get parent transforms
            parent_translation = transforms[parent.id][2]
            parent_rotation = transforms[parent.id][3]

            # chain parent transforms
            translation = translation / scale
            translation = parent_rotation @ translation
            translation = translation + parent_translation
            rotation = parent_rotation @ rotation

            transforms[child.id] = [obj, obj.pvalue, translation, rotation, child.children]
        elif obj is not None and obj.name == 'Texture':
            parent.object[0].Properties70[0]['FileName'] = obj.FileName[0]['props'][0]
        else:
            transforms[child.id] = [obj, None, np.array([0, 0, 0]), np.identity(3), child.children]
        resolve_hierarchy(child, transforms)

def get_coordinate_system(fbx_obj):
    def get_axis_from_dict(axis, axis_sign, dict):
        return dict[axis] if axis_sign > 0 else '-' + dict[axis]
    global_settings = fbx_obj['GlobalSettings']['Properties70'][0]
    up_axis = global_settings['UpAxis'][0].pvalue[0]
    up_axis_sign = global_settings['UpAxisSign'][0].pvalue[0]
    front_axis = global_settings['FrontAxis'][0].pvalue[0]
    front_axis_sign = global_settings['FrontAxisSign'][0].pvalue[0]
    coord_axis = global_settings['CoordAxis'][0].pvalue[0]
    coord_axis_sign = global_settings['CoordAxisSign'][0].pvalue[0]

    axis_dict = {0: 'x', 1: 'y', 2: 'z'}

    # we would need to look what vector is what direction
    # for example: what is x? x is right
    # then write what right is in our coordinate system: y
    # this is complicated, luckily for us we can go the other way round
    # which axes are x,y,z in the FBX coordinate system
    # then transpose/invert
    coordinate_system = [get_axis_from_dict(front_axis, front_axis_sign, axis_dict),
                         get_axis_from_dict(coord_axis, coord_axis_sign, axis_dict),
                         get_axis_from_dict(up_axis, up_axis_sign, axis_dict)]

    return coordinate_system

