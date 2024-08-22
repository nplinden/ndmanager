import os


def clear_line(n: int = 1):
    """Move the print cursor up n lines.

    Args:
        n (int, optional): Number of lines the cursor will be moved up. Defaults to 1.
    """
    for _ in range(n):
        print("\033[1A", end= "\x1b[2K")


def header(string):
    col, _ = os.get_terminal_size()
    toprint = f"  {string}  "
    return f"{toprint:{'-'}{'^'}{col}}"

def footer():
    col, _ = os.get_terminal_size()
    return f"{'':{'-'}{'^'}{col}}"

