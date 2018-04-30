import pytest

import logging
import mock
from pathlib import Path

import logme.providers
from logme.providers import LogmeLogger
from logme.config import get_config_content
from logme.exceptions import InvalidConfig, DuplicatedHandler, InvalidOption, LogmeError


class TestLogmeLogger:

    @classmethod
    def setup(cls):
        cls.config = get_config_content(__file__)
        cls.logger = LogmeLogger('test_logger', cls.config)

    # ---------------------------------------------------------------------------
    # Test overall functionality
    # ---------------------------------------------------------------------------

    def test_logger(self):
        assert self.logger.level == 10

    def test_logging(self, caplog):
        self.logger.info('my logging message')
        captured = caplog.record_tuples[0]

        assert captured[0] == 'test_logger'
        assert captured[1] == 20
        assert captured[2] == 'my logging message'

    def test_non_existent_attr(self):
        with pytest.raises(AttributeError) as e_info:
            self.logger.foo()

        assert e_info.value.args[0] == "LogmeLogger object has no attribute 'foo'."

    def test_handlers(self):

        handlers = self.logger.handlers

        assert len(handlers) == 1
        assert isinstance(handlers[0], logging.StreamHandler)

    def test_set_handlers_twice(self):
        """Should not set duplicated handlers"""
        self.logger._set_handlers_from_conf()

        assert len(self.logger.handlers) == 1
        assert isinstance(self.logger.handlers[0], logging.StreamHandler)

    # ---------------------------------------------------------------------------
    # Test individual methods
    # ---------------------------------------------------------------------------

    def test_get_handler_args(self, monkeypatch):
        # Patch ensure_dir, so the arbitrary directory is not created
        monkeypatch.setattr(logme.providers, 'ensure_dir', lambda x: True)

        args = self.logger._get_handler_args('FileHandler')
        expected = {'filename': 'mylogpath/foo.log'}

        assert args == expected

    def test_get_handler_args_raise(self):
        config = get_config_content(__file__, 'null_config')
        logger = LogmeLogger('my_arg_test', config)

        with pytest.raises(ValueError):
            logger._get_handler_args('FileHandler')

    def test_get_handler_filehandler(self, file_config_content):
        logger = LogmeLogger('file_logger', file_config_content)

        logger.info('my log message for file handler')

        log_path = Path(file_config_content['FileHandler']['filename'])
        assert log_path.exists()

        with open(log_path) as file:
            assert file.readline() == 'file_logger::my log message for file handler\n'

    def test_set_handlers_handler_level_config(self, tmpdir):
        config = get_config_content(__file__, 'my_test_logger')

        logger = LogmeLogger('handler_level_conf', config)

        handler = logger.handlers[0]

        assert handler.level == 20  # INFO
        assert handler.formatter._fmt == '{asctime}::{message}'

    def test_handler_exist(self):
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('{asctime} - {name} - {levelname} - {module}::{funcName}::{message}')
        stream_handler.setFormatter(formatter)

        assert self.logger._handler_exist(stream_handler)

    def test_add_handler_filehandler(self, tmpdir):
        assert len(self.logger.handlers) == 1
        assert self.logger.handlers[0].__class__ == logging.StreamHandler

        self.logger.add_handler('FileHandler', formatter='{name}->{message}',
                                level='debug', filename=str(tmpdir.join('dummy.log')))

        assert len(self.logger.handlers) == 2
        assert set(map(lambda x: x.__class__, self.logger.handlers)) == {logging.StreamHandler, logging.FileHandler}

    def test_add_handler_sockethandler(self):
        self.logger.add_handler('SocketHandler', formatter='{name}->{message}',
                                level='debug', host='127.0.0.5', port=55)

        handler_types = [i.__class__.__name__ for i in self.logger.handlers]

        assert 'SocketHandler' in handler_types

    def test_add_handlers_raise(self, tmpdir):
        self.logger.add_handler('FileHandler', formatter='{name}->{message}',
                                level='debug', filename=str(tmpdir.join('dummy.log')))

        with pytest.raises(DuplicatedHandler):
            self.logger.add_handler('FileHandler', formatter='{name}->{message}',
                                    level='debug', filename=str(tmpdir.join('dummy.log')))

    def test_add_handler_allow_dup(self):
        logger = LogmeLogger('allow_duplicate', self.config)

        assert len(logger.handlers) == 1
        assert logger.handlers[0].__class__ == logging.StreamHandler

        logger.add_handler('StreamHandler', formatter='{asctime} - {name} - {levelname} - {module}::{funcName}::{message}',
                           level='debug', allow_duplicate=True)

        assert len(logger.handlers) == 2
        assert logger._get_handler_attr(logger.handlers[0]) == logger._get_handler_attr(logger.handlers[1])

    def test_get_handler_attr(self, socket_handler):
        attrs = self.logger._get_handler_attr(socket_handler)

        expected = {
            'formatter': '{asctime} - {name}::{message}',
            'level': 10,
            'host': '127.0.0.7',
            'port': '8080'
        }

        assert attrs == expected

    def test_reset_handlers(self):
        logger = LogmeLogger('reset_logger', self.config)
        handler_classes = [i.__class__ for i in logger.handlers]

        assert handler_classes[0] == logging.StreamHandler

        logger.reset_config(config_name='socket_config')

        assert logger.handlers[0].__class__ == logging.handlers.SocketHandler

    def test_reset_handler_rename(self):
        logger = LogmeLogger('rename_logger', self.config)

        assert logger.name == 'rename_logger'

        config = get_config_content(__file__, name='socket_config')
        logger.reset_config(config=config, name='logger_new_name')

        assert logger.name == 'logger_new_name'

    @pytest.mark.parametrize('args, message',
                             [pytest.param({'config_name': 'socket_config', 'config': {'formatter': 'hello'}},
                                           "Can only set keyword argument of either "
                                           "'config_name' or 'config', not both.",
                                           id='InvalidOption raised when both config_name and config are set'),
                              pytest.param({}, "must specify one of 'config_name' or 'config'.",
                                           id="InvalidOption raised when neither config_name nor config are set")])
    def test_reset_handlers_raise(self, args, message):
        with pytest.raises(InvalidOption) as e_info:
            self.logger.reset_config(**args)

        assert e_info.value.args[0] == message

    def test_config_handler_with_master(self):
        stream_handler = logging.StreamHandler()

        assert stream_handler.level == 0  # Level NOTSET
        assert stream_handler.formatter is None

        self.logger._config_handler(stream_handler, set_from_master=True)

        assert stream_handler.level == 10
        assert stream_handler.formatter is not None
        assert stream_handler.formatter._fmt == '{asctime} - {name} - {levelname} - {module}::{funcName}::{message}'

    @pytest.mark.parametrize('level',
                             [
                                 pytest.param('INFO', id='all upper case string'),
                                 pytest.param('Info', id='With lowercase string'),
                                 pytest.param(20, id='with int value passed'),
                             ])
    def test_config_handler_with_no_master(self, level):
        stream_handler = logging.StreamHandler()

        self.logger._config_handler(stream_handler, level=level)

        assert stream_handler.level == 20
        assert stream_handler.formatter is None

    def test_reconfig_handler(self, tmpdir):
        config = get_config_content(__file__, 'filehandler_conf')
        log_file = Path(tmpdir.join('mylog.log'))

        config['FileHandler']['filename'] = str(log_file)
        config['StreamHandler']['active'] = True

        logger = LogmeLogger('reconfig_handler_test', config)

        # Check original level
        assert logger.handlers[0].level == 10
        assert logger.handlers[1].level == 10
        logger.debug('hello, there')

        lines_before = self.get_log_file_lines(log_file)

        # Reconfigure and check current level
        logger.reconfig_handler('FileHandler', level=50)
        assert logger.handlers[0].level == 10
        assert logger.handlers[1].level == 50
        logger.info('hello')

        lines_after = self.get_log_file_lines(log_file)

        assert lines_before == lines_after

    def test_reconfigure_handler_raise_no_arg(self):
        with pytest.raises(InvalidOption):
            self.logger.reconfig_handler('StreamHandler')

    def test_reconfigure_handler_invalid_handler(self):
        with pytest.raises(LogmeError):
            self.logger.reconfig_handler('RotatingFileHandler', level=10)

    def test_get_handler_by_name(self):
        logger = LogmeLogger(name='my_logger', config=self.config)

        handler = logger.get_handler_by_name('StreamHandler')
        assert type(handler) == logging.StreamHandler

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------
    def get_log_file_lines(self, log_file):
        lines_list = []
        with open(log_file) as file:
            for line in file:
                lines_list.append(line)

        return lines_list






