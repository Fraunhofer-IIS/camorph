import yaml
import numpy as np

class UnityCamera(yaml.YAMLObject):
    yaml_tag = '!u!20'
    def __init__(self, id, game_object_id, focal_length = 50, sensor_size = (36,24),fov = 60, projection_type = 'perspective' ):
        self.id = id
        self.m_ObjectHideFlags = 0
        self.m_CorrespondingSourceObject = dict(fileID=0)
        self.m_PrefabInstance = dict(fileID=0)
        self.m_PrefabAsset = dict(fileID=0)
        self.m_GameObject = dict(fileID=game_object_id)
        self.m_Enabled = 1
        self.serializedVersion = 2
        self.m_ClearFlags = 2
        self.m_BackGroundColor = dict(r=0.19215687, g=0.3019608, b=0.4745098, a=0)
        self.m_projectionMatrixMode = 1
        self.m_GateFitMode = 2
        self.m_FOVAxisMode = 1
        self.m_SensorSize = dict(x=float(sensor_size[0]), y=float(sensor_size[1]))
        self.m_LensShift = dict(x=0, y=0)
        self.m_FocalLength = float(focal_length)
        self.m_NormalizedViewPortRect = dict(
            serializedVersion=2,
            x=0,
            y=0,
            width=1,
            height=1)
        setattr(self, 'near clip plane', 0.3)
        setattr(self, 'far clip plane', 1000)
        setattr(self, 'field of view', fov)
        self.orthographic = 0 if projection_type == 'perspective' else 1
        setattr(self, 'orthographic size', 5)
        self.m_Depth = -1
        self.m_CullingMask = dict(
            serializedVersion=2,
            m_Bits=4294967295)
        self.m_RenderingPath = -1
        self.m_TargetTexture = dict(fileID=0)
        self.m_TargetDisplay = 0
        self.m_TargetEye = 0
        self.m_HDR = 1
        self.m_AllowMSAA = 0
        self.m_AllowDynamicResolution = 0
        self.m_ForceIntoRT = 0
        self.m_OcclusionCulling = 0
        self.m_StereoConvergence = 10
        self.m_StereoSeparation = 0.022
