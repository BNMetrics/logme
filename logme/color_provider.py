import logging

from .exceptions import InvalidColorConfig

# Import colorama to allow ANSI code to work on windows systems
try:
    import colorama
    colorama.init()
except ModuleNotFoundError:
    pass


class Color:
    """


    Usage:
    - Get red color/bold code
        >>> color_code = Color(color='red', STYLE='bold').code
    - Reset color
        >>> reset_code = Color('reset')

    """
    escape_code = "\033["

    color_map = {
        'reset': '0',
        'black': '30',
        'red': '31',
        'green': '32',
        'yellow': '33',
        'blue': '34',
        'purple': '35',
        'cyan': '36',
        'white': '37',
    }

    bg_map = {
        'black': '40',
        'red': '41',
        'green': '42',
        'yellow': '43',
        'blue': '44',
        'purple': '45',
        'cyan': '46',
        'white': '47',
    }

    style_map = {
        'bold': '1', 'underline': '4',
    }

    def __init__(self, color: str=None, style: str=None, bg: str=None):
        parse_args = locals()
        try:
            self.text_style = {}
            for k, v in parse_args.items():
                if isinstance(v, str):
                    mapping = getattr(self, f"{k}_map")
                    self.text_style[k] = mapping[v.lower()]

        except KeyError as e:
            if e.args[0] == 'reset':
                self.text_style = {}
            else:
                if not self.color_map.get(color):
                    message = f"{e} is not a valid color"
                else:
                    message = f"{e} is not a valid style or background color"
                raise InvalidColorConfig(message)

    def __repr__(self):
        return "<Color " + "code=\\" + f"{self.code.replace(self.escape_code, '033[')}>"

    @property
    def code(self):
        if self.text_style:
            format_fill = ';'.join(self.text_style.values())
        else:
            format_fill = '0'

        color_code = f"{self.escape_code}0;{format_fill}m"

        return color_code


class ColorFormatter(logging.Formatter):

    def __init__(self, fmt: str=None, datefmt: str=None, style: str='%', color_config: dict=None):
        super().__init__(fmt, datefmt, style)
        self.color_config = color_config

    def format(self, record):
        msg = super().format(record)
        record_level = record.levelname

        if self.color_config:
            color_style = self.color_config.get(record_level)

            if color_style:
                if isinstance(color_style, dict):
                    color = Color(**color_style).code
                if isinstance(color_style, str):
                    color = Color(color_style).code

                # reset code after logging message
                color_reset = Color('reset').code

                msg = f"{color}{msg}{color_reset}"

        return msg
