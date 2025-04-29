from .COLMAP import COLMAP
from .FBX import FBX
from .LLFF import LLFF
from .Meshroom import Meshroom
from .MPEG_OMAF import MPEG_OMAF
from .NeRF import NeRF
from .RealityCapture import RealityCapture
from .Unity import Unity

imported_instances = {
    "colmap": COLMAP(),
    "fbx": FBX(),
    "llff": LLFF(),
    "meshroom": Meshroom(),
    "mpeg_omaf": MPEG_OMAF(),
    "nerf": NeRF(),
    "reality_capture": RealityCapture(),
    "unity": Unity(),
}