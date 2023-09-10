# NTFS 예약어는 루트 디렉토리 (C:나 D: 등)에서 문제를 일으킬 수 있습니다.
# 하지만 사용성이 매우 적기에 포함하지는 않았습니다.
# 관련 링크: https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-fscc/b04c3bd0-79dc-4e58-b8ed-74f19fc2ea0a

# 리눅스의 경우에는 NULL과 slash를 제외하면 모든 것을 파일 이름으로 사용할 수 있습니다.
# 하지만 몇몇 기기들은 자체적으로 그 외의 이름에도 제한을 걸기도 합니다(삼성 갤럭시 등).

import re
import html
from typing import Literal
import logging
from pathlib import Path
from typing import overload, Final

__all__ = (
    "TRANSLATE_TABLE_FULLWIDTH", "TRANSLATE_TABLE_REPLACEMENT", "NOT_ALLOWED_NAMES",
    "DOT_REMOVE", "DOT_REPLACE", "DOT_NO_CORRECTION", "FOLLOWING_DOT_REPLACEMENT",
    "MODE_FULLWIDTH", "MODE_USE_REPLACEMENT_CHAR", "MODE_REMOVE",
    "CHAR_SPACE", "CHAR_DOUBLE_QUOTATION_MARK", "CHAR_WHITE_QUESTION_MARK", "CHAR_RED_QUESTION_MARK",
    "EmptyStringError",
    "is_vaild_file_name", "safe_name_to_original_name", "translate_to_safe_path_name", "translate_to_safe_name",
)

TRANSLATE_TABLE_FULLWIDTH = str.maketrans('\\/:*?"<>|', '⧵／：＊？＂＜＞∣') | {i: 0 for i in range(32)}
TRANSLATE_TABLE_REPLACEMENT = str.maketrans('\\/:*?"<>|', '\x00' * 9) | {i: 0 for i in range(32)}
NOT_ALLOWED_NAMES = {
    # 출처: https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file

    "CON", "PRN", "AUX", "NUL",

    # "COM0",  # : 문서에는 사용할 수 없다고 나와있는데 실제로는 작동하기에 주석 처리함.
    "COM1", "COM¹", "COM2", "COM²", "COM3", "COM³", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",

    # "LPT0",  # : 문서에는 사용할 수 없다고 나와있는데 실제로는 작동하기에 주석 처리함.
    "LPT1", "LPT¹", "LPT2", "LPT²", "LPT3", "LPT³", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
}

DOT_REMOVE = 'dot_remove'
DOT_REPLACE = 'dot_replace'
DOT_NO_CORRECTION = 'dot_no_correction'
FOLLOWING_DOT_REPLACEMENT = {DOT_REPLACE: '．', DOT_NO_CORRECTION: '.'}
CorrectFollowingDot = Literal['dot_remove', 'dot_replace', 'dot_no_correction']

MODE_FULLWIDTH = 'mode_fullwidth'
MODE_USE_REPLACEMENT_CHAR = 'mode_use_replacement_char'
MODE_REMOVE = 'mode_remove'
TextModes = Literal['mode_fullwidth', 'mode_use_replacement_char', 'mode_remove']

CHAR_SPACE: Final = ' '
CHAR_DOUBLE_QUOTATION_MARK: Final = '⁇'
CHAR_WHITE_QUESTION_MARK: Final = '❔'
CHAR_RED_QUESTION_MARK: Final = '❓'


class EmptyStringError(Exception):
    pass


def is_vaild_file_name(
    name: str,
) -> bool:
    return (
        all(char not in TRANSLATE_TABLE_REPLACEMENT for char in name)
        and name.upper()[:3] not in NOT_ALLOWED_NAMES
        and name.upper()[:4] not in NOT_ALLOWED_NAMES
        and name.endswith('.')
    )
    # ...or return translate_to_safe_name(name) == name  # 훨씬 느림


