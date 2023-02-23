"""
.. module:: math_utils
   :platform: Unix, Windows
   :synopsis: A useful module indeed.

.. moduleauthor:: Benjamin Brand


"""
from typing import Union
import numpy as np
import math
from pyquaternion import Quaternion


def euler_to_quaternion(vec, rot_order='xyz'):
    """This function converts a set of Euler angles to a quaternion.


        :param vec: Vector as xyz
        :type vec: ndarray
        :param rot_order: rotational order, one of 'xyz', 'xzy', 'yxz', 'yzx', 'zyx', 'zxy'
        :type rot_order: str

        :return: PyQuaternion

        """
    vec = [math.radians(x) for x in vec]
    combined = euler_to_rotation_matrix(vec, rot_order)

    return Quaternion(matrix=combined)


def quaternion_to_euler(q, rot_order='xyz'):
    """This function converts a quaternion to a set of Euler angles.


        :param q: Quaternion
        :type q: PyQuaternion
        :param rot_order: rotational order, one of 'xyz', 'yxz'
        :type rot_order: str

        :return: list[float]

        """
    mat = quaternion_to_rotation_matrix(q)
    return [math.degrees(x) for x in rotation_matrix_to_euler_angles(mat, rot_order)]



def convert_coordinate_systems(crd: list[str],
                               t: np.ndarray,
                               r: Union[Quaternion, np.ndarray],
                               cdir=np.array([0, 0, -1]),
                               cup=np.array([0, 1, 0]),
                               tdir=np.array([0, 0, -1]),
                               tup=np.array([0, 1, 0]),
                               transpose=False):
    """This function converts translation and rotation with up and front vectors between different coordinate systems
        crd is relative to the camorph coordinate system ['x', 'y', 'z'] with z up, y right, x front
        for example, if the new coordinate system is y up, z front, x left (y up right handed):
        ['x', 'z', 'y']

        :param crd: Relative coordinate axis to camorph coordinate system
        :type crd: list[str]
        :param t: Translation
        :type t: ndarray
        :param r: Rotation
        :type r: ndarray or Quaternion
        :param cdir: Front vector in the source coordinate system
        :type cdir: ndarray
        :param cup: Up vector in the source coordinate system
        :type cup: ndarray
        :param tdir: Front vector in the target coordinate system
        :type tdir: ndarray
        :param tup: Up vector in the target coordinate system
        :type tup: ndarray
        :param transpose: If the linear translation should be inverted.
        :type transpose: bool


        :return: (ndarray, quaternion)

        """


    basevectors = {'x': [1, 0, 0], 'y': [0, 1, 0], 'z': [0, 0, 1], '-x': [-1, 0, 0], '-y': [0, -1, 0], '-z': [0, 0, -1]}

    # check if there are only valid values
    if any([x not in basevectors.keys() for x in crd]):
        raise Exception('Coordinate base vectors must be x,y,z,-x,-y,-z')

    # build base
    # quaternion
    basemat = basevectors[crd[0]]
    basemat.extend(basevectors[crd[1]])
    basemat.extend(basevectors[crd[2]])
    basemat = np.array(basemat).reshape(3, 3)
    # important, because this looks funny:
    # it is easier to build the row matrix
    # but the normal use case is to apply the inverse, which is the same as the transpose in this case
    # so, in normal circumstances we want basemat.inverse
    # BUT sometimes we want to inverse, when it is more convenient (FBX for example)
    # so then we need basemat.inverse.inverse which is just our basemat
    basemat = np.matrix(basemat) if transpose else np.matrix(basemat).transpose()

    # check if matrix is a pure rotational matrix, e.g. if its determinant is positive 1
    det = np.linalg.det(basemat)
    if det == -1:
        # the only possibility for our determinant to be negative
        # is when we convert from right hand to left hand or vice versa
        # so we need to reflect our matrix
        # the plane of reflection does not matter, we choose the y-z plane
        mirror_mat = np.matrix([[-1, 0, 0], [0, 1, 0], [0, 0, 1]])
        basemat = basemat @ mirror_mat
        translation = np.asarray(mirror_mat @ basemat @ t).reshape(-1)
        basequat = Quaternion(matrix=basemat)
        # we need to reflect the quaternion later after conversion
        mirrored = True

    else:
        translation = np.asarray(basemat @ t).reshape(-1)
        basequat = Quaternion(matrix=basemat)
        mirrored = False

    if isinstance(r, Quaternion):
        q_r = r

    elif isinstance(r, np.ndarray):
        if r.shape != (3, 3):
            raise Exception('Matrix must be in shape 3x3')

        q_r = Quaternion(matrix=r)

    else:
        raise Exception("Rotation must be either Quaternion or 3 x 3 np matrix")

    # build local source camera coordinate system
    ccoord = np.cross(cdir, cup)
    csystem = np.array([np.array(cdir), np.array(cup), np.array(ccoord)])
    # build local target camera coordinate system
    tcoord = np.cross(tdir, tup)
    tsystem = np.array([np.array(tdir), np.array(tup), np.array(tcoord)])

    # compute rotational difference between camera matrices
    diffmat = tsystem.transpose() @ csystem
    cdiff = Quaternion(matrix=diffmat)

    # the god formula
    q = basequat * q_r * cdiff.inverse

    # if the system was converted from right to left handed and vice versa, we need to apply the reflection of our rotation here
    if mirrored:
        q = Quaternion(-q.w, -q.x, q.y, q.z)
    return translation, q


