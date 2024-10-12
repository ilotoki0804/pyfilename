from ntpath import altsep, splitroot
from os import sep
import os

_reserved_chars = frozenset({chr(i) for i in range(32)} | {'"', "*", ":", "<", ">", "?", "|", "/", "\\"})

_reserved_names = frozenset(
    {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"}
    | {f"COM{c}" for c in "123456789\xb9\xb2\xb3"}
    | {f"LPT{c}" for c in "123456789\xb9\xb2\xb3"}
)


def isreserved(path):
    """Return true if the pathname is reserved by the system."""
    # Refer to "Naming Files, Paths, and Namespaces":
    # https://docs.microsoft.com/en-us/windows/win32/fileio/naming-a-file
    path = os.fsdecode(splitroot(path)[2]).replace(altsep, sep)
    return any(_isreservedname(name) for name in reversed(path.split(sep)))


def _isreservedname(name):
    """Return true if the filename is reserved by the system."""
    # Trailing dots and spaces are reserved.
    if name[-1:] in (".", " "):
        return name not in (".", "..")
    # Wildcards, separators, colon, and pipe (*?"<>/\:|) are reserved.
    # ASCII control characters (0-31) are reserved.
    # Colon is reserved for file streams (e.g. "name:stream[:type]").
    if _reserved_chars.intersection(name):
        return True
    # DOS device names are reserved (e.g. "nul" or "nul .txt"). The rules
    # are complex and vary across Windows versions. On the side of
    # caution, return True for names that may not be reserved.
    return name.partition(".")[0].rstrip(" ").upper() in _reserved_names


def test_is_name_reserved():
    assert isreserved("NUL")
    assert isreserved("NUL.txt")
    assert isreserved("NUL.hello.world")
    assert isreserved("nUl.txt")
    assert isreserved("COM¹")
    assert isreserved("COM¹.txt")
    assert isreserved("COM¹.hello.world")
    assert isreserved("CoM1.txt")
    assert isreserved("CoM1   .txt")
    assert isreserved("COM0.")
    assert isreserved("hello\0world")
    # assert isreserved("CoM0.txt")
    # assert isreserved("hello/world")
    # assert isreserved("CoM1   txt")
    # assert isreserved("CoM0   .txt")
    # assert isreserved("   hello.txt")


def test_is_creatable():
    assert isreserved("안녕하세요  ")
    assert isreserved("안녕하세요  ...  ")
    # assert isreserved("")
    assert isreserved(" ...   ....  .")
    assert isreserved(".. ? .... .. .   ")
    assert isreserved("NUL.txt")
    assert isreserved("NUL.")


def test_is_name_safe():
    assert not isreserved("hello.txt")
    assert isreserved("hello?.world")
    # assert isreserved("")
    assert isreserved("hello.txt ")
    assert isreserved("hello.txt.")
    assert isreserved("hello.txt.  . ...  ")
