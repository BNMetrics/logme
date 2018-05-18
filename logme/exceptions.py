class LogmeError(Exception):
    """Used as a general error for the logme module"""


class MisMatchScope(Exception):
    """Used when scope and passed callable is mismatched"""


class InvalidOption(Exception):
    """Used when the option in config file is invalid"""


class InvalidConfig(Exception):
    """Used when invalid configuration is passed"""


class InvalidColorConfig(Exception):
    """Used when invalid color configuration is passed"""


class DuplicatedHandler(Exception):
    """Used when an identical handler is being added on to a logger"""
