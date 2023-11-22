# NTFS 예약어는 루트 디렉토리 (C:나 D: 등)에서 문제를 일으킬 수 있습니다.
# 하지만 사용성이 매우 적기에 포함하지는 않았습니다.
# 관련 링크: https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-fscc/b04c3bd0-79dc-4e58-b8ed-74f19fc2ea0a

# 리눅스의 경우에는 NULL과 slash를 제외하면 모든 것을 파일 이름으로 사용할 수 있습니다.
# 하지만 몇몇 기기들은 자체적으로 그 외의 이름에도 제한을 걸기도 합니다(삼성 갤럭시 등).

# import re
import functools
import html
# from typing import Literal
import logging
from pathlib import Path
# from typing import Final
from enum import Enum
import os
from typing import Callable

__all__ = (
    "TRANSLATE_TABLE_FULLWIDTH", "TRANSLATE_TABLE_REPLACEMENT", "NOT_ALLOWED_NAMES",
    # "DOT_REMOVE", "DOT_REPLACE", "DOT_NO_CORRECTION", "FOLLOWING_DOT_REPLACEMENT",
    # "MODE_FULLWIDTH", "MODE_USE_REPLACEMENT_CHAR", "MODE_REMOVE",
    # "CHAR_SPACE", "CHAR_DOUBLE_QUOTATION_MARK", "CHAR_WHITE_QUESTION_MARK", "CHAR_RED_QUESTION_MARK",
    "DotHandlingPolicy", "TextMode", "ReplacementCharacter",
    # "EmptyStringError",
    "is_name_safe", "get_original_name", "sanitize_path", "sanitize",
)

TRANSLATE_TABLE_FULLWIDTH = {i: 0 for i in range(32)} | str.maketrans('\\/:*?"<>|', '⧵／：＊？＂＜＞∣')
TRANSLATE_TABLE_REPLACEMENT = {i: 0 for i in range(32)} | str.maketrans('\\/:*?"<>|', '\x00' * 9)

# 출처: https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file
NOT_ALLOWED_NAMES_WIN11 = {
    "CON", "PRN", "AUX", "NUL",

    "COM1", "COM¹", "COM2", "COM²", "COM3", "COM³", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",

    "LPT1", "LPT¹", "LPT2", "LPT²", "LPT3", "LPT³", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
}
NOT_ALLOWED_NAMES = NOT_ALLOWED_NAMES_WIN11 | {'COM0', 'LPT0'}


class DotHandlingPolicy(Enum):
    remove = 'remove'
    replace = 'replace'
    do_not_correct = 'do_not_correct'


class TextMode(Enum):
    fullwidth = 'fullwidth'
    use_replacement_char = 'use_replacement_char'
    remove = 'remove'


class ReplacementCharacter(Enum):
    space = ' '
    double_question_mark = '⁇'
    white_question_mark = '❔'
    red_question_mark = '❓'


# class EmptyStringError(Exception):
#     pass


