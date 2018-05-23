import pytest

import logging

from logme.color_provider import Color, ColorFormatter
from logme.config import get_color_config, get_config_content
from logme.exceptions import InvalidColorConfig


COLOR_CONFIG = get_color_config(__file__)
NULL_COLOR_CONFIG = get_config_content(__file__, 'colors_null')


@pytest.mark.parametrize('parse_args, result, text_style',
                         [
                             pytest.param({'color': 'red'}, "\033[0;31m", {'color': '31'},
                                          id='With color only, no style passed in'),
                             pytest.param({'color': 'Blue', 'style': 'BOLD'}, "\033[0;1;34m",
                                          {'color': '34', 'style': '1'},
                                          id='With both color and style passed in, and cap on values'),
                             pytest.param({'style': 'bold'}, "\033[0;1m", {'style': '1'},
                                          id='With only style passed in'),
                             pytest.param({'color': 'purple', 'style': 'underline', 'bg': 'cyan'}, "\033[0;46;4;35m",
                                          {'color': '35', 'style': '4', 'bg': '46'},
                                          id='With all args passed in'),
                         ])
def test_color_code(parse_args, result, text_style):
    color = Color(**parse_args)
    print(color.code + "hello" + Color('reset').code)

    assert color.code == result
    assert color.text_style == text_style


def test_color_code_reset():
    reset = Color('reset')
    reset_with_kwargs = Color(color='reset', style='reset')
    reset_with_kwargs2 = Color(color='reset', style='reset', bg='blue')
    reset_bg = Color(color='reset', style='reset', bg='reset')

    assert str(reset) == str(reset_with_kwargs) \
           == str(reset_with_kwargs2) == str(reset_bg)


@pytest.mark.parametrize('parse_args',
                         [
                             pytest.param({'color': 'red', 'style': 'blah'}, id='invalid style passed'),
                             pytest.param('bold', id='Passing in style as color'),
                         ])
def test_color_code_raise(parse_args):
    with pytest.raises(InvalidColorConfig):
        if isinstance(parse_args, dict):
            Color(**parse_args)
        else:
            Color(parse_args)


def test_color_repr(capsys):
    color = Color(color='purple')
    print(color)

    out, err = capsys.readouterr()
    assert out.strip() == '<Color code=\\033[0;35m>'


@pytest.mark.parametrize('color_conf, color_prefix, color_suffix',
                         [
                             pytest.param(None, '', '', id='when color_config is None'),
                             pytest.param(COLOR_CONFIG, '\033[0;41;1;37m', '\033[0;0m',
                                          id='when color_config is passed'),
                         ])
def test_color_formatter(color_conf, color_prefix, color_suffix):
    fmt = ColorFormatter('{name} - {levelname} - {message}', style='{',
                         color_config=color_conf)

    record = logging.LogRecord('logger_name', 50, 'pathname', 'lineno', 'my logging message',
                               [], [])

    msg = fmt.format(record)
    assert msg == color_prefix + 'logger_name - CRITICAL - my logging message' + color_suffix


@pytest.mark.parametrize('color_config, lines',
                         [
                             pytest.param(COLOR_CONFIG,
                                          ['\033[0;37mtest_color_logger - DEBUG - hello\033[0;0m\n',
                                           '\033[0;35mtest_color_logger - ERROR - error message\033[0;0m\n'],
                                          id='With normal color config'),
                             pytest.param(NULL_COLOR_CONFIG,
                                          ['test_color_logger - DEBUG - hello\n',
                                           'test_color_logger - ERROR - error message\n'],
                                          id='With all color values configured to None')
                         ])
def test_color_formatter_integration(tmpdir, color_config, lines):
    logfile = tmpdir.join('color_test.log')

    # Get logger
    logger = logging.getLogger('test_color_logger')
    logger.setLevel('DEBUG')

    # Get Handlers
    stream = logging.StreamHandler()
    file = logging.FileHandler(tmpdir.join('color_test.log'))

    fmt = ColorFormatter('{name} - {levelname} - {message}', style='{',
                         color_config=color_config)

    stream.setFormatter(fmt)
    file.setFormatter(fmt)

    logger.addHandler(stream)
    logger.addHandler(file)

    # output logging message
    logger.debug('hello')
    logger.error('error message')

    with open(logfile) as file:
        for line in file:
            assert line in lines

    # Cleaning up after test
    del logging.Logger.manager.loggerDict['test_color_logger']
