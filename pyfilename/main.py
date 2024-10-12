from __future__ import annotations

from typing import Callable, Literal, TypeVar, overload

T = TypeVar("T")

TRANSLATION_TABLE_FULLWIDTH = {i: 0 for i in range(32)} | str.maketrans('\\/:*?"<>|', "⧵／：＊？＂＜＞∣")
TRANSLATION_TABLE = {i: 0 for i in range(32)} | str.maketrans('\\/:*?"<>|', "\x00" * 9)
FORBIDDEN_CHARS = set('\\/:*?"<>|').union(chr(i) for i in range(32))
FULLWIDTH_TABLE_REVERT = str.maketrans("⧵／：＊？＂＜＞∣．", '\\/:*?"<>|.')

# check https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file
RESERVED_WIN11 = {
    "CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$",
    "COM1", "COM¹", "COM2", "COM²", "COM3", "COM³", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT¹", "LPT2", "LPT²", "LPT3", "LPT³", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
}  # fmt: skip
RESERVED = RESERVED_WIN11 | {"COM0", "LPT0"}


def is_reserved(name: str, strict: bool = True) -> bool:
    """이 함수는 이름이 예약어에 해당하는지 확인합니다.

    윈도우에서는 금지 문자가 포함되어 있지 않더라도
    일부 이름을 파일명으로 사용하지 못하도록 정해놓았는데, 이를 예약어라고 합니다.
    이 예약어에는 대표적으로 `NUL`, `COM`, `LPT1~9` 등이 있습니다.

    이 함수가 **True를 반환할 때** 예약어로, 파일명으로 사용할 수 **없습니다**.

    윈도우에서 예약어로 처리되는 경우는 주로 다음과 같습니다.
    * 예약어와 정확히 일치하는 경우. 이때 대소문자는 구분되지 않으며 대소문자가 섞이더라도 무관.
    * (윈도우 10의 경우, strict=True일때 확인됨) 예약어로 시작해서 예약어 바로 뒤에 마침표나 스페이스가 오는 경우.

    Args:
        name: 예약어인지 확인할 파일명입니다.
        strict: 윈도우 10을 포함한 모든 버전에서 예약어 확인을 하는 경우 True, 윈도우 11에서의 예약어 확인을 하는 경우 False를 사용하세요.
            윈도우 10과 11은 예약어 처리에서 아주 약간의 변화가 있는데, 윈도우 11에서 일부 제한이 완화되었습니다.
            strict가 True라면 윈도우 10에서 예약어로 분류하면 True를 반환하고,
            strict가 False일 경우 윈도우 10에서 예약어로 분류하더라도 윈도우 11에서 예약어가 아니면 False를 반환합니다.
            또한 위에서 설명되었듯이 윈도우 11에서는 예약어로 시작해서 예약어 바로 뒤에 마침표가 오는 경우도 따로 검사하지 않습니다.
            윈도우 10을 사용하는 다른 컴퓨터들과의 호환성을 위해 항상 True로 두는 것을 추천합니다.
    """
    if strict:
        processed_name = name.partition(".")[0].strip(" ").upper()
        if processed_name in RESERVED:
            # COM0과 LPT0는 뒤에 스페이스가 오는 경우에는 전혀 알 수 없는 이유로 생성을 허용함(???)
            if processed_name in {"COM0", "LPT0"}:
                return len(name) <= 4 or name[4] == "."
            return True

        return False

    return name.upper().rstrip(". ") in RESERVED_WIN11


def is_creatable(name: str, strict: bool = True) -> bool:
    """주어진 이름이 파일명이나 폴더명으로 설정되었을 때 오류 없이 생성되는지 확인합니다.

    이 함수를 이용하는 경우 오류는 일어나지 않지만 자신이 설정한 파일명과는
    다른 이름을 가진 파일이 생성될 수 있다는 점을 주의하세요.
    만약 자신이 설정한 파일명과 같은 이름의 파일이 생성될지 여부가 궁금하다면 `is_safe`를 이용해 주세요.

    윈도우에서 생성되지 않는 파일명의 종류는 다음과 같습니다.

    * 예약어류인 경우.
    * 이름이 끝의 마침표와 스페이스를 삭체 처리한 후 비어 있는 경우.
    * 허용되지 않는 문자가 포함된 경우.

    Args:
        name: 확인할 파일명입니다.
        strict: 윈도우 10과 11에서 모두 생성 가능한지 확인합니다.
            윈도우 11을 사용하더라도 다른 컴퓨터와의 호환성을 유지하기 위해 이 값은 True로 두는 것을 권장합니다.
    """
    if is_reserved(name, strict):
        return False

    name_chars = set(name)

    if name_chars <= {".", " "}:
        return False

    return not name_chars & FORBIDDEN_CHARS


