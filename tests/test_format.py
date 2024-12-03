from ndmanager.format import clear_line, footer, get_terminal_size, header


def test_get_terminal_size():
    cols, rows = get_terminal_size(defcol=80, defrow=50)
    assert cols == 80
    assert rows == 50


def test_clear_line(capsys):
    print("test1\ntest2\ntest3\ntest4")
    clear_line(2)
    out = capsys.readouterr().out.encode("unicode_escape")

    assert out == b"test1\\ntest2\\ntest3\\ntest4\\n\\x1b[1A\\x1b[2K\\x1b[1A\\x1b[2K"


def test_header(capsys):
    print(header("Joliot-Curie", defcol=50))
    out = capsys.readouterr().out
    assert out == "-----------------  Joliot-Curie  -----------------\n"


def test_footer(capsys):
    print(footer(defcol=50))
    out = capsys.readouterr().out
    assert out == "--------------------------------------------------\n"
