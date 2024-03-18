---
name: "Typelate 0.1.0"
date: 2024-03-11
---

## The `format` method

With [PEP 3101](https://peps.python.org/pep-3101/) came a new way to format strings, this formatting technique later established what we know as Python's f-strings (in [PEP 498](https://peps.python.org/pep-0498/)). Shortly, it adds placeholders in strings marked with `{}` those placeholders can be later then _formatted_ with values using the `format` method.

In the last years Python and type safety came closely related when the use of type annotations became the standard. But those template using the `format` method stayed unsafe. Which made me think why not incorporate type annotations into those template string.

## Introducing `typelate`

With the `typelate` module, you can create templates and add type annotations to the placeholders later will be replaced by actual values. Let's create a simple example

```python
from typelate import Template

template = Template("Hello, {name: str}!")
```

Here `template` is a simple template that has a `name` placeholder of type `str`. We can use it by calling the template (`__call__`) with the correct parameters.

```pycon
>>> template(name="World")
"Hello, World!"
```

Now, let's pass an invalid type.

```pycon
>>> template(name=123)
TypeError: Incorrect type for replacement 'name', expected: <class 'str'>.
```

### Advanced functionality

1. Format specifiers can be used with `typelate` templates as well:

```pycon
>>> template = Template("pi is: {number: float: .2f}")
>>> template(number=math.pi)
"pi is 3.14"
```

2. You can use local or global classes and types in your template:

```python
from typelate import Template

class A:
    pass

template = Template("A global class: {a: A}")
```

3. The `Template` is wrapped around `str`, which means all `str` methods can be used on `Template`s:

```python
from typelate import Template

template = Template("Hello, {name: str}!")

assert template.count("l") == 2
```

## Installation

`typelate` can be installed via `pip`:

```bash
$ pip install typelate
```
