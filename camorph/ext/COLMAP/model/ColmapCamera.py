class ColmapCamera:
    cam_id: int
    type: str
    res: (float, float)
    params: []

    def __init__(self, cam_id, type, res, params):
        self.cam_id = cam_id
        self.type = type
        self.res = res
        self.params = params
