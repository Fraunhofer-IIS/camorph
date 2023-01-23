import inspect
import math
from typing import Union

import numpy as np
from numpy import ndarray
from pyquaternion import Quaternion


class Camera():
    """
    This class represents camera parameters in camorph
    """


    def __init__(self):
        #          Z
        #          ^
        #          |
        #          |
        #          |
        #          .-------------> Y
        #         /
        #        /    c|
        #       v     a|-->
        #      X      m|
        #              v



        self.r: Union[Quaternion, None] = None
        """Rotation
        
        `Type`: Quaternion"""

        self.t: Union[ndarray, None] = None
        """Translation 
        
        `Type`: ndarray"""

        self.name: Union[str, None] = None
        """A unique name
        
        `Type`: str"""

        self.autocompute: bool = True
        """Automaic computation of certain parameters
        
        `Type`: bool"""

        self.focal_length_px: Union[list[float], None] = None
        """Focal length in pixels
        
        `Type`: float"""

        self.focal_length_mm: Union[list[float], None] = None
        """Focal length in millimeters
        
        `Type`: float"""

        self.resolution: Union[(float, float), None] = None
        """Resolution in pixels as a tuple
        
        `Type`: (float,float)"""

        self.principal_point: Union[(float, float), None] = None
        """Principal point in pixels as a tuple
        
        `Type`: (float,float)"""

        self.fov: Union[(float, float), None] = None
        """Field of view in radians

        `Type`: (float,float)"""

        self.projection_type: Union[str, None] = 'perspective'
        """Projection type, either `perspective`, `orthogonal` or `equirectangular`

        `Type`: str"""

        self.sensor_size: Union[(float, float), None] = None
        """Sensor size

        `Type`: (float,float)"""

        self.lens_shift: Union[(float, float), None] = None
        """Lens shift in normalized coordinates from -0.5 to 0.5

        `Type`: (float,float)"""

        self.model: Union[str, None] = 'pinhole'
        """Camera model. One of the following: `pinhole`, `opencv_fisheye`, `orthographic`, `brown`

        `Type`: str"""

        self.radial_distortion: Union[list[float], None] = None
        """Radial distortion coefficients

        `Type`: list[float]"""

        self.tangential_distortion: Union[list[float], None] = None
        """Tangential distortion coefficients

        `Type`: list[float]"""

        self.source_image: Union[str, None] = None
        """Path to a source image

        `Type`: str"""

        self.near_far_bounds: Union[list,None] = None
        """Near and far camera bounds
        
        `Type`: list[float]
        """



    def _has_or_none(self, *args):
        """
        This function returns False if one of the parameters in args is not bound or None
        :param args: List of parameters
        :return: bool
        """
        for param in args:
            if getattr(self, param, None) is None:
                return False
        return True

    def _focal_length_mm_1(self):
        """
        This function computes the focal length in mm
        :return: float
        """
        return [x * self.sensor_size[idx] / self.resolution[idx] for idx, x in enumerate(self.focal_length_px)]

    def _focal_length_mm_2(self):
        """
        This function computes the focal length in mm
        :return: float
        """
        return [x / (2 * math.atan2(self.fov[0], 2)) for idx, x in enumerate(self.sensor_size[0])]

    def _focal_length_px(self):
        """
        This function computes the focal length in px
        :return: float
        """
        return [x * self.resolution[idx] / self.sensor_size[idx] for idx, x in enumerate(self.focal_length_mm) ]

    def _sensor_size(self):
        """
        This function computes the sensor size in mm
        :return: (float, float)
        """
        return 2 * self.focal_length_mm[0] * math.tan(self.fov[0]), 2 * self.focal_length_mm[1] * math.tan(self.fov[1])

    def _fov(self):
        """
        This function computes the fov in radians
        :return: (float, float)
        """
        return 2 * math.atan2(self.sensor_size[0], 2 * self.focal_length_mm[0]), 2 * math.atan2(self.sensor_size[1],
                                                                                         2 * self.focal_length_mm[1])

    def _principal_point(self):
        """
        This function computes the principal point in px
        :return: (float, float)
        """
        return (0.5 + self.lens_shift[0]) * self.resolution[0], (0.5 + self.lens_shift[1]) * self.resolution[1]

    def _lens_shift(self):
        """
        This function computes the lens shift
        :return:
        """
        return self.principal_point[0] / self.resolution[0] - 0.5, self.principal_point[1] / self.resolution[1] - 0.5

    def __setattr__(self, key, value):
        super(Camera, self).__setattr__(key, value)
        if hasattr(self, 'autocompute') and not self.autocompute:
            return
        if hasattr(self, 'focal_length_mm') and self.focal_length_mm is None and key != 'focal_length_mm' and\
                self._has_or_none('focal_length_px', 'sensor_size', 'resolution'):
            self.focal_length_mm = self._focal_length_mm_1()
        if hasattr(self, 'focal_length_mm') and self.focal_length_mm is None and key != 'focal_length_mm' and\
                self._has_or_none('sensor_size', 'fov'):
            self.focal_length_mm = self._focal_length_mm_2()
        if hasattr(self, 'focal_length_px') and self.focal_length_px is None and key != 'focal_length_px' and\
                self._has_or_none('focal_length_mm', 'resolution','sensor_size'):
            self.focal_length_px = self._focal_length_px()
        if hasattr(self, 'sensor_size') and self.sensor_size is None and key != 'sensor_size' and\
                self._has_or_none('focal_length_mm', 'fov'):
            self.sensor_size = self._sensor_size()
        if hasattr(self, 'fov') and self.fov is None and key != 'fov' and\
                self._has_or_none('sensor_size', 'focal_length_mm'):
            self.fov = self._fov()
        if hasattr(self, 'principal_point') and self.principal_point is None and key != 'principal_point' and\
                self._has_or_none('lens_shift', 'resolution'):
            self.principal_point = self._principal_point()
        if hasattr(self, 'lens_shift') and self.lens_shift is None and key != 'lens_shift' and \
                self._has_or_none('principal_point', 'resolution'):
            self.lens_shift = self._lens_shift()

