import os
import sys
import termui

import termui._termui_impl


def test_echo(runner):
    with runner.isolation() as out:
        termui.echo(u'\N{SNOWMAN}')
        termui.echo(b'\x44\x44')
        termui.echo(42, nl=False)
        termui.echo(b'a', nl=False)
        termui.echo('\x1b[31mx\x1b[39m', nl=False)
        bytes = out.getvalue()
        assert bytes == b'\xe2\x98\x83\nDD\n42ax'

    # If we are in Python 2, we expect that writing bytes into a string io
    # does not do anything crazy.  In Python 3
    if sys.version_info[0] == 2:
        import StringIO
        sys.stdout = x = StringIO.StringIO()
        try:
            termui.echo('\xf6')
        finally:
            sys.stdout = sys.__stdout__
        assert x.getvalue() == '\xf6\n'

    # And in any case, if wrapped, we expect bytes to survive.
    def cli():
        termui.echo(b'\xf6')
    result = runner.invoke(cli, [])
    assert result.output_bytes == b'\xf6\n'

    # Ensure we do not strip for bytes.
    with runner.isolation() as out:
        termui.echo(bytearray(b'\x1b[31mx\x1b[39m'), nl=False)
        assert out.getvalue() == b'\x1b[31mx\x1b[39m'


def test_styling():
    examples = [
        ('x', dict(fg='black'), '\x1b[30mx\x1b[0m'),
        ('x', dict(fg='red'), '\x1b[31mx\x1b[0m'),
        ('x', dict(fg='green'), '\x1b[32mx\x1b[0m'),
        ('x', dict(fg='yellow'), '\x1b[33mx\x1b[0m'),
        ('x', dict(fg='blue'), '\x1b[34mx\x1b[0m'),
        ('x', dict(fg='magenta'), '\x1b[35mx\x1b[0m'),
        ('x', dict(fg='cyan'), '\x1b[36mx\x1b[0m'),
        ('x', dict(fg='white'), '\x1b[37mx\x1b[0m'),
        ('x', dict(bg='black'), '\x1b[40mx\x1b[0m'),
        ('x', dict(bg='red'), '\x1b[41mx\x1b[0m'),
        ('x', dict(bg='green'), '\x1b[42mx\x1b[0m'),
        ('x', dict(bg='yellow'), '\x1b[43mx\x1b[0m'),
        ('x', dict(bg='blue'), '\x1b[44mx\x1b[0m'),
        ('x', dict(bg='magenta'), '\x1b[45mx\x1b[0m'),
        ('x', dict(bg='cyan'), '\x1b[46mx\x1b[0m'),
        ('x', dict(bg='white'), '\x1b[47mx\x1b[0m'),
        ('foo bar', dict(blink=True), '\x1b[5mfoo bar\x1b[0m'),
        ('foo bar', dict(underline=True), '\x1b[4mfoo bar\x1b[0m'),
        ('foo bar', dict(bold=True), '\x1b[1mfoo bar\x1b[0m'),
        ('foo bar', dict(dim=True), '\x1b[2mfoo bar\x1b[0m'),
    ]
    for text, styles, ref in examples:
        assert termui.style(text, **styles) == ref
        assert termui.unstyle(ref) == text


def test_filename_formatting():
    assert termui.format_filename(b'foo.txt') == 'foo.txt'
    assert termui.format_filename(b'/x/foo.txt') == '/x/foo.txt'
    assert termui.format_filename(u'/x/foo.txt') == '/x/foo.txt'
    assert termui.format_filename(u'/x/foo.txt', shorten=True) == 'foo.txt'
    assert termui.format_filename(b'/x/foo\xff.txt', shorten=True) \
        == u'foo\ufffd.txt'


