from collections import ChainMap
import functools
from inspect import signature


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
             provider = getattr(self.provider_factory, attr)
             return ProviderFactory.provide(self.provider_factory, provider=provider)

         def __call__(self, fct):
             sig = signature(fct)
             is_missing_arg = sig.parameters.get(self.provider.__name__) is None
             if is_missing_arg:
                 raise LookupError(
                     "no arg/kwarg of name '{}' found for fct '{}'".format(
                         self.provider.__name__,
                         fct.__name__,
                     )
                 )
             @functools.wraps(fct)
             def inner(*args, **kwargs):
                 return functools.partial(fct, self.provider())(*args, **kwargs)
             return inner


    def __init__(self):
        self.providers = {}
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
    def i_have_providers(i_provide=1, i_provide_too=2, not_provided=3):
        return i_provide + i_provide_too


    print(i_have_providers())


    @hug.provide.i_provide
    @hug.provider
    def i_provide():
        


    # TODO implement
    # hug.assert_all_nullary_callables()
