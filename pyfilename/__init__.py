if __name__ == "__main__":
    from main import (
        TRANSLATE_TABLE_FULLWIDTH, TRANSLATE_TABLE_REPLACEMENT, NOT_ALLOWED_NAMES,
        DotHandlingPolicy, TextMode, ReplacementCharacter,
        is_name_safe, get_original_name, sanitize_path, sanitize, sanitize_return_value
    )
else:
    from .main import (
        TRANSLATE_TABLE_FULLWIDTH, TRANSLATE_TABLE_REPLACEMENT, NOT_ALLOWED_NAMES,
        DotHandlingPolicy, TextMode, ReplacementCharacter,
        is_name_safe, get_original_name, sanitize_path, sanitize, sanitize_return_value
    )

__version__ = "0.4.0"