def is_name_reserved(
    name: str,
    strict: bool = True,
) -> bool:
    """이 함수는 이름이 예약어에 해당하는지 확인합니다.

    주의1: 이 함수는 해당 이름에 잘못된 글자가 쓰였는지와 같은 일반적인 부분은 확인하지 않습니다. 그러한 부분을 확인하려면
        translate_to_safe_name을 사용해야 합니다.
    주의2: 이 함수는 이름이 예약어가 인지 확인합니다. **True를 반환할 때** 사용할 수 없는 값입니다.

    윈도우 10/11의 예약어 제한은 다음과 같습니다.
    1. 윈도우 예약어와 일치하는가(대소문자 구분 없음)?
        이때 Windows 10에서는 COM0과 LPT0이 포함되지만 Windows 11의 일부 버전에서는 포함되지 않습니다.
    1. 예약어 뒤에 바로 마침표('.')가 오는가?
        Windows 10에서는 예약어 뒤에 바로 확장자가 오는 것을 금지합니다.
        예를 들어 COM20은 'COM2'라는 예약어 뒤에 마침표가 아닌 글자 '0'이 붙어 적절한 이름이지만,
        COM2.tar.bz는 예약어 뒤에 바로 마침표('.')가 오기에 적절하지 않은 이름입니다.
        예약어 뒤에 마침표가 온 뒤에는 사실 어떤 글자가 오더라도 부적절합니다.
        예를 들어 "Com1. Is the most great thing.txt'라는 파일명은 COM1 뒤에 '.'이 붙었기에 적절하지 않습니다.
        이 제한은 Windows 10에서만 포함되며 일부 Windows 11 버전에서는 이 제한이 완화된 것으로 보입니다.

    Args:
        name: 예약어인지 확인할 파일명입니다.
        strict_check:
            윈도우의 최근 버전에서는 예약어 관련 제한이 조금 완화된 것으로 보입니다.
            예약어 제한이 조금 풀어진 예약어 체크를 하고 싶다면 False로,
            Windows 10을 포함해서 모든 윈도우 버전에 대해서 예약어 충돌이 없도록 하려면 True로 설정하세요.
            윈도우 간에 파일을 옮기거나 Windows 10기반 컴퓨터를 쓰는 경우 생길 수 있는 충돌을 방지하기 위해
            항상 True로 두는 것을 권장하고, pyfilename의 모든 함수는 strict_check가 True인 상태를 사용합니다.
    """
    # sourcery skip: assign-if-exp
    reserved_names = NOT_ALLOWED_NAMES if strict else NOT_ALLOWED_NAMES_WIN11
    name_upper = name.upper()

    if name_upper in reserved_names:
        return True

    if not strict:
        return False

    if name_upper[:3] in reserved_names:
        return name_upper[3] == '.'

    if name_upper[:4] in reserved_names:
        return name_upper[4] == '.'

    return False


def is_name_safe(
    name: str,
    is_path: bool = False,
    creatable_check_only: bool = False,
    strict: bool = True,
) -> bool:
    r"""
    해당 이름이 파일 이름으로 사용하기에 적절한지 확인합니다.

    윈도우의 파일명 제약은 다음과 같습니다:
    1. 생성 자체가 불가능한 경우
        * 금지 문자 중 하나라도 포함하는가? (맞으면 파일명으로 사용 불가능; 금지어: `\/:*?"<>|`)
        * 예약어 중 하나인가? (맞으면 파일명으로 사용 불가능; 예약어는 NOT_ALLOWED_NAMES에서 확인 가능합니다.)
    1. 생성은 가능하지만 윈도우가 파일명을 수정하여 사용하는 경우
        * 이름이 마침표('.')로 끝나는가? (맞으면 윈도우가 맨 뒤에 붙은 .을 자동으로 제거함;
                                        이름 전체가 .이라면 PermissionError가 나며 생성이 불가)
        * 이름이 스페이스로 시작하거나 끝나는가? (맞으면 윈도우가 맨 뒤에 붙은 스페이스(' ')를 자동으로 제거함.
                                               윈도우 10이라면 맨 앞에 붙은 스페이스도 자동으로 제거함.)

    생성은 가능하지만 윈도우가 파일명을 수정하는 경우에는 파일을 생성한 후에
    os.listdir같은 걸로 파일의 존재 여부를 확인할 경우 다음과 같은 골치 아픈 시나리오가 생길 수 있습니다.
    ```python
    # 예제 1

    import os

    # 파일명 뒤에 .이 붙음; 나중에 os.listdir에서 filename이 결과에 없는 이유가 됨.
    filename = './hello.txt.'

    # 문제없이 잘 동작함. 하지만 사용자가 모르는 사이에 윈도우는 파일명 뒤의 '.'을 땜.
    with open(filename, 'w') as f:
        f.write('hello world')  # 실제로는 'hello.txt.'이 아닌 'hello.txt'에 저장됨.

    # 분명히 잘 저장은 되었는데도 불구하고 False가 출력결과로 나옴.
    print(filename in os.listdir('.'))  # 출력결과: False
    ```

    translate_to_safe_name을 이용하면 해당 문제를 피할 수 있습니다.
    ```python
    # 예제 2

    import os
    import pyfilename as pf

    # '통계적 확률에 대하여．'(반각 마침표 > 전각 마침표)로 변경.
    filename = pf.translate_to_safe_name('통계적 확률에 대하여.')

    os.mkdir(filename)

    # 제대로 결과값이 True로 나옴.
    print(filename in os.listdir('.'))  # 출력결과: True
    ```
    """
    str_table = {chr(chr_int) for chr_int in TRANSLATE_TABLE_REPLACEMENT}
    if is_path:
        str_table -= {'\\', '/'}

    if is_name_reserved(name, strict) or any(char in str_table for char in name):
        return False

    if creatable_check_only:
        return True

    if name.endswith('.') or name.endswith(' '):
        return False

    if not strict:  # sourcery skip
        return True

    return not name.startswith(' ')

    # ...or return translate_to_safe_name(name) == name  # 훨씬 느림


