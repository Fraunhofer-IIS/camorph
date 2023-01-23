About
=====

Camorph is a python library to convert different representations of camera parameters into each other.

Quickstart
==========

.. code-block:: python

    import camorph.camorph as camorph


    cams = camorph.read_cameras('COLMAP',r'\\path\to\colmap')

    camorph.visualize(cams)

    camorph.write_cameras('fbx', r'\\path\to\file.fbx', cams)


:meth:`camorph.read_cameras` takes a format name and path as a string and returns a list of :class:`Cameras <model.Camera.Camera>`.

:meth:`camorph.visualize` creates a visualization of :class:`Cameras <model.Camera.Camera>` with `Matplotlib <https://matplotlib.org/>`_.

:meth:`camorph.write_cameras` takes a format name, a path as a string and a list of cameras and writes the output file(s) to the specified path.

Currently supported formats:
   - Computer Graphics
      - :doc:`FBX <formats/FBX/FBX>`
   - Photogrammetry
      - :doc:`COLMAP <formats/COLMAP/COLMAP>`
      - :doc:`Meshroom <formats/Meshroom/Meshroom>`
      - :doc:`Reality Capture <formats/RealityCapture/RealityCapture>`
   - Game Engines
      - :doc:`Unity <formats/Unity/Unity>`
   - Virtual Reality
      - :doc:`MPEG OMAF <formats/MPEG_OMAF/MPEG_OMAF>`
   - Machine Learning
      - :doc:`NeRF <formats/NeRF/NeRF>`