def is_safe(name: str, strict: bool = True) -> bool:
    """주어진 이름이 파일 이름으로 사용하기에 적절한지 확인합니다.

    이때 파일명은 변경되지 않고 그대로 생성됩니다.
    만약 파일명이 변경될 가능성이 있더라도 생성되기만 해도 된다면 `is_creatable`을 사용하세요.

    윈도우에서 다음과 같은 조건들은 충족할 경우 파일명이 변경되지 않고 그대로 생성됩니다.

    * 예약어류가 아닌 경우.
    * 이름이 끝의 마침표와 스페이스를 삭체 처리한 후 비어 있지 않은 경우.
    * 허용되지 않는 문자가 포함된 경우.
    * 이름이 마침표나 스페이스로 끝나지 않는 경우.
    * (윈도우 10의 경우, strict=True일때 확인됨) 스페이스로 시작하지 않는 경우.

    Args:
        name: 확인할 파일명입니다.
        strict: 윈도우 10의 조금 더 강력한 예약어 사용 제한을 사용하고, 이름 앞에 스페이스가 오는 것을 허용합니다.
            윈도우 11을 사용하더라도 다른 컴퓨터와의 호환성을 유지하기 위해 이 값은 True로 두는 것을 권장합니다.
    """
    if not name:
        return False

    if strict and name[0] == " ":
        return False

    if name[-1] in (".", " "):
        return False

    return is_creatable(name, strict)


def revert(name: str) -> str:
    """`convert`에서 `"fullwidth"` 모드를 통해 바뀐 안전한 파일명을 다시 원본 파일명으로 변경합니다.

    전각 문자의 경우 잘 원본으로 변환되지만 replace_char로 변경된 제어 문자의 경우는 다시 변경이 불가능합니다.

    Args:
        name: 원본 파일명으로 되돌릴 안전한 파일명입니다.
    """
    return name.translate(FULLWIDTH_TABLE_REVERT)


@overload
def convert(
    name: str,
    replacement_char: str = " ",
    mode: Literal["fullwidth", "char", "remove"] = "fullwidth",
    *,
    strict: bool = True,
    following_dot: Literal["fullwidth", "char", "remove", "no_correct"] | None = None,
    when_reserved: Callable[[str], str] = lambda name: "_" + name,
    when_empty: str = "_",
) -> str: ...  # pragma: no cover


@overload
def convert(
    name: str,
    replacement_char: str = " ",
    mode: Literal["fullwidth", "char", "remove"] = "fullwidth",
    *,
    strict: bool = True,
    following_dot: Literal["fullwidth", "char", "remove", "no_correct"] | None = None,
    when_reserved: Callable[[str], T] = lambda name: "_" + name,
    when_empty: str | T = "_",
) -> str | T: ...  # pragma: no cover


