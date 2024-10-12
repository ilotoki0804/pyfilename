import pytest

from pyfilename import (
    convert,
    is_creatable,
    is_reserved,
    revert,
)
from pyfilename import (
    is_safe as _is_safe,
)

# fmt: off

def check_validity_in_covert_too(func):
    def inner(path, *args, **kwargs):
        assert _is_safe(convert(path))
        return func(path, *args, **kwargs)
    return inner

is_reserved = check_validity_in_covert_too(is_reserved)
is_creatable = check_validity_in_covert_too(is_creatable)
is_safe = check_validity_in_covert_too(_is_safe)


def test_isreserved_testcase():
    # source: https://github.com/python/cpython/blob/16be8db6bec7bf8b58df80601cab58a26eee4afa/Lib/test/test_ntpath.py#L985
    # assert is_safe('')
    # assert is_safe('.')
    # assert is_safe('..')
    # assert is_safe('/')
    # assert is_safe('/foo/bar')
    assert not is_safe('foo.')
    assert not is_safe('foo ')
    assert not is_safe('\foo')
    assert not is_safe('foo*bar')
    assert not is_safe('foo?bar')
    assert not is_safe('foo"bar')
    assert not is_safe('foo<bar')
    assert not is_safe('foo>bar')
    assert not is_safe('foo:bar')
    assert not is_safe('foo|bar')
    assert not is_safe('nul')
    assert not is_safe('aux')
    assert not is_safe('prn')
    assert not is_safe('con')
    assert not is_safe('conin$')
    assert not is_safe('conout$')
    assert not is_safe('COM1')
    assert not is_safe('LPT9')
    assert not is_safe('com\xb9')
    assert not is_safe('com\xb2')
    assert not is_safe('lpt\xb3')
    assert not is_safe('NUL.txt')
    assert not is_safe('PRN  ')
    assert not is_safe('AUX  .txt')
    assert not is_safe('COM1:bar')
    assert not is_safe('LPT9   :bar')
    assert is_safe('bar.com9')
    assert is_safe('bar.lpt9')
    assert not is_safe('c:/bar/baz/NUL')
    assert not is_safe('c:/NUL/bar/baz')
    # assert is_safe('//./NUL')
    # assert is_safe(b'')
    # assert is_safe(b'.')
    # assert is_safe(b'..')
    # assert is_safe(b'/')
    # assert is_safe(b'/foo/bar')
    # assert not is_safe(b'foo.')
    # assert not is_safe(b'nul')

def test_is_name_reserved():
    assert is_reserved("NUL")
    assert is_reserved("NUL.txt")
    assert is_reserved("NUL.hello.world")
    assert is_reserved("nUl.txt")
    assert is_reserved("COM¹")
    assert is_reserved("COM¹.txt")
    assert is_reserved("COM¹.hello.world")
    assert is_reserved("CoM1.txt")
    assert is_reserved("CoM0.txt")
    assert is_reserved("CoM1   .txt")
    assert is_reserved("COM0.")
    assert not is_reserved("hello/world")
    assert not is_reserved("hello\0world")
    assert not is_reserved("CoM1   txt")
    assert not is_reserved("CoM0   .txt")
    assert not is_reserved("hello")
    assert not is_reserved("NUL.txt", strict=False)
    assert not is_reserved("COM¹.hello.world", strict=False)
    assert not is_reserved("COM¹.hello.world", strict=False)
    assert not is_reserved("COM0", strict=False)


def test_is_creatable():
    assert is_creatable("hello.txt")
    assert is_creatable("hello")
    assert is_creatable("안녕하세요")
    assert is_creatable("안녕하세요  ")
    assert is_creatable("안녕하세요  ...  ")
    assert is_creatable("NUL.txt", strict=False)
    assert not is_creatable("")
    assert not is_creatable(" ...   ....  .")
    assert not is_creatable(".. ? .... .. .   ")
    assert not is_creatable("NUL.txt")
    assert not is_creatable("NUL.")


def test_is_name_safe():
    assert is_safe("hello.txt")
    assert is_safe("   hello.txt", strict=False)
    assert not is_safe("hello?.world")
    assert not is_safe("")
    assert not is_safe("hello.txt ")
    assert not is_safe("hello.txt.")
    assert not is_safe("hello.txt.  . ...  ")
    assert not is_safe("   hello.txt")


def test_unsanitize():
    assert revert("⧵／：＊？＂＜＞∣．txt") == '\\/:*?"<>|.txt'


def test_sanitize():
    assert convert("hello.txt") == "hello.txt"
    assert convert("hello?.txt.") == "hello？.txt．"
    assert convert("          hello?.txt.") == "hello？.txt．"
    assert convert("   ... . . .   . .   . ", when_empty=None) == "... . . .   . .   ．"
    assert convert("   ... . . .   . .   . ", following_dot="remove", when_empty=None) is None
    assert convert("   ????hello.????txt", mode="char", when_empty=None) == "hello.    txt"
    assert convert("   ????hello.????txt...........", mode="char", replacement_char=";") == ";;;;hello.;;;;txt..........;"
    assert convert("   ????hello.????txt...........", mode="fullwidth", following_dot="char", replacement_char=";") == "？？？？hello.？？？？txt..........;"
    assert convert("   ????hello.????txt", mode="remove", when_empty=None) == "hello.txt"
    assert convert("   ????hello.????txt....", mode="remove", following_dot="no_correct", when_empty=None) == "hello.txt...."
    assert convert("NUL.   ????hello.????txt....", mode="remove", following_dot="no_correct", when_reserved=lambda name: f"The name is reserved. Sorry! Original name: {name}") == "The name is reserved. Sorry! Original name: NUL.   hello.txt...."

    with pytest.raises(TypeError):
        convert("hello?.txt.", mode="any")  # type: ignore
    with pytest.raises(TypeError):
        convert("hello?.txt.", following_dot="any")  # type: ignore

    assert convert("NUL", when_empty=123, when_reserved=lambda name: 345) == 345
    assert convert("   ... . . .   . .   . ", mode="remove", when_empty=None) is None
    assert convert("", when_empty="empty") == "empty"
    assert convert("", when_empty="empty") == "empty"
    assert convert("", when_empty=None) is None
    assert convert("", when_empty=123) == 123
