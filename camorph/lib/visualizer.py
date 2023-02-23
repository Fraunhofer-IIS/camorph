from model.Camera import Camera
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

def visualize(cams: list[Camera]):
    """
    This function takes a list of camorph cameras and visualizes them with matplotlib

    :param cams: A list of camorph Cameras
    :type cams: list[Camera]
    :return: None
    """
    x,y,z = zip(*[x.t for x in cams])
    dir = np.array([0,0,-1])
    up = np.array([0,1,0])
    maxdist = max([np.linalg.norm(x.t) for x in cams])
    dir = dir * maxdist * 0.2
    up = up * maxdist * 0.2
    #dir = np.array([1, 0, 0])
    #up = np.array([0, 0, 1])
    dirx,diry,dirz = zip(*[x.r.rotate(dir) for x in cams])
    upx, upy, upz = zip(*[x.r.rotate(up) for x in cams])
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.quiver(x, y, z, dirx, diry, dirz, color='r', label='Camera Front')
    ax.quiver(x, y, z, upx, upy, upz, color='g', label='Camera Up')

    ax.set_xlim([-maxdist, maxdist])
    ax.set_ylim([-maxdist, maxdist])
    ax.set_zlim([-maxdist, maxdist])

    ax.scatter(x,y,z)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    ax.legend()

    plt.show()