def get_original_name(
    name: str,
    remove_replacement_char: str | None = None,
    html_escape: bool = False,
    consecutive_char: str | None = None,
) -> str:
    """translate_to_safe_name을 통해 안전한 이름으로 바꾸었던 것을 다시 일반적인 문자열로 변경합니다.

    Args:
        name (str): 일반적인 문자열로 되돌릴 안전한 이름입니다.
        remove_replacement_char (str | None, optional): 만약 안전한 이름을 만들 때 사용했던 replacement_char가 있고 제거하고 싶다면 작성해 주세요.
            해당 문자가 replacement_char로 간주되며 삭제됩니다. None(기본값)이라면 않았다면 아무것도 바꾸지 않습니다. Defaults to None.
        html_escape (bool, optional): html unescape했던 것을 다시 되돌리고 싶다면 선택하세요. 만약 되돌리고 싶지 않다면 그대로 False로 두세요. Defaults to False.
        consecutive_char (str | None, optional): consecutive_char를 알고 있고 다시 스페이스로 되돌리고 싶다면 작성해 주세요.
            이때 기존에 이미 있었던 consecutive_char와 동일한 문자도 같이 변경될 수 있습니다.
            예를 들어 기존 이름이 'Hello World! - by myself.txt'가 있고 consecutive_char가 '-'면 'Hello-World!---by-myself.txt'가 되었을 것이고
            consecutive_char 값을 '-'으로 설정하면 'Hello World!   by myself.txt'가 됩니다. 즉, consecutive_char를 설정하면 원본과 달라질 수도 있습니다. Defaults to None.
    """
    upside_down_table: dict[int, int] = dict(map(reversed, TRANSLATE_TABLE_FULLWIDTH.items()))  # type: ignore
    processed = name.translate(upside_down_table)

    if remove_replacement_char is not None:
        processed = processed.replace(remove_replacement_char, '')

    if html_escape:
        processed = html.escape(processed)

    if consecutive_char is not None:
        processed = processed.replace(consecutive_char, ' ')

    return processed


