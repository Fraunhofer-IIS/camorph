
Autocomputation
===============

Some parameters on camera representations are equivalent. For example, the focal length can be expressed in millimeters as well as in pixels.
Camorph supports autocomputation of certain parameters. The :class:`Camera <model.Camera.Camera>` class has the
attribute `autcompute` which is true by default.To disable autocompute, set this to false.

The supported parameters are:
   - Focal length in pixels from focal length in millimeters, sensor size and resolution
   - Focal length in millimeters from focal length in pixels, sensor size and resolution
   - Focal length in millimeters from sensor size and field of view
   - Sensor size in millimeters from focal length in millimeters and field of view
   - Field of view in radians from focal length in millimeters and sensor size
   - Principal point in pixel coordinates from lens shift and resolution
   - lens shift in normalized coordinates from -0.5 to +0.5 from principal point and resolution