import yaml


class UnityGameObject(yaml.YAMLObject):
    yaml_tag = r'!u!1'

    def __init__(self, id, cam_id, transform_id, Name):
        self.id = id
        self.m_ObjectHideFlags = 0
        self.m_CorrespondingSourceObject = dict(fileID=0)
        self.m_PrefabInstance = dict(fileID=0)
        self.m_PrefabAsset = dict(fileID=0)
        self.serializedVersion = 6
        self.m_Component = [dict(component=dict(fileID=cam_id)), dict(component=dict(fileID=transform_id))]
        self.m_Layer = 0
        self.m_Name = Name
        self.m_TagString = Name
        self.m_Icon = dict(fileID=0)
        self.m_NavMeshLayer = 0
        self.m_StaticEditorFlags = 0
        self.m_IsActive = 1