def quaternion_difference(q1, q2):
    """This function returns the rotational difference between two quaternions


        :param q1: First Quaternion
        :type q1: PyQuaternion
        :param q2: Second Quaternion
        :type q2: PyQuaternion

        :return: PyQuaternion

        """
    q1 / np.linalg.norm(q1)
    q2 / np.linalg.norm(q2)
    v = q1 + q2
    if np.linalg.norm(v) != 0:
        v = v / np.linalg.norm(v)
    else:
        # rotation of 180 or 360 deg, axis irrelevant
        v = np.array([1, 0, 0])
    angle = math.acos(np.dot(q1, q2))
    axis = np.cross(v, q2)
    if np.linalg.norm(axis) == 0:
        return Quaternion()
    return Quaternion(angle=angle, axis=axis)


def euler_to_rotation_matrix(vec, rotation_order='xyz'):
    """This function converts a set of euler angles to a rotation matrix with the given order


        :param vec: Vector as xyz
        :type vec: ndarray
        :param rot_order: rotational order, one of 'xyz', 'xzy', 'yxz', 'yzx', 'zyx', 'zxy'
        :type rot_order: str

        :return: ndarray

        """
    x = vec[0]
    y = vec[1]
    z = vec[2]
    rotmat_x = np.array([[1, 0, 0], [0, np.cos(x), -np.sin(x)], [0, np.sin(x), np.cos(x)]])
    rotmat_y = np.array([[np.cos(y), 0, np.sin(y)], [0, 1, 0], [-np.sin(y), 0, np.cos(y)]])
    rotmat_z = np.array([[np.cos(z), -np.sin(z), 0], [np.sin(z), np.cos(z), 0], [0, 0, 1]])

    if rotation_order == 'zyx':
        combined = rotmat_x @ rotmat_y @ rotmat_z
    elif rotation_order == 'zxy':
        combined = rotmat_y @ rotmat_x @ rotmat_z
    elif rotation_order == 'xzy':
        combined = rotmat_y @ rotmat_z @ rotmat_x
    elif rotation_order == 'xyz':
        combined = rotmat_z @ rotmat_y @ rotmat_x
    elif rotation_order == 'yxz':
        combined = rotmat_z @ rotmat_x @ rotmat_y
    elif rotation_order == 'yzx':
        combined = rotmat_x @ rotmat_z @ rotmat_y
    else:
        raise Exception('Rotational Order not supported')

    return combined


# Calculates Rotation Matrix given euler angles.
def rotation_matrix_to_euler_angles(R, rot_order='xyz'):
    """This function converts a rotation matrix to a set of euler angles
        From Gregory G. Slabaugh "Computing Euler angles from a rotation matrix"
        Other orders are calculated in a similiar fashion.

        :param R: Rotation matrix
        :type R: ndarray
        :param rot_order: rotational order, one of 'xyz', 'yxz'
        :type rot_order: str

        :return: ndarray

        """
    if rot_order == 'xyz':
        if math.fabs(R[2][0]) < 0.9999:
            theta = -np.arcsin(R[2][0])
            psi = np.arctan2(R[2][1] / np.cos(theta), R[2][2] / np.cos(theta))
            phi = np.arctan2(R[1][0] / np.cos(theta), R[0][0] / np.cos(theta))
        else:
            phi = 0
            if R[2][0] < -0.9999:
                theta = math.pi / 2
                psi = phi + np.arctan2(R[0][1], R[0][2])
            else:
                theta = -math.pi / 2
                psi = -phi + np.arctan2(-R[0][1], -R[0][2])
        return np.array((psi, theta, phi))
    elif rot_order == 'yxz':
        if math.fabs(R[2][1]) < 0.9999:
            psi = np.arcsin(R[2][1])
            phi = -np.arctan2(R[0][1] / np.cos(psi), R[1][1] / np.cos(psi))
            theta = -np.arctan2(R[2][0] / np.cos(psi), R[2][2] / np.cos(psi))
        else:
            theta = 0
            if R[2][1] < -0.9999:
                psi = -math.pi / 2
                phi = -theta + np.arctan2(-R[1][0], -R[0][0])
            else:
                psi = math.pi / 2
                phi = theta + np.arctan2(R[1][0], R[0][0])
        return np.array((psi, theta, phi))
    elif rot_order == 'zxy':
        if math.fabs(R[1][2]) < 0.9999:
            psi = - np.arcsin(R[1][2])
            phi = np.arctan2(R[1][0] / np.cos(psi), R[1][1] / np.cos(psi))
            theta = np.arctan2(R[0][2] / np.cos(psi), R[2][2] / np.cos(psi))
        else:
            phi = 0
            if R[1][2] < -0.9999:
                psi = math.pi / 2
                theta = phi + np.arctan2(R[0][1], R[0][0])
            else:
                psi = -math.pi / 2
                theta = -phi + np.arctan2(-R[0][1], -R[0][0])
        return np.array((psi, theta, phi))
    else:
        raise Exception("Unsupported rotation order")


def quaternion_to_rotation_matrix(q: Quaternion):
    """This function converts a quaternion to the corresponding rotation matrix.

    :param q: Quaterion
    :type q: PyQuaternion
    :return: ndarray
    """
    return q.rotation_matrix

def inch_to_mm(inch: float):
    """
    This function converts inch to mm.

    :param inch: Inch
    :type inch: float
    :return: float
    """
    return inch * 25.4


def mm_to_inch(mm: float):
    """
    This function converts mm to inch.

    :param mm: Millimeter
    :type mm: float
    :return: float
    """
    return mm / 25.4
