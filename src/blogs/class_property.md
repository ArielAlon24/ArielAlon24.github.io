---
name: "Class Property Decorator"
date: 2024-12-30
---

## Background

One day, my cousin, a Python backend engineer, introduced me to a problem his team encountered that week at work, but couldn't solve.

## Problem

If you're familiar with Python's properties and classmethods, a specific feature might seem missing - why isn't there a decorator for class properties? A classmethod which is also a decroator.

Consider a class named `A` with a class attribute `metadata` that needs to be computed each time it's accessed. However, the computation isn't particularly intensive. Without a `class_property` decorator, it would look something like this:

```python
from datetime import datetime


class A:
    @classmethod
    def get_metadata(cls) -> str:
        return str(datetime.now())

```

This isn't convenient as we want to provide a way for the user to interact with metadata as a class attribute rather than a function.

## Investigation

My first thought for solving this problem was to chain decorators - using both `classmethod` and `property`. However, to my surprise, this exact functionality is deprecated from Python 3.11, as mentioned in the [Python docs](https://docs.python.org/3/howto/descriptor.html#class-methods).

I quickly realized descriptors could do the job, but I wasn't sure how. I started with the `__init__` method of the `class_property`, that will get the method it decorates as an argument. For naming conventions, I created a private class `_ClassProperty` and then renamed it to `class_property`. We will ignore the last assignment fron now on:

```python
class _ClassProperty:

    def __init__(self, function):
        self.function

class_property = _ClassProperty
```

For correct type hints I'll use a generic `T` to mark the given method return type:

```python
from typing import TypeVar, Generic, Callable


T = TypeVar("T")


class _ClassProperty(Generic[T]):

    def __init__(self, method: Callable[..., T]) -> None:
        self.method = method

```

Now for the interesting part, how can I call the `method` argument on access to a `_ClassProperty`? If you're familiar with Python's descriptor protocol, you'll certainly know the answer, otherwise here's a brief explenation.

## Brief overview on descriptor's `__get__` method

Luckily, the [Python descriptor protocol](https://docs.python.org/3/howto/descriptor.html#descriptor-howto-guide) allows implementing a `__get__(self, obj, objtype=None)` method. This method is called when a descriptor as an attribute is being accessed. For example:

```python
class Ten:
    def __get__(self, obj, objtype=None):
        return 10

class A:
    x = 5
    y = Ten()
```

```bash
>>> a.y     # Triggers the __get__ method (obj=a, objtype=A)
10
```

## Solution?

By using the `__get__` method, we can execute the `_ClassProperty` method and even supply it with the correct `cls` parameter (named `owner` for readability.):

```python
class _ClassProperty:

    ...

    def __get__(self, _, owner=None) -> T:
        if owner:
            return self.method(owner)
        raise TypeError("Owner must not be None (unreachable).")

```

This method can be called in two ways:

1.  on a class: Python will pass `owner=<class-type>`.
2.  on an instance: Python will provide the owner of the instance (the instance's type).

The `if` block exists mainly for safety, as there's no straightforward way (without special workarounds) to access this `__get__` with `owner=None`.

## Oh no

This approach looked promising and worked quite well, but it had a flaw. The need for this feature arose for use with Pydantic's `BaseModel`, but when used together, an error occurrs:

```console
raise PydanticUserError(
pydantic.errors.PydanticUserError: A non-annotated attribute was detected: `metadata = <class_property._ClassProperty object at 0x103559d10>`. All model fields require a type annotation; if `metadata` is not meant to be a field, you may be able to resolve this error by annotating it as a `ClassVar` or updating `model_config['ignored_types']`.
```

This was curious. How do regular `property`s work with Pydantic's `BaseModel`, and why don't they raise this error? Ignoring this entire curiosity an idea popped up - why not inherit from `property` itself:

```python
from typing import TypeVar, Generic, Callable

T = TypeVar("T")


class _ClassProperty(property, Generic[T]):

    def __init__(self, method: Callable[..., T]) -> None:
        super().__init__()
        self.method = method

    def __get__(self, _, owner=None) -> T:
        if owner:
            return self.method(owner)
        raise TypeError("Owner must not be None (unreachable).")

```

## Additional Safeguards

Just to ensure this decorator isn't being misused, I added an additional check for correct arguments. As a method decorated by `class_property` is both a `classmethod` and a `property`, it should only have `cls` as an argument. Using the `inspect` module, we can access the method's signature and validate its parameters. Finally, at 23 lines of code, we have it - a `class_property` decorator:

```python
from typing import TypeVar, Generic, Callable, Tuple
import inspect


T = TypeVar("T")


class _ClassProperty(property, Generic[T]):
    PARAMETERS: Tuple[str] = ("cls",)

    def __init__(self, method: Callable[..., T]) -> None:
        super().__init__()
        if not tuple(inspect.signature(method).parameters) == self.PARAMETERS:
            raise ValueError(f"Incorrect arguments, expected: {self.PARAMETERS}.")
        self.method = method

    def __get__(self, _, owner=None) -> T:
        if owner:
            return self.method(owner)
        raise TypeError("Owner must not be None (unreachable).")


class_property = _ClassProperty
```
