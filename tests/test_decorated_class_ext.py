import pytest
import types

from .dummy_stubs import (DummyClassForExtension, dummy_function_default,
                          DummyClassCustom)

from logme.providers import LogmeLogger

obj = DummyClassForExtension('myarg1', 'myarg2')
obj_custon_name = DummyClassCustom('myarg')


def test_valid_typing_class():
    assert type(DummyClassForExtension) == type
    assert type(DummyClassCustom) == type

    assert type(obj) == DummyClassForExtension
    assert type(obj_custon_name) == DummyClassCustom

def test_valid_typing_function():
    #  <class 'function'>
    assert type(dummy_function_default) == types.FunctionType


def test_class_logging_working_properly(caplog):
    obj.log_this()
    assert obj_custon_name.logger.name == 'custom_class_logger'
    assert caplog.record_tuples[0] == ('tests.dummy_stubs', 20, 'my logging message')


def test_isinstance_dummyclass():
    assert isinstance(obj, DummyClassForExtension)


def test_isinstance_function():
    # Check if dummy_function() is instance a function type
    assert isinstance(dummy_function_default, types.FunctionType)


def test_extending_decorated_class():
    class MyExtended(DummyClassForExtension):
        def __init__(self, arg1, arg2):
            super().__init__(arg1, arg2)

    extended_obj = MyExtended('a1', 'a2')

    assert extended_obj.arg1 == 'a1'
    assert hasattr(extended_obj, 'logger')
    assert isinstance(extended_obj.logger, LogmeLogger)

