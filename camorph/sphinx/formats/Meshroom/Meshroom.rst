Meshroom
========

*Meshroom* is a 3D reconstruction software developed by Griwodz et. al.
The software has a nodal architecture and stores intermediate results in
a specific subfolder structure. Each nodes data is stored in a folder
with its unique identifier as a name in a subfolder of the node type in
the folder ``MeshroomCache``. The reconstructed camera poses are stored
in ``cameras.sfm`` in the ``StructureFromMotion`` folder. Known poses
can be imported into Mehsroom by setting the input of a
``FeatureExtraction`` node to the custom ``cameras.sfm`` file.

Coordinate System
-----------------

The standard *Meshroom* coordinate system is y up, x right, z front. The camera orientation is -z front and y up.

.. image:: Meshrrom_coordinatesystem_cam-1.png

SfM File
--------
The SfM file uses the widespread JSON format.

-  ``featuresFolders`` and ``matchesFolders`` point to specific folders
   in the *Meshroom* folder structure, and should be left empty when
   writing a custom file.

-  ``views`` holds view objects which hold data of a source image used
   for reconstruction in *Meshroom*.

   -  ``viewId`` is a unique identifier

   -  ``poseId`` refers to a pose object in ``poses`` where extrinsic
      parameters are stored

   -  ``intrinsicId`` refers to an intrinsic object in ``intrinsics``
      where intrinsic parameters are stored

   -  ``path`` refers to the file path of the source image

   -  ``width`` and ``height`` are the width and height of the image

   -  ``metadata`` holds metadata about the image which is not relevant
      in this thesis.

-  ``intrinsics`` holds intrinsic objects which store intrinsic
   parameters of a specific camera model

   -  ``intrinsicId`` is a unique identifier

   -  ``width`` and ``height`` the resolution of the camera

   -  ``sensorWidth`` and ``sensorHeight`` the size of the sensor in mm

   -  ``serialNumber`` the serial number of the camera the source image
      was taken with

   -  ``type`` the name of the distortion model type

   -  ``initializationMode`` one of ``calibrated`` for externally
      calibrated cameras, ``estimated`` for estimated cameras,
      ``unknown`` for unkown cameras with guess values or ``none`` for
      none

   -  ``pxInitialFocalLength`` is the initial guess of the focal length
      in px

   -  ``pxFocalLength`` is the focal length in px

   -  ``principalPoint`` is the principal point in px

   -  ``distortionParams`` are the distortion params of the camera model

   -  ``locked`` is a bool if the intrinsic objects parameters are
      locked or can be modified

-  ``poses`` holds pose objects which store extrinsic parameters of a
   specific pose

   -  ``poseId`` is a unique identifier

   -  ``pose`` is a nested pose object

      -  ``transform`` stores the rotation as ``rotation`` as a matrix
         in row major order and the translation as ``center`` as a
         three-dimensional vector

   -  ``locked`` is a bool if the pose objects parameters are locked or
      can be modified

Camera Models
-------------
Meshroom supports the following camera models:

+--------------------+-----------------------+-----------------------+
| **Name**           | **Description**       | **Parameters**        |
+====================+=======================+=======================+
| ``pinhole``        | Pinhole model without |                       |
|                    | distortion            |                       |
|                    | coefficients          |                       |
+--------------------+-----------------------+-----------------------+
| ``radial1``        | Brown model with one  | k1                    |
|                    | radial coefficient    |                       |
+--------------------+-----------------------+-----------------------+
| ``radial3``        | Brown model with      | k1, k2, k3            |
|                    | three radial          |                       |
|                    | coefficients          |                       |
+--------------------+-----------------------+-----------------------+
| ``brown``          | Brown model with      | k1, k2, k3, t1, t2    |
|                    | three radial and two  |                       |
|                    | tangential            |                       |
|                    | coefficients          |                       |
+--------------------+-----------------------+-----------------------+
| ``fisheye``        | OpenCV fisheye        | k1, k2, k3, k4        |
|                    | distortion model with |                       |
|                    | 4                     |                       |
|                    | coefficients          |                       |
|                    |                       |                       |
+--------------------+-----------------------+-----------------------+
| ``equidistant_r3`` | Camera model used for | w                     |
|                    | fisheye optics with   |                       |
|                    | distortion provided   |                       |
|                    | in [1]_               |                       |
|                    |                       |                       |
+--------------------+-----------------------+-----------------------+
| ``3deanamorphic4`` | Anamorphic camera     | cxx, cxy, cyx, cyy    |
|                    | model with 4          |                       |
|                    | coefficients used by  |                       |
|                    | 3D Equalizer          |                       |
|                    |                       |                       |
+--------------------+-----------------------+-----------------------+
| ``3declassicld``   | Anamorphic camera     | delta, epsilon, mux,  |
|                    | model with 10         | muy, q                |
|                    | coefficients used by  |                       |
|                    | 3D Equalizer          |                       |
|                    |                       |                       |
+--------------------+-----------------------+-----------------------+
| ``3deradial4``     | Radial camera model   | c2, c4, u1, v1, u3,   |
|                    | with used by 3D       | v3                    |
|                    | Equalizer             |                       |
|                    |                       |                       |
+--------------------+-----------------------+-----------------------+

.. [1] Devernay, Frédéric and Faugeras, Olivier. "Straight Lines Have to Be Straight
    Automatic Calibration and Removal of Distortion from Scenes of Structured Envi-
    ronments". In: *Mach Vis Appl 13 (Aug. 2001)*. doi: 10.1007/PL00013269