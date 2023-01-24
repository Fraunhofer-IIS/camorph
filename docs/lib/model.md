# `Camera` Class


### _class_ model.Camera.Camera()
This class represents camera parameters in camorph


#### autocompute()
Automaic computation of certain parameters

Type: bool


#### focal_length_mm()
Focal length in millimeters

Type: float


#### focal_length_px()
Focal length in pixels

Type: float


#### fov()
Field of view in radians

Type: (float,float)


#### lens_shift()
Lens shift in normalized coordinates from -0.5 to 0.5

Type: (float,float)


#### model()
Camera model. One of the following: pinhole, opencv_fisheye, orthographic, brown

Type: str


#### name()
A unique name

Type: str


#### near_far_bounds()
Near and far camera bounds

Type: list[float]


#### principal_point()
Principal point in pixels as a tuple

Type: (float,float)


#### projection_type()
Projection type, either perspective, orthogonal or equirectangular

Type: str


#### r()
Rotation

Type: Quaternion


#### radial_distortion()
Radial distortion coefficients

Type: list[float]


#### resolution()
Resolution in pixels as a tuple

Type: (float,float)


#### sensor_size()
Sensor size

Type: (float,float)


#### source_image()
Path to a source image

Type: str


#### t()
Translation

Type: ndarray


#### tangential_distortion()
Tangential distortion coefficients

Type: list[float]

# `FileHandler` Class


### _class_ model.FileHandler.FileHandler()
This is the base class for all external FileHandlers.


#### _abstract_ coordinate_from(camera_array)
Convert cameras rotation and translation from this coordinate system into camorph coordinate system


* **Parameters**

    **camera_array** – Ths list of cameras



* **Returns**

    list[Camera]



#### _abstract_ coordinate_into(camera_array)
Convert cameras rotation and translation from camorph coordinate system into this coordinate system


* **Parameters**

    **camera_array** – Ths list of cameras



* **Returns**

    list[Camera]



#### _abstract_ crucial_properties()
Define all crucial properties as a list of the property name, for example:
return [‘source_image’, ‘resolution’]


#### _abstract property_ file_number()
How many files the Handler needs to read or write. Return -1 if the number cannot be known beforehand (for example RealityCapture).


#### _abstract property_ name()
The unique name of the FileHandler, for example COLMAP, fbx, etc.


#### _abstract_ read_file(\*args, \*\*kwargs)
Read the given file


* **Parameters**

    
    * **args** – The input parameters, usually file paths.


    * **kwargs** – The input keyword args, like posetrace.



* **Returns**

    list[Camera]



#### _abstract_ write_file(camera_array, output_path, file_type=None)
Write the given list of cameras to a file.


* **Parameters**

    
    * **camera_array** – The list of cameras


    * **output_path** – The output path


    * **file_type** – An optional string for different filetypes (for example binary or ascii)



* **Returns**

    None
