import struct


def read_uint8(f):
    """
    This function reads a uint8 from a file
    :param f: File handle
    :return: int
    """
    bytes = f.read(1)
    return int.from_bytes(bytes, 'little')


def read_uint32(f):
    """
    This function reads a uint32 from a file
    :param f: File handle
    :return: int
    """
    bytes = f.read(4)
    return int.from_bytes(bytes, 'little')

def read_uint64(f):
    """
    This function reads a uint64 from a file
    :param f: File handle
    :return: int
    """
    bytes = f.read(8)
    return int.from_bytes(bytes, 'little')

def read_int16(f):
    """
    This function reads a in16 from a file
    :param f: File handle
    :return: int
    """
    bytes = f.read(2)
    return int.from_bytes(bytes, 'little', signed=True)


def read_int32(f):
    """
    This function reads a int32 from a file
    :param f: File handle
    :return: int
    """
    bytes = f.read(4)
    return int.from_bytes(bytes, 'little', signed=True)


def read_int64(f):
    """
    This function reads a int64 from a file
    :param f: File handle
    :return: int
    """
    bytes = f.read(8)
    return int.from_bytes(bytes, 'little', signed=True)


def read_float32(f):
    """
    This function reads a float32 from a file
    :param f: File handle
    :return: float
    """
    bytes = f.read(4)
    return struct.unpack('<f', bytes)[0]


def read_float64(f):
    """
    This function reads a float64 from a file
    :param f: File handle
    :return: float
    """
    bytes = f.read(8)
    return struct.unpack('<d', bytes)[0]


def read_bool(f):
    """
    This function reads a bool from a file
    :param f: File handle
    :return: bool
    """
    bytes = f.read(1)
    return int.from_bytes(bytes, 'little') == 1


def read_string(f, length, str_format='ascii'):
    """
    This function reads a string from a file
    :param f: File handle
    :return: str
    """
    bytes = f.read(length)
    return bytes.decode(str_format)