def safe_name_to_original_name(
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
            예를 들어 기존 이름이 'Hello World! - by myself.txt'가 있고 consecutive_char가 '-'면 'Hello-World!---by-myself.txt'
            가 되었을 것이고 consecutive_char 값을 '-'으로 설정하면 'Hello World!   by myself.txt'가 됩니다.
            원본과는 달라졌을 수 있다는 의미입니다. Defaults to None.
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


def translate_to_safe_path_name(
    path: str | Path,
    mode: TextModes = MODE_FULLWIDTH,
    *,
    length_check: bool = True,
    html_unescape: bool = True,
    replacement_char: str = CHAR_SPACE,
    correct_following_dot: CorrectFollowingDot = DOT_REPLACE,
    consecutive_char: str | None = None,
) -> str | Path:
    r"""
    경로를 직접 변경하기보다는 경로에 들어가는 각각의 파일이나 디렉토리 이름들을 모두 안전한 이름으로 바꾸고
    사용할 것을 권장합니다.
    예를 들어 사용자 입력이 "1/0은 무슨 값일까?"라면  "1" 디렉토리 아래에 "0은 무슨 값일까?"라는 파일이 있는 식으로
    잘못 계산될 수 있습니다. translate_to_safe_name을 이용하면 이러한 문제가 발생하지 않습니다.
    pathlib.Path는 이름이 실제로 작성 가능한지 여부를 따지지 않습니다. 따라서 실제로 사용 가능한 URL인지는 확신할 수 없습니다.
    따라서 translate_to_safe_path_name를 통해 해당 디렉토리를 안전하게 만들고 싶을 수 있습니다.

    Params:
        path: 사용할 경로입니다.
        length_check: Windows에는 경로를 포함한 파일의 이름이 255자가 넘어가면 해당 이름으로 파일을 만들 수 없습니다.
            단순히 PurePath의 용도로 사용할 것이거나, 현재 경로가 바뀔 수 있거나 속도 향상을 원한다면 False로 설정해 끌 수 있습니다.
        correct_following_dot: 이 값을 DOT_NO_CORRECTION으로 하려 한다면 디렉토리의 이름들까지 모두 변경되지 않기 때문에
        특별한 주의가 필요합니다. 예를 들어 'hello./world.'이라는 경로가 있을 때 DOT_NO_CORRECTION을 사용하면 'hello.'만
        변경되지 않는 것이 아닌 'hello.'의 이름도 변경되지 않습니다.
        나머지 파라미터들과 correct_following_dot의 기본 설명은 translate_to_safe_name을 확인해 주세요.
    """
    is_path = not isinstance(path, str)

    translated = [translate_to_safe_name(
        path_part, mode=mode, html_unescape=html_unescape, correct_following_dot=correct_following_dot,
        replacement_char=replacement_char, consecutive_char=consecutive_char
    ) for path_part in Path(path).parts]

    translated_path = Path('/'.join(translated))

    if length_check and len(str(translated_path.absolute())) >= 246:
        logging.warning('Your path is too long, so it might cannot be not saved or modified '
                        'in case of you are using default settings in Windows.')

    return translated_path if is_path else str(translated_path)


def translate_to_safe_name(
    name: str,
    mode: TextModes = MODE_FULLWIDTH,
    *,
    html_unescape: bool = True,
    replacement_char: str = CHAR_SPACE,
    correct_following_dot: CorrectFollowingDot = DOT_REPLACE,
    consecutive_char: str | None = None,
) -> str:
    """파일명 혹은 디렉토리명에 사용할 수 없는 글자를 사용할 수 있는 글자로 변경합니다.
    이 함수는 이름을 normalize하는 것에 주안점을 두고 있지 않습니다. 대신 윈도우에서 이름 충돌이 일어나지 않도록 만듭니다.
    주의: 이 함수는 디렉토리를 처리하도록 제작되지 않았습니다. 만약 디렉토리를 처리하야 한다면 

    이 함수에서 처리되는
    이 함수는 거의 모든 경우에서 함수의 부분에 대해서도 성립합니다. 하지만 마침표(.)의 경우는 그렇지 않습니다.

    params:
        name: 파일 혹은 디렉토리의 이름입니다.
            만약 'helloworld.txt'가 있다면 'helloworld.txt' 전체를 그대로 입력하시면 됩니다.
            'is_vaild_file_name' 사용을 권장합니다.

        mode: 파일 이름에서 사용될 수 없는 이름을

        html_unescape:

        correct_following_dot:
            윈도우에서는 파일 이름 맨 끝에 

        replacement_char:
            만약 mode가 MODE_USE_REPLACEMENT_CHAR이면 사용할 수 없는 모든 글자가 replacement_char로 변환됩니다.
            mode가 fullwidth일 때에는 일부 fullwidth character로 표현할 수 없는 문자(제어 문자 등.)가 replacement_char로 변환됩니다.
            현재로서는 꼭 한 글자일 필요는 없고, 여러 글자도 사용 가능합니다.

        consecutive_char:
            만약 None(기본값)일 경우 아무런 영향도 주지 않지만, None이 아닐 경우 스페이스를 해당 문자로 변경합니다.
            replacement_char가 스페이스(기본값)일 때 영향을 받을 수 있으니 주의하세요.
    """
    processed = html.unescape(name) if html_unescape else name

    processed = processed.translate(TRANSLATE_TABLE_FULLWIDTH if mode == MODE_FULLWIDTH else TRANSLATE_TABLE_REPLACEMENT)

    # 윈도우에서는 앞뒤에 space가 있을 수 없기에 strip이 필요하다.
    processed = processed.replace('\x00', replacement_char).strip()

    if correct_following_dot and processed.endswith('.'):
        if correct_following_dot == DOT_REMOVE:
            processed = processed.rstrip('.')
        else:
            processed = processed.removesuffix('.') + FOLLOWING_DOT_REPLACEMENT[correct_following_dot]

    if not processed:
        raise EmptyStringError(f'After processing, the string is empty. (input name: {name})')

    if processed.upper()[:3] in NOT_ALLOWED_NAMES or processed.upper()[:4] in NOT_ALLOWED_NAMES:
        processed += '_'

    if consecutive_char is not None:
        processed = processed.replace(' ', consecutive_char)

    return processed
