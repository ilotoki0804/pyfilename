"""Windows-proof file name generator.

██████╗░██╗░░░██╗███████╗██╗██╗░░░░░███████╗███╗░░██╗░█████╗░███╗░░░███╗███████╗
██╔══██╗╚██╗░██╔╝██╔════╝██║██║░░░░░██╔════╝████╗░██║██╔══██╗████╗░████║██╔════╝
██████╔╝░╚████╔╝░█████╗░░██║██║░░░░░█████╗░░██╔██╗██║███████║██╔████╔██║█████╗░░
██╔═══╝░░░╚██╔╝░░██╔══╝░░██║██║░░░░░██╔══╝░░██║╚████║██╔══██║██║╚██╔╝██║██╔══╝░░
██║░░░░░░░░██║░░░██║░░░░░██║███████╗███████╗██║░╚███║██║░░██║██║░╚═╝░██║███████╗
╚═╝░░░░░░░░╚═╝░░░╚═╝░░░░░╚═╝╚══════╝╚══════╝╚═╝░░╚══╝╚═╝░░╚═╝╚═╝░░░░░╚═╝╚══════╝
"""

__version__ = "0.4.0"
__github_project_name__ = "pyfilename"
__github_user_name__ = "ilotoki0804"

from .main import (
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
