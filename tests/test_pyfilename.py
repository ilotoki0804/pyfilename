import pytest
from pyfilename import (
    NOT_ALLOWED_CHARS,
    NOT_ALLOWED_NAMES,
    NOT_ALLOWED_NAMES_WIN11,
    REVERSE_FULLWIDTH_TABLE,
    TRANSLATION_TABLE_FULLWIDTH,
    is_creatable,
    is_name_reserved,
    is_name_safe,
    sanitize,
    unsanitize,
)


def test_is_name_reserved():
    assert is_name_reserved("NUL")
    assert is_name_reserved("NUL.txt")
    assert is_name_reserved("NUL.hello.world")
    assert is_name_reserved("nUl.txt")
    assert is_name_reserved("COM¹")
    assert is_name_reserved("COM¹.txt")
    assert is_name_reserved("COM¹.hello.world")
    assert is_name_reserved("CoM1.txt")
    assert is_name_reserved("CoM0.txt")
    assert is_name_reserved("COM0.")
    assert not is_name_reserved("hello")
    assert not is_name_reserved("NUL.txt", strict=False)
    assert not is_name_reserved("COM¹.hello.world", strict=False)
    assert not is_name_reserved("COM¹.hello.world", strict=False)
    assert not is_name_reserved("COM0", strict=False)


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
    assert is_name_safe("hello.txt")
    assert is_name_safe("   hello.txt", strict=False)
    assert not is_name_safe("")
    assert not is_name_safe("hello.txt ")
    assert not is_name_safe("hello.txt.")
    assert not is_name_safe("hello.txt.  . ...  ")
    assert not is_name_safe("   hello.txt")


def test_unsanitize():
    assert unsanitize("⧵／：＊？＂＜＞∣．txt") == '\\/:*?"<>|.txt'


def test_sanitize():
    assert sanitize("hello.txt") == "hello.txt"
    assert sanitize("hello?.txt.") == "hello？.txt．"
    assert sanitize("          hello?.txt.") == "hello？.txt．"
    assert sanitize("   ... . . .   . .   . ", when_empty=None) == "... . . .   . .   ．"
    assert sanitize("   ... . . .   . .   . ", following_dot="remove", when_empty=None) is None
    assert sanitize("   ????hello.????txt", mode="char", when_empty=None) == "hello.    txt"
    assert sanitize("   ????hello.????txt...........", mode="char", replacement_char=";") == ";;;;hello.;;;;txt..........;"
    assert sanitize("   ????hello.????txt...........", mode="fullwidth", following_dot="char", replacement_char=";") == "？？？？hello.？？？？txt..........;"
    assert sanitize("   ????hello.????txt", mode="remove", when_empty=None) == "hello.txt"
    assert sanitize("   ????hello.????txt....", mode="remove", following_dot="no_correct", when_empty=None) == "hello.txt...."
    assert sanitize("NUL.   ????hello.????txt....", mode="remove", following_dot="no_correct", when_reserved=lambda name: f"The name is reserved. Sorry! Original name: {name}") == "The name is reserved. Sorry! Original name: NUL.   hello.txt...."

    with pytest.raises(TypeError):
        sanitize("hello?.txt.", mode="any")  # type: ignore
    with pytest.raises(TypeError):
        sanitize("hello?.txt.", following_dot="any")  # type: ignore

    assert sanitize("NUL", when_empty=123, when_reserved=lambda name: 345) == 345
    assert sanitize("   ... . . .   . .   . ", mode="remove", when_empty=None) is None
    assert sanitize("", when_empty="empty") == "empty"
    assert sanitize("", when_empty="empty") == "empty"
    assert sanitize("", when_empty=None) is None
    assert sanitize("", when_empty=123) == 123
