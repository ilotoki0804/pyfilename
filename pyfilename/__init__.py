if __name__ == "__main__":
    from pyfilename import (
        TRANSLATE_TABLE_FULLWIDTH, TRANSLATE_TABLE_REPLACEMENT, NOT_ALLOWED_NAMES,
        DOT_REMOVE, DOT_REPLACE, DOT_NO_CORRECTION, FOLLOWING_DOT_REPLACEMENT,
        MODE_FULLWIDTH, MODE_USE_REPLACEMENT_CHAR, MODE_REMOVE,
        CHAR_SPACE, CHAR_DOUBLE_QUOTATION_MARK, CHAR_WHITE_QUESTION_MARK, CHAR_RED_QUESTION_MARK,
        EmptyStringError,
        is_vaild_file_name, safe_name_to_original_name, translate_to_safe_path_name, translate_to_safe_name,
    )
else:
    from .pyfilename import (
        TRANSLATE_TABLE_FULLWIDTH, TRANSLATE_TABLE_REPLACEMENT, NOT_ALLOWED_NAMES,
        DOT_REMOVE, DOT_REPLACE, DOT_NO_CORRECTION, FOLLOWING_DOT_REPLACEMENT,
        MODE_FULLWIDTH, MODE_USE_REPLACEMENT_CHAR, MODE_REMOVE,
        CHAR_SPACE, CHAR_DOUBLE_QUOTATION_MARK, CHAR_WHITE_QUESTION_MARK, CHAR_RED_QUESTION_MARK,
        EmptyStringError,
        is_vaild_file_name, safe_name_to_original_name, translate_to_safe_path_name, translate_to_safe_name,
    )

if __name__ == '__main__':
    print('Testing codes.')
