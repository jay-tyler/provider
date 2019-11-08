#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import provider.provider


@pytest.fixture
def provider_factory():
    return provider.provider.ProviderFactory()


@pytest.fixture
def provider1(provider_factory):
    @provider_factory.provider()
    def provider1():
        return 42
    return provider1


@pytest.fixture
def provided1(provider_factory, provider1):
    @provider_factory.provide.provider1
    def provided1(provider1):
        return provider1
    return provided1


def test_provider1_instantiation(provider1):
    assert provider1


def test_provided1_instantiations(provided1):
    assert provided1


def test_provided1_call(provided1):
    assert provided1() == 42


def test_provided_missing_provider(provider_factory):
    with pytest.raises(AttributeError) as excinfo:
        @provider_factory.provide.provider1
        def provided1(provider1):
            return provider1
    assert "no provider named 'provider1'" in str(excinfo.value)


def test_provided_missing_arg(provider_factory, provider1):
    with pytest.raises(LookupError) as excinfo:
        @provider_factory.provide.provider1
        def provided1():
            return provider1
    assert "expected arg/kwarg of name 'provider1' in fct 'provided1'" in str(excinfo.value)


def test_provided_misnamed_arg(provider_factory, provider1):
    with pytest.raises(LookupError) as excinfo:
        @provider_factory.provide.provider1
        def provided1(not_the_right_arg):
            return provider1
    assert "expected arg/kwarg of name 'provider1' in fct 'provided1'" in str(excinfo.value)


def test_no_nullary_callable_hook(provider_factory, provider1):
    @provider_factory.provide.provider1
    def provided1(provider1, not_a_known_arg):
        return provider1