def test_prompts(runner):
    def test():
        if termui.confirm('Foo'):
            termui.echo('yes!')
        else:
            termui.echo('no :(')

    result = runner.invoke(test, input='y\n')
    assert not result.exception
    assert result.output == 'Foo [y/N]: y\nyes!\n'

    result = runner.invoke(test, input='\n')
    assert not result.exception
    assert result.output == 'Foo [y/N]: \nno :(\n'

    result = runner.invoke(test, input='n\n')
    assert not result.exception
    assert result.output == 'Foo [y/N]: n\nno :(\n'

    def test_no():
        if termui.confirm('Foo', default=True):
            termui.echo('yes!')
        else:
            termui.echo('no :(')

    result = runner.invoke(test_no, input='y\n')
    assert not result.exception
    assert result.output == 'Foo [Y/n]: y\nyes!\n'

    result = runner.invoke(test_no, input='\n')
    assert not result.exception
    assert result.output == 'Foo [Y/n]: \nyes!\n'

    result = runner.invoke(test_no, input='n\n')
    assert not result.exception
    assert result.output == 'Foo [Y/n]: n\nno :(\n'


def test_echo_via_pager(monkeypatch, capfd):
    monkeypatch.setitem(os.environ, 'PAGER', 'cat')
    monkeypatch.setattr(termui._termui_impl, 'isatty', lambda x: True)
    termui.echo_via_pager('haha')
    out, err = capfd.readouterr()
    assert out == 'haha\n'


def test_echo_color_flag(monkeypatch, capfd):
    isatty = True
    monkeypatch.setattr(termui._compat, 'isatty', lambda x: isatty)

    text = 'foo'
    styled_text = termui.style(text, fg='red')
    assert styled_text == '\x1b[31mfoo\x1b[0m'

    termui.echo(styled_text, color=False)
    out, err = capfd.readouterr()
    assert out == text + '\n'

    termui.echo(styled_text, color=True)
    out, err = capfd.readouterr()
    assert out == styled_text + '\n'

    isatty = True
    termui.echo(styled_text)
    out, err = capfd.readouterr()
    assert out == styled_text + '\n'

    isatty = False
    termui.echo(styled_text)
    out, err = capfd.readouterr()
    assert out == text + '\n'


def test_echo_writing_to_standard_error(capfd, monkeypatch):
    def emulate_input(text):
        """Emulate keyboard input."""
        if sys.version_info[0] == 2:
            from StringIO import StringIO
        else:
            from io import StringIO
        monkeypatch.setattr(sys, 'stdin', StringIO(text))

    termui.echo('Echo to standard output')
    out, err = capfd.readouterr()
    assert out == 'Echo to standard output\n'
    assert err == ''

    termui.echo('Echo to standard error', err=True)
    out, err = capfd.readouterr()
    assert out == ''
    assert err == 'Echo to standard error\n'

    emulate_input('asdlkj\n')
    termui.prompt('Prompt to stdin')
    out, err = capfd.readouterr()
    assert out == 'Prompt to stdin: '
    assert err == ''

    emulate_input('asdlkj\n')
    termui.prompt('Prompt to stderr', err=True)
    out, err = capfd.readouterr()
    assert out == ''
    assert err == 'Prompt to stderr: '

    emulate_input('y\n')
    termui.confirm('Prompt to stdin')
    out, err = capfd.readouterr()
    assert out == 'Prompt to stdin [y/N]: '
    assert err == ''

    emulate_input('y\n')
    termui.confirm('Prompt to stderr', err=True)
    out, err = capfd.readouterr()
    assert out == ''
    assert err == 'Prompt to stderr [y/N]: '

    monkeypatch.setattr(termui._termui, 'isatty', lambda x: True)
    monkeypatch.setattr(termui._termui, 'getchar', lambda: ' ')

    termui.pause('Pause to stdout')
    out, err = capfd.readouterr()
    assert out == 'Pause to stdout\n'
    assert err == ''

    termui.pause('Pause to stderr', err=True)
    out, err = capfd.readouterr()
    assert out == ''
    assert err == 'Pause to stderr\n'


def test_open_file(runner):
    with runner.isolated_filesystem():
        with open('hello.txt', 'w') as f:
            f.write('Cool stuff')

        def cli(filename):
            with termui.open_file(filename) as f:
                termui.echo(f.read())
            termui.echo('meep')

        result = runner.invoke(cli, ['hello.txt'])
        assert result.exception is None
        assert result.output == 'Cool stuff\nmeep\n'

        result = runner.invoke(cli, ['-'], input='foobar')
        assert result.exception is None
        assert result.output == 'foobar\nmeep\n'
