---
name: "Exploring A Lesser-Known Operator"
date: 2024-02-07
---

## Introduction

Many are familiar with Python's capability to customize the behavior of various operators through dunder methods. If you're new to this concept, it's quite straightforward. Let's explore an example that implements addition and subtraction for complex numbers.

First, we'll define a simple class to represent a complex number, complete with `__init__` and `__str__` methods for initialization and string representation, respectively.

```python
class Complex:

    def __init__(self, real: float, imaginary: float) -> None:
        self.real = real
        self.imaginary = imaginary

    def __repr__(self) -> str:
        return f"{self.real} + {self.imaginary}i"

```

```pycon
>>> c1 = Complex(real=1.0, imaginary=2.0)
1.0 + 2.0i
>>> c2 = Complex(real=3.0, imaginary=4.0)
3.0 + 4.0i
```

## Complex Addition

Attempting to add two `Complex` numbers without overriding the appropriate method will result in an error.

```pycon
>>> c1 + c2
Traceback (most recent call last):
  File "/Users/arielalon/Programming/Python/complex/main.py", line 18, in <module>
    print(c1 + c2)
          ~~~^~~~
TypeError: unsupported operand type(s) for +: 'Complex' and 'Complex'
```

But, we know how to add complex numbers—it's simply the sum of their real and imaginary parts. To accomplish this, we can use another dunder method: `__add__`.

```python
class Complex:

    ...

    def __add__(self, other: Complex) -> Complex:
        return Complex(
            real=self.real + other.real,
            imaginary=self.imaginary + other.imaginary
        )
```

Remember to import `__annotations__` from the `future` module to allow the use of the type annotation `Complex` within its body.

```pycon
>>> c1 + c2
4.0 + 6.0i
```

Great, now addition works! But that's not all—we can override the `-` operator with `__sub__`, the `*` operator with `__mul__`, and much more. You can find a list of basic arithmetic operations that can be implemented [here](https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types).

## The Unknown Operator

A few days ago, while working with [numpy](https://numpy.org/), an open-source numerical computing library, I stumbled upon an operator that I had never seen before: the `@` operator. In numpy, it's used for matrix multiplication, hence its dunder method name `__matmul__`. This operator, introduced in [PEP 465](https://peps.python.org/pep-0465/), was intended solely for matrix multiplication, which is why it doesn't even appear in Python's built-ins - Python doesn't have any matrix-related modules.

Does this mean the operator can only be used for this specific task? Not at all, but after searching for use cases, I couldn't find anything.

## Email Addresses

An email consists of two parts: the local part and the domain, separated by, well, you guessed it, an `@` symbol. The email address: `test@example.com`, has `test` as its local part and `example.com` as its domain. The dunder `__matmul__`, or specifically `__rmatmul__` (an `r` can be added to each binary operation dunder, signifying that this dunder will execute when the object is on the right-hand side of that operation, with the `other` parameter being the left-hand side), can be utilized to create a method to concatenate the local and domain parts of an email address in a pythonic way.

First, we need to define a class representing an email address, nothing too sophisticated:

```python
class Email:
    def __init__(self, local: str, domain: str) -> None:
        self.local = local
        self.domain = domain

    def __repr__(self) -> str:
        return f"{self.local}@{self.domain}"
```

Now, because we want achieve the ability to create an `Email` object using a `@` binary operation between two strings, we'll create a subclass of `str` for our domain type, as python wont allow creating dunder methods for built-in types.

```python
class Domain(str):
    def __init__(self, domain: str) -> None:
        super().__init__()
        self.domain = domain

    def __repr__(self) -> str:
        return super().__repr__()
```

Lastly, we'll add the `__rmatmul__` dunder to make that binary operation possible.

```python
from typing import Any

class Domain(str):
    ...

    def __rmatmul__(self, local: Any) -> Email:
        if not isinstance(local, str):
            raise TypeError(f"local must be of type str, found: {type(local)}.")
        return Email(local=local, domain=self)
```

Note that I added a check to ensure the left-hand side, named `local`, is of type string, just to ensure this operation isn't misused.

And there we have it! A simple and pythonic method for creating email addresses!

```pycon
>>> domain = Domain("example.com")
>>> local = "test"
>>> email = local @ domain
>>> email
test@example.com
```

Of course, this is more of a curiosity than a practical tool, but it's a great dive into Python's hidden dunder methods.
