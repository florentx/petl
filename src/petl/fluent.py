"""
As the root :mod:`petl` module but with modifications to allow for fluent style
usage.

.. versionadded:: 0.6

"""


import sys
from .util import valueset, RowContainer


petl = sys.modules['petl']
thismodule = sys.modules[__name__]


class FluentWrapper(object):
    
    def __init__(self, inner):
        object.__setattr__(self, '_inner', inner)

    def __iter__(self):
        return iter(self._inner)

    def __getattr__(self, attr):
        # pass through
        return getattr(self._inner, attr) 
    
    def __setattr__(self, attr, value):
        # pass through
        setattr(self._inner, attr, value)
        
    def __getitem__(self, item):
        # pass through
        return self._inner[item]
    
    def __setitem__(self, item, value):
        # pass through
        self._inner[item] = value

    def __str__(self):
        return str(self._inner)

    def __repr__(self):
        return repr(self._inner)


# define a wrapper function
def wrap(f):
    def wrapper(*args, **kwargs):
        _innerresult = f(*args, **kwargs)
        if isinstance(_innerresult, RowContainer): 
            return FluentWrapper(_innerresult)
        else:
            return _innerresult
    wrapper.__name__ = f.__name__
    wrapper.__doc__ = f.__doc__
    return wrapper

        
# import and wrap all functions from root petl module
for n, c in petl.__dict__.items():
    if callable(c):
        setattr(thismodule, n, wrap(c))
    else:
        setattr(thismodule, n, c)


# add module functions as methods on the wrapper class
# TODO add only those methods that expect to have row container as first argument
for n, c in thismodule.__dict__.items():
    if callable(c):
        setattr(FluentWrapper, n, c) 
        
        
# need to manually override for facet(), because it returns a dict 
def facet(table, field):
    fct = dict()
    for v in valueset(table, field):
        fct[v] = getattr(thismodule, 'selecteq')(table, field, v)
    return fct


# need to manually override for diff(), because it returns a tuple 
def diff(*args, **kwargs):
    a, b = petl.diff(*args, **kwargs)
    return FluentWrapper(a), FluentWrapper(b)

    



