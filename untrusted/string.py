import collections.abc
import untrusted
import untrusted.util
from typing import Any


class UndefinedType:
    pass


class String:
    _keyType = TypeError # NA
    _cast_error = "Implicit cast to/of untrusted.string is not allowed"

    # whitelist of methods to wrap that return a simple value e.g. boolean
    _safe_methods = set([
        '__eq__',
        '__gt__',
        '__gte__',
        '__len__',
        '__lt__',
        '__lte__',
        '__ne__',
        '__contains__',
        '__hash__',
        'count',
        'endswith',
        'find',
        'index',
        'isalnum',
        'isalpha',
        'isdecimal',
        'isdigit',
        'isidentifier',
        'islower',
        'isnumeric',
        'isprintable',
        'isspace',
        'istitle',
        'isupper',
        'rfind',
        'rindex',
        'startswith',
    ])

    # whitelist of methods to wrap that return a `str` value
    _simple_wrapped_methods = set([
        '__add__',
        '__mul__',
        '__rmul__',
        '__getitem__',
        'capitalize',
        'casefold',
        'center',
        'expandtabs',
        'format',
#        'format_map',
        'join',
        'ljust',
        'lower',
        'lstrip',
        'replace',
        'rstrip',
        'strip',
        'swapcase',
        'title',
        'upper',
        'zfill'
    ])

    # whitelist of methods to wrap that return some complicated type, e.g. a
    # list of strings, and we want them to be all wrapped by an appropriate
    # untrusted type
    _complex_wrapped_methods = {
        '__reversed__': untrusted.util._to_untrusted_iterator,
        'partition':    untrusted.util._to_untrusted_tuple_of_strings, # returns a 3-tuple
        'rpartition':   untrusted.util._to_untrusted_tuple_of_strings, # returns a 3-tuple
        'split':        untrusted.util._to_untrusted_list,
        'rsplit':       untrusted.util._to_untrusted_list,
        'splitlines':   untrusted.util._to_untrusted_list,
    }

    # disallowed: encode
    # not yet considered: maketrans, translate

    def __getattr__(self, name):
        return untrusted.util._wrapped_method(self, name)

    def __init__(self, value):
        if isinstance(value, untrusted.string):
            value = value.value
        if not isinstance(value, str):
            raise TypeError("Initialiser for an untrusted string must be an instance of str or untrusted.string")

        self._value = value

    def __add__(self, other: Any) -> 'String':
        # explicit so we can type it
        other = untrusted.util._wrap_arg(other)
        return self._valueType(self.value + other)

    def __radd__(self, other: Any) -> 'String':
        # underlying str doesn't implement __radd__ for us to wrap
        other = untrusted.util._wrap_arg(other)
        return self._valueType(other + self.value)

    def __bool__(self):
        # underlying str doesn't have __bool__ for us to wrap
        return not not self.value

    def __reversed__(self) -> 'String':
        # underlying str doesn't have __reversed__ for us to wrap
        return untrusted.iterator(reversed(self.value))

    def __mod__(self, arg) -> 'String':
        arg_type = type(arg)
        arg = untrusted.util._wrap_arg(arg)
        return self._valueType(self.value % arg_type(arg))

    def format_map(self, mapping) -> 'String':
        arg = untrusted.util._wrap_arg(mapping)
        return self._valueType(self.value.format_map(arg))

    def __str__(self) -> UndefinedType: # type: ignore
        raise TypeError(self._cast_error)

    def __repr__(self):
        return "<untrusted.string of length %d>" % len(self.value)

    @property
    def value(self) -> str:
        """Read only access to the raw `str` value."""
        return self._value

    @property
    def _valueType(self):
        return type(self)

    def __truediv__(self, args) -> str:
        # shorthand e.g. untrusted.string("hello") / html.escape
        if hasattr(args, '__iter__'):
            if len(args) == 2:
                fn, args = args
                return self.escape(fn, *args)
            else:
                fn, args, kwargs = args
                return self.escape(fn, *args, **kwargs)
        else:
            return self.escape(args)

    def escape(self, fn, *args, **kwargs) -> str:
        result = fn(self.value, *args, **kwargs)
        assert isinstance(result, str)
        return result

    def valid(self, fn, *args, **kwargs) -> bool:
        result = fn(self.value, *args, **kwargs)
        assert isinstance(result, bool)
        return result

    def validate(self, fn, *args, **kwargs):
        result = fn(self.value, *args, **kwargs)
        return result


# some magic to let us easily passthrough magic methods that are otherwise
# not picked up when operator overloading

_magicMethods = (untrusted.util._createMagicPassthroughBindings(
    ["add", "contains", "hash", "eq", "gt", "gte", "getitem", "len", "lt", "lte", "mul", "ne", "rmul"]
))

for k,v in _magicMethods.items():
    setattr(String, k, v)


# alias
string = String






