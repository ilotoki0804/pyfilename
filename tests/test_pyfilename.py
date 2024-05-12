import pytest

from pyfilename import (
    convert,
    is_creatable,
    is_reserved,
    is_safe,
    revert,
)

# fmt: off


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
    assert not is_creatable("")
    assert not is_creatable(" ...   ....  .")
    assert not is_creatable(".. ? .... .. .   ")
    assert not is_creatable("NUL.txt")
    assert not is_creatable("NUL.")
    assert is_creatable("NUL.txt", strict=False)


def test_is_name_safe():
    assert is_safe("hello.txt")
    assert is_safe("   hello.txt", strict=False)
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
