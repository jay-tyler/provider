from collections import ChainMap
import functools
from inspect import signature


class ProviderFactory:
    class provide:
         def __init__(self, provider_factory, provider=None):
             self.provider_factory = provider_factory
             self.provider = provider

         def __getattr__(self, attr):
             provider = getattr(self.provider_factory, attr)
             return ProviderFactory.provide(self.provider_factory, provider=provider)

         def __call__(self, fct):
             @functools.wraps(fct)
             def inner(*args, **kwargs):
                 sig = signature(fct)
                 assert sig.parameters.get(self.provider.__name__) is not None
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


    @hug.provide.i_provide
    def i_have_provider(i_provide):
        return i_provide


    print(i_have_provider())