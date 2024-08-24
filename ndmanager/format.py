"""Some functions to format printed output"""

import os


def clear_line(n: int = 1):
    """Move the print cursor up n lines.

    Args:
        n (int, optional): Number of lines the cursor will be moved up. Defaults to 1.
    """
    for _ in range(n):
        print("\033[1A", end="\x1b[2K")


def header(string: str, defcol: int = 150):
    """Format a cool header with a title

    Args:
        string (str): The title
        defcol (int, optional): Override column width default.

    Returns:
        str: The formatted header
    """
    col, _ = get_terminal_size(defcol=defcol)
    toprint = f"  {string}  "
    return f"{toprint:{'-'}{'^'}{col}}"


def footer(defcol: int = 150):
    """Format a footer fitting the terminal size

    Args:
        defcol (int, optional): Override column width default.

    Returns:
        str: The formatted footer
    """
    col, _ = get_terminal_size(defcol=defcol)
    return f"{'':{'-'}{'^'}{col}}"


def get_terminal_size(defcol: int = 150, defrow: int = 80) -> os.terminal_size:
    """Get the size of the current terminal window.
    If such an information is not available (e.g. when ndmanager is run from
    a Docker command or in pytest), it returns a default value that can be controlled
    through the `defcol` and `defrow` parameters.

    Args:
        defcol (int, optional): Default number of columns. Defaults to 150.
        defrow (int, optional): Default number of rows. Defaults to 80.

    Returns:
        os.terminal_size: The size of the terminal
    """
    try:
        return os.get_terminal_size()
    except OSError:
        return os.terminal_size((defcol, defrow))
