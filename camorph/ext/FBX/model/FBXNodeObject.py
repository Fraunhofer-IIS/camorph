class FBXNodeObject:

    def __init__(self, name, pname, ptype, pvalue, nested_objects = None):
        self.name = name
        self.pname = pname
        self.ptype = ptype
        self.pvalue = pvalue
        if nested_objects is not None:
            for obj in nested_objects:
                setattr(self, obj, nested_objects[obj])