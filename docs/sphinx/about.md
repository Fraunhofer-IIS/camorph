# About

Camorph is a python library to convert different representations of camera parameters into each other.

# Quickstart

```python
import camorph.camorph as camorph


cams = camorph.read_cameras('COLMAP',r'\\path\to\colmap')

camorph.visualize(cams)

camorph.write_cameras('fbx', r'\\path\to\file.fbx', cams)
```

[`camorph.read_cameras()`](camorph.md#camorph.read_cameras) takes a format name and path as a string and returns a list of [`Cameras`](../lib/model.md#model.Camera.Camera).

[`camorph.visualize()`](camorph.md#camorph.visualize) creates a visualization of [`Cameras`](../lib/model.md#model.Camera.Camera) with [Matplotlib](https://matplotlib.org/).

[`camorph.write_cameras()`](camorph.md#camorph.write_cameras) takes a format name, a path as a string and a list of cameras and writes the output file(s) to the specified path.

Currently supported formats:

    
* Computer Graphics


  * [FBX](formats/FBX/FBX.md)


* Photogrammetry


  * [COLMAP](formats/COLMAP/COLMAP.md)


  * [Meshroom](formats/Meshroom/Meshroom.md)


  * [Reality Capture](formats/RealityCapture/RealityCapture.md)


* Game Engines


  * [Unity](formats/Unity/Unity.md)


* Virtual Reality


  * [MPEG OMAF](formats/MPEG_OMAF/MPEG_OMAF.md)


* Machine Learning


  * [NeRF](formats/NeRF/NeRF.md)
