# -*- coding: utf-8 -*-

import pytest

import dump_env
from dump_env import Env, dump


@pytest.fixture(scope='session')
def env(env_file):
    return Env(env_file)


@pytest.mark.usefixtures('env')
class TestEnv(object):
    def test_env_normal(self, env):
        assert isinstance(env.data, dict)
        assert 'NORMAL_KEY' in env.data
        assert env.data['NORMAL_KEY'] == 'SOMEVALUE'

    def test_env_exceptions(self, env):
        assert isinstance(env.data, dict)
        assert 'COMMENTED_KEY' not in env.data
        assert 'KEY_WITH_NO_ASSIGNMENT' not in env.data


@pytest.mark.usefixtures('monkeypatch', 'env_file')
class TestDump(object):
    @staticmethod
    def simple_environ(prefix=''):
        return {
            '{}key'.format(prefix): 'value',
            'a': 'b',
        }

    def test_with_default_arguments(self, monkeypatch):
        monkeypatch.setattr(dump_env, 'environ', self.simple_environ())
        result = dump()

        assert list(result.keys()) == ['a', 'key']
        assert result['key'] == 'value'
        assert result['a'] == 'b'

    def test_with_prefix(self, monkeypatch):
        prefix = 'P_'
        monkeypatch.setattr(
            dump_env, 'environ', self.simple_environ(prefix=prefix),
        )
        result = dump(prefix=prefix)

        assert len(result.keys()) == 1
        assert result['key'] == 'value'

    def test_with_template(self, monkeypatch, env_file):
        monkeypatch.setattr(dump_env, 'environ', self.simple_environ())
        result = dump(template=env_file)

        assert list(result.keys()) == ['NORMAL_KEY', 'a', 'key']
        assert result['key'] == 'value'
        assert result['a'] == 'b'
        assert result['NORMAL_KEY'] == 'SOMEVALUE'

    def test_with_two_options(self, monkeypatch, env_file):
        prefix = 'P_'
        monkeypatch.setattr(
            dump_env, 'environ', self.simple_environ(prefix=prefix),
        )
        result = dump(template=env_file, prefix=prefix)

        assert list(result.keys()) == ['NORMAL_KEY', 'key']
        assert result['key'] == 'value'
        assert result['NORMAL_KEY'] == 'SOMEVALUE'


@pytest.mark.usefixtures('monkeypatch', 'env_file')
class TestDumpRegression(object):
    @staticmethod
    def same_environ():
        return {
            'NORMAL_KEY': 'test',
        }

    @staticmethod
    def multiple_prefix():
        return {
            'SECRET_DJANGO_SECRET_KEY': 'test',
            'SECRET_SECRET_VALUE': 'value',
        }

    def test_same_environ(self, monkeypatch, env_file):
        monkeypatch.setattr(
            dump_env, 'environ', self.same_environ(),
        )
        result = dump(template=env_file)

        # Should contain the value from env, not from template:
        assert result['NORMAL_KEY'] == 'test'

    def test_multiple_prefix(self, monkeypatch, env_file):
        monkeypatch.setattr(
            dump_env, 'environ', self.multiple_prefix(),
        )
        result = dump(template=env_file, prefix='SECRET_')

        # Only prefix should be changed, other parts should not:
        assert result['DJANGO_SECRET_KEY'] == 'test'
        assert result['SECRET_VALUE'] == 'value'
