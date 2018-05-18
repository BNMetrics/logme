import pytest

from logme.color_provider import ColorProvider
from logme.exceptions import InvalidColorConfig


@pytest.mark.parametrize('parse_args, result',
                         [
                             pytest.param({'color': 'red'}, "\033[31m",
                                          id='With color only, no style passed in'),
                             pytest.param({'color': 'blue', 'style': 'bold'}, "\033[1;34m",
                                          id='With both color and style passed in'),
                             pytest.param({'style': 'bold'}, "\033[m",
                                          id='With only style passed in, no change in output formatting'),
                         ])
def test_color_provider(parse_args, result):
    provider = ColorProvider(**parse_args)

    assert provider.code == result


def test_color_provider_raise():
    with pytest.raises(InvalidColorConfig):
        ColorProvider(color='red', style='blah')


# class TestcolorProvider:
#
#     def test_color(self):
#         red = ColorProvider(color='red')
#
#         print(f"{red.code}hi")
#
#     def test_blah(self):
#         from termcolor import colored
#
#         print(colored('hello', 'pink'))
#         print("\033[0mHello \033[0;0mworld")