def convert(
    name: str,
    replacement_char: str = " ",
    mode: Literal["fullwidth", "char", "remove"] = "fullwidth",
    *,
    strict: bool = True,
    following_dot: Literal["fullwidth", "char", "remove", "no_correct"] | None = None,
    when_reserved: Callable[[str], T] = lambda name: "_" + name,
    when_empty: str | T = "_",
) -> str | T:
    r"""파일명 혹은 디렉토리명에 사용할 수 없는 글자를 사용할 수 있는 글자로 변경합니다.

    주의: 이 함수는 파일 *경로*(슬래시가 포함된 `path/to/file.txt` 같은 문자열)를 처리하도록 제작되지 않았습니다.

    주의: 부분적인 파일명보다는 전체 파일명을 함수에 입력하는 것을 강력히 권장합니다.
    부분적인 파일명을 입력했을 때는 필요 없는 제한 우회가 들어가거나 전체 합쳐졌을 때 문제가 있는 파일명이 생길 수 있기 때문입니다.
    예를 들어 `"file: " + pf.convert(unsafe) + ".txt"`보다는 `pf.convert("file: " + unsafe + ".txt")`가 훨씬 낫습니다.

    Args:
        name: 변환할 파일 혹은 디렉토리의 이름입니다.
        mode: 사용할 수 없는 문자를 맏닥뜨렸을 때 해당 문자를 처리할 방식을 결정합니다.
            아래 모드들은 제어 문자와 일부 특수문자들을 어떻게 처리할지를 결정합니다.
            "fullwidth" (기본값): 가능한 문자를 전각 문자로 변경하고 대응하는 전각 문자가 없는 경우 `replacement_char`로 교체합니다.
                사용할 수 있는 문자는 제어 문자와 일부 특수문자가 있습니다.
                제어 문자는 특수한 목적을 위해 남아있는 문자이고, 일부 특수문자는 시스템에서 사용하기 위한 요량으로
                사용자가 해당 문자를 사용하는 것을 금지한 문자들입니다.
                윈도우에서 사용할 수 없는 특수문자에 해당하는 문자에는 슬래시/백슬래시/콜론/별표/물음표/쌍따옴표/부등호/수직선(절댓값 기호)가 있습니다.
                그러나 이 제한은 반각 문자에만 해당하며, 전각 문자의 경우 윈도우에서 파일명으로 문제 없이 사용할 수 있습니다.
                예를 들어 반각 `?`은 윈도우에서 파일명에서 사용할 수 없지만, 전각 `？`은 사용할 수 있습니다.
                따라서 이러한 특수문자들을 전각으로 전환하는 것이 "fullwidth" 모드입니다.
                단, 별도의 전각 대응 문자가 없는 제어 문자는 `replacement_char`로 교체됩니다.
            "char": 모든 사용할 수 없는 문자를 `replacement_char`로 교체합니다.
            "remove": 모든 사용할 수 없는 문자를 문자열에서 삭제합니다.
        replacement_char: 기본적으로 사용할 수 없는 문자를 대신해 사용되는 문자인데, `mode`에 따라 양상이 살짝 다르게 나타납니다.
            `mode`가 "char"인 경우: 윈도우에서 파일명으로 포함될 수 없는 문자가 대체 문자로 대체됩니다.
            `mode`가 "fullwidth"인 경우: 제어 문자와 같은 경우 윈도우에서 파일명으로 쓰일 수 없음과 동시에
                대응하는 전각 문자가 없습니다. 따라서 제어 문자의 경우 이 대체 문자로 대체됩니다.
        following_dot: 파일 이름 맨 마지막에는 마침표가 올 수 없기에 이를 어떻게 처리할지를 결정합니다.
            None (기본값): `mode`로 설정된 값과 `following_dot`의 설정값을 일치시킵니다.
                만약 mode가 "fullwidth"라면 "fullwidth"가, "char"일 경우 "char"가,
                "remove"일 경우 "remove"가 선택됩니다.
            "fullwidth": 맨 끝에 있는 마침표를 전각 마침표 `．`로 변경합니다.
            "char": 맨 끝에 있는 마침표를 `replacement_char`로 설정된 문자로 교체합니다.
                단, `replacement_char`가 마침표거나 스페이스일 경우 "remove"와 같은 역할을 합니다.
            "remove": 맨 끝에 있는 마침표를 제거합니다. 윈도우가 기본적으로 하는 작업과도 일치합니다.
            "no_correct": 만약 이름 뒤에 확장자나 다른 문자열이 추가될 예정이라면 마침표를 굳이 수정할 필요가 없습니다.\
                그러한 경우 "no_correct"를 사용하면 추가적인 문자열 변형 없이 정상적으로 파일명을 결정할 수 있습니다.
        when_reserved: 문자열을 처리한 결과 예약어라면 어떻게 처리할지 결정합니다.
            예약어에 대해서는 `is_reserved`의 문서를 확인해 보세요.
            **주의**: 이 함수로 처리된 결과가 안전한 이름인지 꼭 확인해 보세요. `when_reserved` 함수의 결과는 별도로 모니터되지 않습니다.
        when_empty: 문자열을 처리한 결과가 빈 문자열일 경우 어떻게 처리할지 결정합니다.
            이 함수는 when_empty의 값이 안전한지를 별도로 검사하지 않습니다.
            when_empty에 속한 문자열이 문자열에서 사용 가능한지 반드시 확인해 보세요.
            만약 확신하지 못한다면 반드시 when_empty의 문자열을 convert하세요.
    """
    name = (
        name.translate(TRANSLATION_TABLE_FULLWIDTH if mode == "fullwidth" else TRANSLATION_TABLE)
        .replace("\x00", "" if mode == "remove" else replacement_char)
        .rstrip()
    )

    if name.endswith("."):
        following_dot = following_dot or mode
        if following_dot == "no_correct":
            pass
        elif (
            following_dot == "remove"
            or following_dot == "char"
            and (not replacement_char or replacement_char in ". ")
        ):
            name = name.rstrip(". ")
        elif following_dot == "fullwidth":
            name = name.removesuffix(".") + "．"
        elif following_dot == "char":
            name = name.removesuffix(".") + replacement_char
        else:
            if mode not in {"fullwidth", "char", "remove"}:
                raise TypeError(f"Unknown option for `mode`: {mode!r}")
            else:
                raise TypeError(f"Unknown option for `following_dot`: {following_dot!r}")

    if strict:
        name = name.lstrip(" ")

    if is_reserved(name, strict):
        return when_reserved(name)

    return name or when_empty
