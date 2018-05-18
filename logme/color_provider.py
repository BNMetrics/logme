import logging

from .exceptions import InvalidColorConfig


class ColorProvider:
    """
    * Having style alone will not have an effect!*


    """
    escape_code = "\033["

    color_map = {
        'reset': 0,
        'black': 30,
        'red': 31,
        'green': 32,
        'yellow': 33,
        'blue': 34,
        'purple': 35,
        'cyan': 36,
        'white': 37,
    }

    style_map = {
        'bold': 1, 'underline': 4,
    }

    def __init__(self, color: str=None, style: str=None):
        try:
            if color:
                self.color = self.color_map[color]
            if style:
                self.style = self.style_map[style]
        except KeyError as e:
            raise InvalidColorConfig(f"'{e}' is not a valid style or color")

    @property
    def code(self):
        if hasattr(self, 'color'):
            if hasattr(self, 'style'):
                style_fill = f"{self.style};{self.color}"
            else:
                style_fill = f"{self.color}"
        else:
            style_fill = f""

        color_code = f"{self.escape_code}{style_fill}m"

        return color_code
