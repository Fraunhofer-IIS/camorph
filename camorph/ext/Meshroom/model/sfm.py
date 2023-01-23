from json import JSONEncoder


class sfm:

    def __init__(self):
        self.version = ["1","0","0"]
        self.feature_folders = [""]
        self.matchesFolders = [""]
        self.views = []
        self.intrinsics = []
        self.poses = []


class sfm_view:

    def __init__(self):
        self.viewId = '0'
        self.poseId = '0'
        self.intrinsicId = '0'
        self.resectionId = '0'
        self.path = ""
        self.width = '0'
        self.height = '0'
        self.metadata = None

class sfm_intrinsics(dict):

    def __init__(self):
        super().__init__()
        self.intrinsicId = '0'
        self.width = '0'
        self.height = '0'
        self.sensorWidth = '0'
        self.sensorHeight = '0'
        self.serialNumber = '0'
        self.type = 'pinhole'
        self.initializationMode = 'calibrated'
        self.pxInitialFocalLength = '0'
        self.pxFocalLength = '0'
        self.principalPoint = ['0','0']
        self.locked = '1'

class sfm_pose:

    def __init__(self):
        self.poseId = '0'
        self.pose = sfm_transform()
        self.locked = '1'

class sfm_transform:

    def __init__(self):
        transform_obj = dict()
        transform_obj['rotation'] = []
        transform_obj['center'] = []
        self.transform = transform_obj