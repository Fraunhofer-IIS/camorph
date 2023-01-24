# Camorph
<font size=5>

[Paper](https://www.int-arch-photogramm-remote-sens-spatial-inf-sci.net/XLVIII-2-W1-2022/29/2022/isprs-archives-XLVIII-2-W1-2022-29-2022.pdf)
</font>
<center>
<img src='Header.png' width=90%/>
</center>

This is the gitlab project for camorph, a camera parameter converting tool written in python 3.9.

## Documentation

Documentation can be found [here](docs/index.md).

## Quickstart

Install the conda environment by running

```
conda env create -f camorph_win.yml
```

Then use the library to convert camera parameter representations:

```
import camorph.camorph as camorph
 
 
cams = camorph.read_cameras('COLMAP',r'\\path\to\colmap')
 
camorph.visualize(cams)
 
camorph.write_cameras('fbx', r'\\path\to\file.fbx', cams)
```

``camorph.read_cameras()`` takes a format name and path as a string and returns a list of Cameras.

``camorph.visualize()`` creates a visualization of Cameras with Matplotlib.

``camorph.write_cameras()`` takes a format name, a path as a string and a list of cameras and writes the output file(s) to the specified path.

**Currently supported formats:**

- Computer Graphics
   - FBX

- Photogrammetry
   - COLMAP
   - Meshroom
   - Reality Capture

- Game Engines
   - Unity

- Virtual Reality
   - MPEG OMAF

- Machine Learning
   - NeRF

## Citation 

```
@article{Brand2022CAMORPHAT,
  title={CAMORPH: A TOOLBOX FOR CONVERSION BETWEEN CAMERA PARAMETER
CONVENTIONS},
  author={B. Brand and Michel B{\"a}tz and Joachim Keinert},
  journal={The International Archives of the Photogrammetry, Remote Sensing and Spatial Information Sciences},
  year={2022}
}
```