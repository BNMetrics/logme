import pytest

import logging
from pathlib import Path

import logme.providers
from logme.providers import LogmeLogger
from logme.config import get_config_content
from logme.exceptions import DuplicatedHandler, InvalidOption, LogmeError


class TestLogmeLogger:

    @classmethod
    def setup_class(cls):
        cls.config = get_config_content(__file__)
    # def setup_method(self, method):
    #     self.config = get_config_content(__file__)
    #     self.logger = LogmeLogger('test_logger', self.config)
    #
    #     self.ver11_conf = get_config_content(__file__, 'ver11_config')
    #     self.ver11_logger = LogmeLogger('test_ver11', self.ver11_conf)
    #
    # def teardown_method(self, method):
    #     # for i, j in zip(logger_from_provider.logger.handlers, self.ver11_logger.logger.handlers):
    #     #     logger_from_provider.removeHandler(i)
    #     #     self.ver11_logger.removeHandler(j)
    #
    #     for i in logger_from_provider.logger.handlers:
    #         logger_from_provider.removeHandler(i)
    #
    #     for j in self.ver11_logger.logger.handlers:
    #         self.ver11_logger.removeHandler(j)
    #
    #     logger_from_provider.handlers = {}
    #     self.ver11_logger.handlers = {}

    # ---------------------------------------------------------------------------
    # Test overall functionality
    # ---------------------------------------------------------------------------

    def test_logger(self, logger_from_provider):
        assert logger_from_provider.level == 10

    def test_logging(self, caplog, logger_from_provider):
        logger_from_provider.info('my logging message')
        captured = caplog.record_tuples[0]

        assert captured[0] == 'test_logger'
        assert captured[1] == 20
        assert captured[2] == 'my logging message'

    def test_non_existent_attr(self, logger_from_provider):
        with pytest.raises(AttributeError) as e_info:
            logger_from_provider.foo()

        assert e_info.value.args[0] == "LogmeLogger object has no attribute 'foo'."

    def test_set_handlers_twice(self, logger_from_provider):
        """Should not set duplicated handlers"""
        with pytest.raises(LogmeError):
            logger_from_provider._set_handlers_from_conf()

    def test_logger_handler(self, logger_from_provider):
        assert type(logger_from_provider.handlers) == dict
        assert list(logger_from_provider.handlers.values()) == logger_from_provider.logger.handlers

    def test_logger_handler_ver11_custom_name(self, ver11_logger):
        stream = ver11_logger.handlers['stream']

        assert stream == ver11_logger.logger.handlers[0]
        assert type(stream) == logging.StreamHandler
        assert list(ver11_logger.handlers.values()) == ver11_logger.logger.handlers

    def test_filehandler(self, file_config_content):
        logger = LogmeLogger('file_logger', file_config_content)

        logger.info('my log message for file handler')

        log_path = Path(file_config_content['FileHandler']['filename'])
        assert log_path.exists()

        with open(log_path) as file:
            assert file.readline() == 'file_logger::my log message for file handler\n'

    # ---------------------------------------------------------------------------
    # Test individual methods
    # ---------------------------------------------------------------------------
    def test_get_handler_args(self, monkeypatch, logger_from_provider):
        # Patch ensure_dir, so the arbitrary directory is not created
        monkeypatch.setattr(logme.providers, 'ensure_dir', lambda x: True)

        args = logger_from_provider._get_handler_args('FileHandler')
        expected = {'filename': 'mylogpath/foo.log'}

        assert args == expected

    def test_get_handler_type(self, logger_from_provider):
        handler_type = logger_from_provider._get_handler_type('FileHandler')
        assert handler_type == 'FileHandler'

    def test_set_handlers_handler_level_config(self, tmpdir):
        """
        Ensure master_level applies to handlers without *level* config set on individual handler
        """
        config = get_config_content(__file__, 'my_test_logger')

        logger = LogmeLogger('handler_level_conf', config)

        handler = logger.handlers['StreamHandler']

        assert handler.level == 20  # INFO
        assert handler.formatter._fmt == '{asctime}::{message}'

    def test_config_handler_with_master(self, logger_from_provider):
        stream_handler = logging.StreamHandler()

        assert stream_handler.level == 0  # Level NOTSET
        assert stream_handler.formatter is None

        logger_from_provider._config_handler(stream_handler, set_from_master=True)

        assert stream_handler.level == 10
        assert stream_handler.formatter is not None
        assert stream_handler.formatter._fmt == '{asctime} - {name} - {levelname} - {module}::{funcName}::{message}'

    def test_config_handler_with_no_master(self, logger_from_provider):
        stream_handler = logging.StreamHandler()

        logger_from_provider._config_handler(stream_handler, level='INFO')

        assert stream_handler.level == 20
        assert stream_handler.formatter is None

    @pytest.mark.parametrize('level',
                             [
                                 pytest.param('INFO', id='all upper case string'),
                                 pytest.param('Info', id='With lowercase string'),
                                 pytest.param(20, id='with int value passed'),
                             ])
    def test_get_level(self, level, logger_from_provider):
        assert logger_from_provider._get_level(level) == 20

    def test_handler_exist_true(self, logger_from_provider):
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('{asctime} - {name} - {levelname} - {module}::{funcName}::{message}')
        stream_handler.setFormatter(formatter)

        assert logger_from_provider._handler_exist(stream_handler)

    def test_handler_exist_false(self, logger_from_provider, ver11_logger):
        handler = ver11_logger.handlers['stream']

        assert not logger_from_provider._handler_exist(handler)

    def test_add_handler_filehandler(self, tmpdir, logger_from_provider):
        # Check handlers before adding additional one
        assert len(logger_from_provider.handlers) == 1
        assert logger_from_provider.handlers['StreamHandler'].__class__ == logging.StreamHandler

        logger_from_provider.add_handler('file', 'FileHandler', formatter='{name}->{message}',
                                         level='debug', filename=str(tmpdir.join('dummy.log')))

        # Check handler after adding filehandler
        assert len(logger_from_provider.handlers) == 2
        assert set(map(lambda x: x.__class__, logger_from_provider.handlers.values())) == \
               {logging.StreamHandler, logging.FileHandler}

        assert set(logger_from_provider.handlers.values()) == set(logger_from_provider.logger.handlers)

    def test_add_handler_sockethandler(self, logger_from_provider):
        assert len(logger_from_provider.handlers) == 1

        logger_from_provider.add_handler('socket', 'SocketHandler', formatter='{name}->{message}',
                                         level='debug', host='127.0.0.5', port=55)

        handler_types = [i.__class__.__name__ for i in logger_from_provider.handlers.values()]

        assert len(logger_from_provider.handlers) == 2
        assert 'SocketHandler' in handler_types
        assert 'socket' in logger_from_provider.handlers

    @pytest.mark.parametrize('handler_name, error',
                             [
                                 pytest.param('file', LogmeError,
                                              id='When the handler name already exists in the logger'),
                                 pytest.param('file2', DuplicatedHandler,
                                              id='When handler with the same configuration exists'),
                             ])
    def test_add_handler_raise(self, tmpdir, logger_from_provider, handler_name, error):
        logger_from_provider.add_handler('file', 'FileHandler', formatter='{name}->{message}',
                                         level='debug', filename=str(tmpdir.join('dummy.log')))

        with pytest.raises(error):
            logger_from_provider.add_handler(handler_name, 'FileHandler', formatter='{name}->{message}',
                                             level='debug', filename=str(tmpdir.join('dummy.log')))

    def test_add_handler_allow_dup(self, logger_from_provider):
        logger = LogmeLogger('allow_duplicate', self.config)

        assert len(logger.handlers) == 1
        assert logger.handlers['StreamHandler'].__class__ == logging.StreamHandler

        logger.add_handler('stream2', 'StreamHandler',
                           formatter='{asctime} - {name} - {levelname} - {module}::{funcName}::{message}',
                           level='debug', allow_duplicate=True)

        assert len(logger.handlers) == 2
        assert logger._get_handler_attr(logger.handlers['StreamHandler']) == \
               logger._get_handler_attr(logger.handlers['stream2'])

    @pytest.mark.parametrize('handler_class',
                             [
                                 pytest.param(logging.FileHandler, id='logging FileHandler'),
                                 pytest.param(logging.handlers.WatchedFileHandler, id='logging WatchedFileHandler'),
                                 pytest.param(logging.handlers.RotatingFileHandler, id='logging RotatingFileHandler'),
                             ])
    def test_ensure_filepath(self, logger_from_provider, tmpdir, handler_class):
        log_file = tmpdir.join('blah/test.log')
        logger_from_provider._ensure_filepath(handler_class, filename=log_file)

        assert Path(log_file).parent.exists()

    def test_ensure_filepath_raise(self, logger_from_provider):
        with pytest.raises(ValueError):
            logger_from_provider._ensure_filepath(logging.FileHandler)

    def test_get_handler_attr(self, socket_handler, logger_from_provider):
        attrs = logger_from_provider._get_handler_attr(socket_handler)

        expected = {
            'formatter': '{asctime} - {name}::{message}',
            'level': 10,
            'host': '127.0.0.7',
            'port': '8080'
        }

        assert attrs == expected

    def test_reset_config(self, logger_from_provider):
        # Ensure handlers before change
        assert type(logger_from_provider.handlers['StreamHandler']) == logging.StreamHandler
        assert list(logger_from_provider.handlers.keys()) == ['StreamHandler']

        logger_from_provider.reset_config(config_name='socket_config')

        # Test reset changes
        assert type(logger_from_provider.handlers['SocketHandler']) == logging.handlers.SocketHandler
        assert list(logger_from_provider.handlers.values()) == logger_from_provider.logger.handlers

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
    def test_reset_handlers_raise(self, logger_from_provider, args, message):
        with pytest.raises(InvalidOption) as e_info:
            logger_from_provider.reset_config(**args)

        assert e_info.value.args[0] == message

    def test_reconfig_handler(self, tmpdir):
        config = get_config_content(__file__, 'filehandler_conf')
        log_file = Path(tmpdir.join('mylog.log'))

        config['FileHandler']['filename'] = str(log_file)
        config['StreamHandler']['active'] = True

        logger = LogmeLogger('reconfig_handler_test', config)

        # Check original level
        assert list(logger.handlers.values()) == logger.logger.handlers
        assert logger.handlers['StreamHandler'].level == 10
        assert logger.handlers['FileHandler'].level == 10
        logger.debug('hello, there')

        lines_before = self.get_log_file_lines(log_file)

        # Reconfigure and check current level
        logger.reconfig_handler('FileHandler', level=50)

        assert list(logger.handlers.values()) == logger.logger.handlers
        assert logger.handlers['StreamHandler'].level == 10
        assert logger.handlers['FileHandler'].level == 50

        logger.info('hello')

        lines_after = self.get_log_file_lines(log_file)

        assert lines_before == lines_after

    def test_reconfigure_handler_raise_no_arg(self, logger_from_provider):
        with pytest.raises(InvalidOption):
            logger_from_provider.reconfig_handler('StreamHandler')

    def test_reconfigure_handler_invalid_handler(self, logger_from_provider):
        with pytest.raises(LogmeError):
            logger_from_provider.reconfig_handler('RotatingFileHandler', level=10)

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------
    def get_log_file_lines(self, log_file):
        lines_list = []
        with open(log_file) as file:
            for line in file:
                lines_list.append(line)

        return lines_list