def sanitize_path(
    path: str | Path,
    mode: TextMode = TextMode.fullwidth,
    *,
    # length_check: bool = False,
    html_unescape: bool = True,
    replacement_char: str | ReplacementCharacter = ReplacementCharacter.space,
    correct_following_dot: DotHandlingPolicy = DotHandlingPolicy.replace,
    consecutive_char: str | None = None,
) -> str | Path:
    r"""
    이 함수를 사용해 경로를 직접 변경하기보다는 translate_to_safe_name을 사용해 경로에 들어가는
    각각의 파일이나 디렉토리 이름들을 모두 안전한 이름으로 바꾸고 사용할 것을 권장합니다.
    예를 들어 파일의 이름으로 설정할 값이 "articles/1/0은 무슨 값일까?"라면 "articles" > "1" > "0은 무슨 값일까?"와 같은 디렉토리 구조로
    잘못 계산될 수 있습니다. translate_to_safe_name을 이용하면 이러한 문제가 발생하지 않습니다.
    pathlib.Path는 이름이 실제로 작성 가능한지 여부를 따지지 않습니다. 따라서 실제로 사용 가능한 URL인지는 확신할 수 없습니다.
    따라서 translate_to_safe_path_name를 통해 해당 디렉토리를 안전하게 만들고 싶을 때 사용할 수도 있습니다.

    Params:
        path: 이 함수를 통해 변환할 값입니다.
        length_check: Windows에는 경로를 포함한 파일의 이름이 255자가 넘어가면 해당 이름으로 파일을 만들 수 없습니다. 기본적으로는 꺼져 있습니다.
        correct_following_dot: 이 값을 DOT_NO_CORRECTION으로 하려 한다면 디렉토리의 이름들까지 모두 변경되지 않기 때문에
        특별한 주의가 필요합니다. 예를 들어 'hello./world.'이라는 경로가 있을 때 DOT_NO_CORRECTION을 사용하면 'hello.'만
        변경되지 않는 것이 아닌 'hello.'의 이름도 변경되지 않습니다.
        나머지 파라미터들과 correct_following_dot의 기본 설명은 translate_to_safe_name을 확인해 주세요.
    """
    is_path = not isinstance(path, str)

    # normalized_path_parts = os.path.normpath(path).split(os.path.sep)
    # 윈도우 사용자도 '/'을 구분자로 사용하는 경우가 더러 있기 때문에 위의 코드 대신 둘 모두를 구분자로 사용함.
    normalized_path_parts = [fully_splited
                             for backslash_splited in os.path.normpath(path).split('\\')
                             for fully_splited in backslash_splited.split('/')]

    translated = [path_part if path_part in {'.', '..'} else sanitize(
        path_part, mode=mode, html_unescape=html_unescape, correct_following_dot=correct_following_dot,
        replacement_char=replacement_char, consecutive_char=consecutive_char
    ) for path_part in normalized_path_parts]

    translated_path = os.path.sep.join(translated)

    # if length_check and len(os.path.abspath(translated_path)) >= 246:
    if len(os.path.abspath(translated_path)) >= 246:
        logging.warning('Your path is too long, so it might cannot be not saved or modified '
                        'in case of you are using default settings in Windows.')

    return Path(translated_path) if is_path else translated_path


