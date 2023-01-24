# `math_utils` module


### utils.math_utils.convert_coordinate_systems(crd, t, r, cdir=array([0, 0, - 1]), cup=array([0, 1, 0]), tdir=array([0, 0, - 1]), tup=array([0, 1, 0]), transpose=False)
This function converts translation and rotation with up and front vectors between different coordinate systems
crd is relative to the camorph coordinate system [‘x’, ‘y’, ‘z’] with z up, y right, x front
for example, if the new coordinate system is y up, z front, x left (y up right handed):
[‘x’, ‘z’, ‘y’]


* **Parameters**

    
    * **crd** (*list**[**str**]*) – Relative coordinate axis to camorph coordinate system


    * **t** (*ndarray*) – Translation


    * **r** (*ndarray** or **Quaternion*) – Rotation


    * **cdir** (*ndarray*) – Front vector in the source coordinate system


    * **cup** (*ndarray*) – Up vector in the source coordinate system


    * **tdir** (*ndarray*) – Front vector in the target coordinate system


    * **tup** (*ndarray*) – Up vector in the target coordinate system


    * **transpose** (*bool*) – If the linear translation should be inverted.



* **Returns**

    (ndarray, quaternion)



### utils.math_utils.euler_to_quaternion(vec, rot_order='xyz')
This function converts a set of euler angles to a quaternion.


* **Parameters**

    
    * **vec** (*ndarray*) – Vector as xyz


    * **rot_order** (*str*) – rotational order, one of ‘xyz’, ‘xzy’, ‘yxz’, ‘yzx’, ‘zyx’, ‘zxy’



* **Returns**

    PyQuaternion



### utils.math_utils.euler_to_rotation_matrix(vec, rotation_order='xyz')
This function converts a set of euler angles to a rotation matrix with the given order


* **Parameters**

    
    * **vec** (*ndarray*) – Vector as xyz


    * **rot_order** (*str*) – rotational order, one of ‘xyz’, ‘xzy’, ‘yxz’, ‘yzx’, ‘zyx’, ‘zxy’



* **Returns**

    ndarray



### utils.math_utils.inch_to_mm(inch)
This function converts inch to mm.


* **Parameters**

    **inch** (*float*) – Inch



* **Returns**

    float



### utils.math_utils.mm_to_inch(mm)
This function converts mm to inch.


* **Parameters**

    **mm** (*float*) – Millimeter



* **Returns**

    float



### utils.math_utils.quaternion_difference(q1, q2)
This function returns the rotational difference between two quaternions


* **Parameters**

    
    * **q1** (*PyQuaternion*) – First Quaternion


    * **q2** (*PyQuaternion*) – Second Quaternion



* **Returns**

    PyQuaternion



### utils.math_utils.quaternion_to_euler(q, rot_order='xyz')
This function converts a quaternion of euler angles to a quaternion.


* **Parameters**

    
    * **q** (*PyQuaternion*) – Quaternion


    * **rot_order** (*str*) – rotational order, one of ‘xyz’, ‘yxz’



* **Returns**

    list[float]



### utils.math_utils.quaternion_to_rotation_matrix(q)
This function converts a quaternion to the corresponding rotation matrix.


* **Parameters**

    **q** (*PyQuaternion*) – Quaterion



* **Returns**

    ndarray



### utils.math_utils.rotation_matrix_to_euler_angles(R, rot_order='xyz')
This function converts a rotation matrix to a set of euler angles
From Gregory G. Slabaugh “Computing Euler angles from a rotation matrix”
Other orders are calculated in a similiar fashion.


* **Parameters**

    
    * **R** (*ndarray*) – Rotation matrix


    * **rot_order** (*str*) – rotational order, one of ‘xyz’, ‘yxz’



* **Returns**

    ndarray


# `file_utils` module


### utils.file_utils.extension(path)
This function returns the extension of a filename.
:param path: Filename
:type path: str
:return: str


### utils.file_utils.fixed_list(ilist, length, optype=None)
This function returns a list of a fixed length, regardless of number of elements in the input list.
If the list is shorter than the length parameter, it will be padded with the default value for this type.
When the list is empty, an optype has to be supplied.
For example:
>>> ilist = list[1.0]
>>> fixed_list(ilist, 3)
returns [1.0,0.0,0.0]


* **Parameters**

    
    * **ilist** – List to extend or truncate


    * **length** – Desired output length


    * **optype** – When ilist is empty, this is the type with which the list is filled.



* **Returns**

    list[any]



### utils.file_utils.get_files_in_dir(path, extension=None)
This function returns all files in a given directory with an optional extension match.
:param path: Path to directory
:type path: str
:param extension: Optional extension
:type extension: str
:return: list[str]


### utils.file_utils.peek(f, length)
This function peeks if the file can be read for a given length.


* **Parameters**

    
    * **f** – File handle


    * **length** – Length



* **Returns**

    bytes or str
