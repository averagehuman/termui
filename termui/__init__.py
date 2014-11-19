# -*- coding: utf-8 -*-
"""
    termui
    ~~~~~

    Terminal utilities extracted from Armin Ronacher's Click.

    :copyright: (c) 2014 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

# Utilities
from .utils import echo, get_binary_stream, get_text_stream, open_file, \
     format_filename, get_app_dir

# Terminal functions
from ._termui import prompt, confirm, get_terminal_size, echo_via_pager, \
     progressbar, clear, style, unstyle, secho, edit, launch, getchar, \
     pause

# Exceptions
from .exceptions import TermUIException, UsageError, BadParameter, \
    FileError, Abort


__all__ = [
    # Utilities
    'echo', 'get_binary_stream', 'get_text_stream', 'open_file',
    'format_filename', 'get_app_dir',

    # Terminal functions
    'prompt', 'confirm', 'get_terminal_size', 'echo_via_pager',
    'progressbar', 'clear', 'style', 'unstyle', 'secho', 'edit', 'launch',
    'getchar', 'pause',

    # Exceptions
    'TermUIException', 'UsageError', 'BadParameter', 'FileError', 'Abort',

]


__version__ = '0.0.1-dev'
