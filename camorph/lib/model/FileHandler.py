# This is an interface to be used for all new extensions

from abc import ABC, abstractmethod
from functools import wraps


class FileHandler(ABC):
    """
    This is the base class for all external FileHandlers.
    """

    @abstractmethod
    def crucial_properties(self) -> list[(str, type)]:
        """
        Define all crucial properties as a list of the property name, for example:
        return ['source_image', 'resolution']
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The unique name of the FileHandler, for example COLMAP, fbx, etc.
        """
        pass

    @property
    @abstractmethod
    def file_number(self) -> int:
        """
        How many files the Handler needs to read or write. Return -1 if the number cannot be known beforehand (for example RealityCapture).
        """
        pass

    @abstractmethod
    def read_file(self, *args, **kwargs):
        """
        Read the given file

        :param args: The input parameters, usually file paths.
        :param kwargs: The input keyword args, like posetrace.
        :return: list[Camera]
        """
        pass

    @abstractmethod
    def write_file(self, camera_array, output_path, file_type=None):
        """
        Write the given list of cameras to a file.

        :param camera_array: The list of cameras
        :param output_path: The output path
        :param file_type: An optional string for different filetypes (for example binary or ascii)
        :return: None
        """
        pass

    @abstractmethod
    def coordinate_from(self, camera_array):
        """
        Convert cameras rotation and translation from this coordinate system into camorph coordinate system

        :param camera_array: Ths list of cameras
        :return: list[Camera]
        """
        pass

    @abstractmethod
    def coordinate_into(self, camera_array):
        """
        Convert cameras rotation and translation from camorph coordinate system into this coordinate system

        :param camera_array: Ths list of cameras
        :return: list[Camera]
        """
        pass
