import struct


def get_uint8(i: int) -> bytes:
    """
    This function encodes an integer to a uint8
    :param i: Integer
    :return: bytes
    """
    return i.to_bytes(1, 'little')


def get_uint32(i: int) -> bytes:
    """
    This function encodes an integer to a uint32
    :param i: Integer
    :return: bytes
    """
    return i.to_bytes(4, 'little')


def get_uint64(i: int) -> bytes:
    """
    This function encodes an integer to a uint64
    :param i: Integer
    :return: bytes
    """
    return i.to_bytes(8, 'little')


def get_int16(i: int) -> bytes:
    """
    This function encodes an integer to a int16
    :param i: Integer
    :return: bytes
    """
    return i.to_bytes(2, 'little', signed=True)


def get_int32(i: int) -> bytes:
    """
    This function encodes an integer to a int32
    :param i: Integer
    :return: bytes
    """
    return i.to_bytes(4, 'little', signed=True)


def get_int64(i: int) -> bytes:
    """
    This function encodes an integer to a int64
    :param i: Integer
    :return: bytes
    """
    return i.to_bytes(8, 'little', signed=True)


def get_float32(f: float) -> bytes:
    """
    This function encodes an float to a float32
    :param f: Float
    :return: bytes
    """
    return bytearray(struct.pack('<f', f))


def get_float64(f: float) -> bytes:
    """
    This function encodes an float to a float64
    :param f: Float
    :return: bytes
    """
    return bytearray(struct.pack('<d', f))


def get_bool(b: bool) -> bytes:
    """
    This function encodes a bool to bytes
    :param b: Bool
    :return: bytes
    """
    i = 1 if b == True else 0
    return i.to_bytes(1, 'little')


def get_string(s: str) -> bytes:
    """
    This function encodes a string to bytes
    :param s: String
    :return: bytes
    """
    if len(s) == 0:
        return b''
    return bytearray(s, 'Ascii')
