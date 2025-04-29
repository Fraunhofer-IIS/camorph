import sys

# sys.path.append('<project directory>')
# sys.path.append("../..")  # Adds higher directory to python modules path.

import camorph.lib.utils.bin_reader_utils as BinaryFileUtils
import camorph.lib.utils.file_utils as FileUtils
from ..model import *

primitive_type_size = {
    'Y': lambda f: BinaryFileUtils.read_int16(f),
    'C': lambda f: BinaryFileUtils.read_bool(f),
    'I': lambda f: BinaryFileUtils.read_int32(f),
    'F': lambda f: BinaryFileUtils.read_float32(f),
    'D': lambda f: BinaryFileUtils.read_float64(f),
    'L': lambda f: BinaryFileUtils.read_int64(f)
}

supported_nodes = ['Objects', 'Connections', 'Model', 'C', 'P', 'Properties70', 'Definitions', 'NodeAttribute',
                   'Geometry', 'GlobalSettings', 'ObjectType', 'PropertyTemplate', 'TypeFlags', 'Texture', 'FileName']

# syntactic helpers
def read_header(f):
    head_1 = BinaryFileUtils.read_string(f, 21)
    head_2 = f.read(2)
    head_3 = BinaryFileUtils.read_uint32(f)
    return [head_1, head_2, head_3]


def read_node_record(f, file_size, FBXVersion, depth=0):
    nested_obj = FBXNode()
    if (file_size - f.tell()) < 200:  # TODO magic fbx footer number
        f.read(file_size - f.tell())
        return [None, '']
    # read node header
    if FBXVersion < 7500:
        offset = BinaryFileUtils.read_uint32(f)
        num_properties = BinaryFileUtils.read_uint32(f)
        property_list_len = BinaryFileUtils.read_uint32(f)
    else:
        offset = BinaryFileUtils.read_uint64(f)
        num_properties = BinaryFileUtils.read_uint64(f)
        property_list_len = BinaryFileUtils.read_uint64(f)
    name_len = BinaryFileUtils.read_uint8(f)
    name = BinaryFileUtils.read_string(f, name_len)

    # skip all records that are not supported
    if name not in supported_nodes and offset != 0:
        curpos = f.tell()
        to_read = offset - curpos
        f.read(to_read)
        return [None, '']

    # ignoring Geometry attributes, just reading for connections
    elif name == 'Geometry':
        naid = read_property(f)
        natype = read_property(f)
        naname = read_property(f)
        curpos = f.tell()
        to_read = offset - curpos
        f.read(to_read)
        p = FBXNodeObject(name, naid, natype, naname, None)
        return [p, naid]

    # handling supported fbx objects
    elif name in ['NodeAttribute', 'Texture', 'Model']:
        naid = read_property(f)
        natype = read_property(f)
        naname = read_property(f)
        for i in range(3, num_properties):
            read_property(f)
        read_child_records(f, offset, file_size, depth, nested_obj, FBXVersion)
        p = FBXNodeObject(name, naid, natype, naname, nested_obj)
        return [p, naid]

    # handling first level nodes
    elif name in ['Objects', 'Connections']:
        for i in range(0, num_properties):
            read_property(f)

        read_child_records(f, offset, file_size, depth, nested_obj, FBXVersion)
        return [nested_obj, name]

    # handling special nested nodes
    elif name == "P":
        # read P header
        pname = read_property(f)
        ptype = read_property(f)
        read_property(f)  # unknown
        read_property(f)  # unknown
        pvalue = []
        for i in range(4, num_properties):
            pvalue.append(read_property(f))
        p = FBXProperty(pname, ptype, pvalue)
        return [p, p.pname]

    elif name == "C":
        ctype = read_property(f)
        cnames = []
        for x in range(1, num_properties):
            cnames.append(read_property(f))
        return ['connect', FBXConnection(ctype, cnames)]

    elif name == 'PropertyTemplate':
        pname = read_property(f)
        # default handling for unsupported nodes
        props = []
        for i in range(1, num_properties):
            props.append(read_property(f))

        read_child_records(f, offset, file_size, depth, nested_obj, FBXVersion)
        nested_obj['props'] = props
        nested_obj['pname'] = pname
        return [nested_obj, name]
    else:
        # default handling for unsupported nodes
        props = []
        for i in range(0, num_properties):
            # props.append(self.read_property(f))
            props.append(read_property(f))

        read_child_records(f, offset, file_size, depth, nested_obj, FBXVersion)
        nested_obj['props'] = props
        nested_obj['name'] = name
        return [nested_obj, name]


def read_child_records(f, offset, file_size, depth, nested_obj, FBXVersion):
    # only way to check if nested_list is set is to check
    # if the offset is longer than the current position
    cur_pos = f.tell()
    endlen = 13 if FBXVersion < 7500 else 25
    endbytes = b''.join([b'\x00' for x in range(endlen)])
    while cur_pos < offset:
        if FileUtils.peek(f, endlen) == endbytes and offset - cur_pos <= endlen:
            f.read(endlen)
            cur_pos = offset
            break
        [second_level_obj, second_level_name] = read_node_record(f, file_size, FBXVersion, depth + 1)
        cur_pos = f.tell()
        if second_level_obj is not None:
            if not str(second_level_name) in nested_obj:
                nested_obj[second_level_name] = []
            nested_obj[second_level_name].append(second_level_obj)


def read_property(f):
    prop_type = BinaryFileUtils.read_string(f, 1)
    # simple primitives
    if prop_type in primitive_type_size:
        value = primitive_type_size[prop_type](f)

    # arrays
    elif prop_type in array_type_size:
        array_length = BinaryFileUtils.read_uint32(f)
        encoding = BinaryFileUtils.read_uint32(f)
        compressed_length = BinaryFileUtils.read_uint32(f)
        if encoding == 0:
            value = f.read(array_length * array_type_size[prop_type])
        else:
            value = f.read(compressed_length)

    # raw binary data
    elif prop_type == 'R':
        length = BinaryFileUtils.read_uint32(f)
        value = f.read(length)

    # string
    elif prop_type == 'S':
        length = BinaryFileUtils.read_uint32(f)
        if length == 0:
            value = ""
        prop_str = BinaryFileUtils.read_string(f, length)
        value = prop_str

    else:
        raise Exception('unkown fbx property type ' + prop_type)

    return value


def read_property_debug(f, depth, debug_text):
    prop_type = BinaryFileUtils.read_string(f, 1)
    # simple primitives
    if prop_type in primitive_type_size:
        value = primitive_type_size[prop_type](f)

    # arrays
    elif prop_type in array_type_size:
        array_length = BinaryFileUtils.read_uint32(f)
        encoding = BinaryFileUtils.read_uint32(f)
        compressed_length = BinaryFileUtils.read_uint32(f)
        if encoding == 0:
            value = f.read(array_length * array_type_size[prop_type])
        else:
            value = f.read(compressed_length)

    # raw binary data
    elif prop_type == 'R':
        length = BinaryFileUtils.read_uint32(f)
        value = f.read(length)

    # string
    elif prop_type == 'S':
        length = BinaryFileUtils.read_uint32(f)
        if length == 0:
            value = ""
        prop_str = BinaryFileUtils.read_string(f, length)
        value = prop_str

    else:
        raise Exception('unkown fbx property type ' + prop_type)

    debug_offset = "".join(["   " for x in range(0,depth)])
    #print(debug_offset+prop_type)
    debug_text.append(debug_offset+prop_type)
    #print(debug_offset+str(value))
    debug_text.append(debug_offset+str(value))
    return value, debug_text
