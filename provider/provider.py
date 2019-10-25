from collections import ChainMap
import functools
from inspect import signature, Parameter

class RuntimeProvided: pass

class ProviderFactory:
    class provide:
         def __init__(self, provider_factory, provider=None):
             """

             :param provider_factory:
             :param provider:
             """
             self.provider_factory = provider_factory
             self.provider = provider

         def __getattr__(self, attr):
             # TODO prevent provider chaining
             provider = getattr(self.provider_factory, attr)
             return ProviderFactory.provide(self.provider_factory, provider=provider)

         def __call__(self, fct):
             sig = signature(fct)
             is_missing_expected_arg = sig.parameters.get(self.provider.__name__) is None
             if is_missing_expected_arg:
                 raise LookupError(
                     "expected arg/kwarg of name '{}' in fct '{}'".format(
                         self.provider.__name__,
                         fct.__name__,
                     )
                 )
             @functools.wraps(fct)
             def inner(*args, **kwargs):
                 return functools.partial(fct, self.provider())(*args, **kwargs)

             # TODO: stuff this bit into a function
             bound_param = Parameter(name=self.provider.__name__,
                           kind=Parameter.POSITIONAL_OR_KEYWORD,
                           default=RuntimeProvided())
             other_params = (
                 param for param in signature(fct).parameters.values()
                 if param.name != self.provider.__name__
             )
             sig = signature(fct).replace(parameters=[*other_params, bound_param])
             inner.__signature__ = sig

             self.provider_factory.providees[inner.__name__] = inner

             return inner

    def __init__(self):
        self.providers = {}
        self.providees = {}
        self.provide = ProviderFactory.provide(self)

    def __getattr__(self, attr):
        try:
            provider = self.providers[attr]
        except KeyError:
            raise AttributeError("no provider named '{}'".format(attr))
        return provider

    def register_provider(self, fct):
        self.providers[fct.__name__] = fct

    # TODO typing
    # TODO optional non-call
    def provider(self, scope=None, interfaces=None):
        def outer(fct):
            self.register_provider(fct)
            # TODO ensure callable is nullary here
            # TODO ensure callable has connascence with fct sig

            @functools.wraps(fct)
            def inner(*args, **kwargs):
                return fct(*args, **kwargs)

            return inner
        return outer

    def assert_all_nullary_callables(self):
        """
        Assert all of the providees have fully bound args

        Note that providee functions must be accessible in this namespace

        Whether this is necessary will be dependent on context, but if this is what you need in your library,
        this is your hook

        Raises RuntimeError in case of callables not being fully bound.

        :return:
        """
        # for fct_name, provider in self.providers.items()
        # TODO this requires fct_names be accessible in this context
        for fct_name, fct in self.providees.items():
            assert_nullary_callable(fct)



def assert_nullary_callable(fct):
    sig = signature(fct)
    for param in sig.parameters.values():
        if param.kind == Parameter.POSITIONAL_OR_KEYWORD:
            if param.default is not Parameter.empty:
                continue
            # else continue to exception
        else:
            # VAR_POSITION or VAR_KEYWORD, both optional
            continue
        raise RuntimeError(
            "'{}' requires '{}' param; not a nullary callable".format(
                fct.__name__, param.name
            )
        )


if __name__ == "__main__":
    hug = ProviderFactory()


    @hug.provider()
    def i_provide():
        return 42


    @hug.provider()
    def i_provide_too():
        return 42 + 1


    @hug.provide.i_provide
    def i_have_provider(i_provide):
        return i_provide

    print(i_have_provider())

    @hug.provide.i_provide
    @hug.provide.i_provide_too
    def i_have_providers(i_provide, i_provide_too, not_provided=3):
        return i_provide + i_provide_too


    print(i_have_providers())




    # TODO implement
    # hug.assert_all_nullary_callables()
    print(i_have_provider())
