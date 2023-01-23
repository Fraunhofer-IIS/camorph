from os import listdir


def peek(f, length):
    """
    This function peeks if the file can be read for a given length.

    :param f: File handle
    :param length: Length
    :return: bytes or str
    """
    pos = f.tell()
    peeked = f.read(length)
    f.seek(pos)
    return peeked

def extension(path: str) -> str:
    """
    This function returns the extension of a filename.
    :param path: Filename
    :type path: str
    :return: str
    """
    return path[path.rfind('.'):]

def get_files_in_dir(path: str, extension = None):
    """
    This function returns all files in a given directory with an optional extension match.
    :param path: Path to directory
    :type path: str
    :param extension: Optional extension
    :type extension: str
    :return: list[str]
    """
    if extension is None:
        return [f for f in listdir(path)]
    else:
        return [f for f in listdir(path) if f.endswith(extension)]

def fixed_list(ilist, length, optype = None):
    """
    This function returns a list of a fixed length, regardless of number of elements in the input list.
    If the list is shorter than the length parameter, it will be padded with the default value for this type.
    When the list is empty, an optype has to be supplied.
    For example:
    >>> ilist = list[1.0]
    >>> fixed_list(ilist, 3)
    returns [1.0,0.0,0.0]

    :param ilist: List to extend or truncate
    :param length: Desired output length
    :param optype: When ilist is empty, this is the type with which the list is filled.
    :return: list[any]
    """
    if ilist is None or len(ilist) == 0:
        if optype is not None:
            rlist = [optype()]
        else:
            raise Exception("If list is None or empty, a basetype must be supplied")
    else:
        rlist = ilist.copy()
    eltype = type(rlist[0])
    listlen = len(rlist)
    if listlen >= length:
        return rlist[:length]
    else:
        rlist.extend([eltype() for x in range(length - listlen)])
        return rlist