def sanitize(
    name: str,
    mode: TextMode = TextMode.fullwidth,
    strict: bool = True,
    *,
    html_unescape: bool = True,
    replacement_char: str | ReplacementCharacter = ReplacementCharacter.space,
    correct_following_dot: DotHandlingPolicy = DotHandlingPolicy.replace,
    consecutive_char: str | None = None,
) -> str:
    r"""파일명 혹은 디렉토리명에 사용할 수 없는 글자를 사용할 수 있는 글자로 변경합니다.

    이 함수는 이름을 normalize하는 것에 주안점을 두고 있지 않습니다. 대신 윈도우에서 이름 충돌이 일어나지 않도록 만듭니다.

    주의: 이 함수는 파일 '경로'(path/to/file.txt)를 처리하도록 제작되지 않았습니다.
    만약 디렉토리를 처리하야 한다면 translate_to_safe_path_name를 사용해야 합니다.

    params:
        name: 파일 혹은 디렉토리의 이름입니다.
            만약 'helloworld.txt'가 있다면 'helloworld.txt' 전체를 그대로 입력하시면 됩니다.
            'is_vaild_file_name' 사용을 권장합니다.

        mode: 문자열 변환 모드를 설정합니다.

        html_unescape: HTML escape되었던 문자열을 unescape합니다. 예를 들어 '\&lt;\&amp;\&gt;'라는 문자열이 있다면 '<&>'로 다시 되돌립니다.

        correct_following_dot:
            윈도우에서는 파일 이름 맨 끝에 점이 오는 것을 금지합니다. 그렇게 맨 뒤 글자의 마침표는 제거하거나, 안전한 문자로 변경해야 합니다.

            이 파라미터로 조절 파일 이름의 조절 방법을 결정합니다.

            값으로 가능한 수:
                `DotHandlingPolicy.remove`: 이 경우에는 뒤에 따라오는 모든 마침표를 제거합니다.

                `DotHandlingPolicy.replace`: 이 함수는 맨 뒤 마침표 하나를 '．'으로 변경합니다. '．'는 전각 마침표로, 윈도우에서 제거하는 대상이 아닙니다.

                `DotHandlingPolicy.do_not_correct`:
                    이 함수는 거의 모든 경우에서 "안전한 이름 + 안전한 이름 = 안전한 이름" 공식이 성립합니다.

                    예를 들어 `translate_to_safe_name(title) + '.txt'`와 `translate_to_safe_name(title + '.txt')`는 같습니다.

                    하지만 마침표(.)의 경우는 그렇지 않습니다. 즉, 안전하지 않은 이름(.으로 끝나느 이름) + 안전한 이름 = 안전한 이름일 수 있습니다.

                    따라서 만약 이 함수로 처리한 문자열 뒤에 '.txt' 따위를 붙일 예정이라면 correct_following_dot이 필요가 없을 것입니다. 이럴 때에
                    DotHandlingPolicy.do_not_correct를 사용할 수 있습니다.

        replacement_char:
            만약 mode가 MODE_USE_REPLACEMENT_CHAR이면 사용할 수 없는 모든 글자가 replacement_char로 변환됩니다.
            mode가 fullwidth일 때에는 일부 fullwidth character로 표현할 수 없는 문자(제어 문자 등.)가 replacement_char로 변환됩니다.
            현재로서는 꼭 한 글자일 필요는 없고, 여러 글자도 사용 가능합니다.

        consecutive_char:
            만약 None(기본값)일 경우 아무런 영향도 주지 않지만, None이 아닐 경우 스페이스를 해당 문자로 변경합니다.
            replacement_char가 스페이스(기본값)일 때 영향을 받을 수 있으니 주의하세요.
    """
    processed = html.unescape(name) if html_unescape else name

    processed = processed.translate(TRANSLATE_TABLE_FULLWIDTH
                                    if mode == TextMode.fullwidth else TRANSLATE_TABLE_REPLACEMENT)

    # 윈도우에서는 앞뒤에 space가 있을 수 없기에 strip이 필요하다.
    if isinstance(replacement_char, str):
        processed = processed.replace('\x00', replacement_char)
    elif isinstance(replacement_char, ReplacementCharacter):
        processed = processed.replace('\x00', replacement_char.value)
    else:
        raise TypeError(f'Unexpected type of replacement_char: {type(replacement_char)}')

    processed = processed.strip() if strict else processed.rstrip()

    if correct_following_dot and processed.endswith('.'):
        if correct_following_dot == DotHandlingPolicy.remove:
            processed = processed.rstrip('.').rstrip()
        elif correct_following_dot == DotHandlingPolicy.replace:
            processed = processed.removesuffix('.') + '．'

    if is_name_reserved(processed, strict):
        # 만약 processed + '_'이라면 파일 확장자가 망가질 수 있다.
        # 예를 들어 "COM2.txt"라면 "COM2.txt_"가 되어 파일 확장자가 망가진다.
        # 하지만 앞쪽에 놓는다면 "_COM2.txt"가 되어 파일 확장자가 망가지지 않는다.
        processed = f'_{processed}'

    if consecutive_char is not None:
        processed = processed.replace(' ', consecutive_char)

    if not processed:  # sourcery skip
        return '_'

    return processed


def sanitize_return_value(
    f: Callable | None = None,
    /,
    *,
    allow_path: bool = False,
    **sanitize_kwargs,
):
    """함수의 출력값이 문자열일 경우 해당 출력값을 파일명 및 디렉토리명에 사용할 수 있도록 변경하는 데코레이터입니다.

    allow_path가 True라면 sanitize_path를 사용합니다.
    """
    if f is None:
        return functools.partial(sanitize_return_value, **sanitize_kwargs)

    def wrapper(*args, **kwargs):
        return_value = f(*args, **kwargs)

        if not isinstance(return_value, str):
            return return_value

        return sanitize_path(return_value) if allow_path else sanitize(return_value)

    return wrapper
