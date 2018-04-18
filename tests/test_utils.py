import pytest

from pathlib import Path

from logme.exceptions import InvalidOption
from logme.utils import (dict_to_conf, conf_to_dict, ensure_dir, check_scope,
                         conf_item_to_dict, strip_blank_recursive, cd)


class TestPackageUtils:


    @classmethod
    def setup(cls):

        cls.sample_dict = {
            "level": "DEBUG",
            "format": "%(levelname)s: %(message)s",
            "StreamHandler": {
                "level": "DEBUG",
            },
            "FileHandler": {
                "level": "DEBUG",
                "filename": "/var/log/mylog.log",
            },
        }

        cls.sample_conf_dict = {
            "level": "DEBUG",
            "format": "%(levelname)s: %(message)s",
            "StreamHandler": "\nlevel: DEBUG",
            "FileHandler": f"\nlevel: DEBUG"
                           f"\nfilename: /var/log/mylog.log",
        }

        cls.conf_section = [(k, v) for k, v in cls.sample_conf_dict.items()]

    def test_conf_section_to_dict(self):
        output = conf_to_dict(self.conf_section)

        assert output == self.sample_dict

    @pytest.mark.parametrize('parse_option',
                             [pytest.param(" \ntype: option \n second_val : my_val ",
                                           id='config options with blank space in the beginning and middle'),
                              pytest.param("\n  type  : option    \n  second_val : my_val \n",
                                           id='config option with blank space after new line, '
                                              'and new line after last option'),
                              pytest.param("\ntype: option \nsecond_val: my_val ",
                                           id='config option with no blank space')])
    def test_conf_item_to_dict(self, parse_option):
        expected_dict = {'type': 'option',
                         'second_val': 'my_val'}
        output = conf_item_to_dict(parse_option)

        assert expected_dict == output

    @pytest.mark.parametrize('parse_option',
                             [pytest.param(['blah', 'test'], id='when option passed is a list'),
                              pytest.param(20, id='when option passed is an int'),
                              pytest.param({'blah': 'test'}, id='when option passed is a dict'),
                              pytest.param("\nhello\nbye", id='when option passed is in invalid format'),
                              pytest.param("\nhello: hi\nbye", id='when option passed is in invalid format'),
                              ])
    def test_conf_item_to_dict_raise(self, parse_option):
        with pytest.raises(InvalidOption):
            conf_item_to_dict(parse_option)

    def test_dict_to_conf(self):

        flattened = dict_to_conf(self.sample_dict)

        assert flattened == self.sample_conf_dict

    @pytest.mark.parametrize('parse_dict',
                             [pytest.param({'test': 'test1', 'int_val': 1},
                                           id='when one of the dict value is integer'),
                              pytest.param({'test': 'test1', 'list_val': [1,2,3,4,5]},
                                           id='when one of the dict value is list')
                              ])
    def test_dict_to_conf_raise(self, parse_dict):
        with pytest.raises(ValueError):
            dict_to_conf(parse_dict)

    @pytest.mark.parametrize('iterable_, expected',
                             [pytest.param(['hello ', '\nhi ', 1], ['hello', 'hi', 1],
                                           id='when the iterable passed is not nested'),
                              pytest.param([[' hello ', 'hi \n'], [1, ' blah ', ' bye']],
                                           [['hello', 'hi'], [1, 'blah', 'bye']],
                                           id='when the iterable passed has nested list'),
                              pytest.param([[' hello ', 'hi \n'], [1, ' blah ', ' bye'], 'greet '],
                                           [['hello', 'hi'], [1, 'blah', 'bye'], 'greet'],
                                           id='when a tuple is passed and it has nested list and tuple'),
                              ])
    def test_strip_blank_recursive(self, iterable_, expected):
        strip_blank_recursive(iterable_)

        assert iterable_ == expected

    @pytest.mark.parametrize('parse_arg', [pytest.param(1, id='int value passed'),
                                           pytest.param('hello foo bar', id='string value passed'),
                                           pytest.param(('hello', 'hi'), id='tuple value passed')
                                           ])
    def test_strip_blank_recursive_rase(self, parse_arg):
        with pytest.raises(ValueError):
            strip_blank_recursive(parse_arg)

    @pytest.mark.parametrize('subpath, path_type, expected_path',
                             [pytest.param('test/my_test_dir', 'current', 'test/my_test_dir',
                                           id='make sure the exact dir exists'),
                              pytest.param('foo/my_dir/myfile.txt', 'parent', 'foo/my_dir',
                                           id='make sure the parent dir exists')])
    def test_ensure_dir(self, tmpdir, subpath, path_type, expected_path):
        dir_path = Path(tmpdir) / Path(subpath)

        ensure_dir(dir_path, path_type=path_type)

        assert (Path(tmpdir) / Path(expected_path)).exists()

    def test_ensure_dir_raise(self, tmpdir):
        with pytest.raises(InvalidOption):
            ensure_dir(tmpdir, path_type='cwd')

    @pytest.mark.parametrize('scope, options', [pytest.param('function', ['function', 'class']),
                                                pytest.param('class', ['function', 'class', 'module', 'blah'])])
    def test_check_scope_function(self, scope, options):
        assert check_scope(scope, options) is True

    def test_cd(self, tmpdir):

        original_cwd = Path.cwd()

        with cd(tmpdir):
            assert Path.cwd() == tmpdir
            assert Path.cwd() != original_cwd

        assert original_cwd == Path.cwd()

