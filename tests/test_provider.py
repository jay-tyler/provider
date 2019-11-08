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
def provider2(provider_factory):
    @provider_factory.provider()
    def provider2():
        return 53
    return provider2

@pytest.fixture
def provided1(provider_factory, provider1):
    @provider_factory.provide.provider1
    def provided1(provider1):
        return provider1
    return provided1


@pytest.fixture
def hybrid_provider_providee(provider_factory, provider1, provider2):
    @provider_factory.provider()
    @provider_factory.provide.provider1
    @provider_factory.provide.provider2
    def hybrid_provider_providee(provider1, provider2, not_provided=3):
        return provider1 + provider2
    return hybrid_provider_providee

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


def test_nullary_callable_simple_fail(provider_factory, provider1):
    @provider_factory.provide.provider1
    def provided1(provider1, not_a_known_arg):
        return provider1
    with pytest.raises(RuntimeError):
        provider_factory.assert_all_nullary_callables()


def test_nullary_callable_pass_with_default_kwarg(provider_factory, provider1):
    @provider_factory.provide.provider1
    def provided1(provider1, not_a_known_arg=1):
        return provider1
    try:
        provider_factory.assert_all_nullary_callables()
    except AssertionError:
        pytest.fail("nullary callable with false raise")


def test_hybrid_provider_providee_as_providee(hybrid_provider_providee, provider1, provider2):
    assert hybrid_provider_providee() == provider1() + provider2()


def test_hybrid_provider_providee_as_provider(provider_factory, hybrid_provider_providee, provider1, provider2):
    @provider_factory.provide.hybrid_provider_providee
    def foo(hybrid_provider_providee):
        return hybrid_provider_providee

    assert foo() == provider1() + provider2()
