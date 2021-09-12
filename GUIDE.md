# Guide

## Poetry installation

Note that poetry needs to be installed in isolated environment. So refrain from `pip install poetry`

https://python-poetry.org/docs/master/#installation

```bat
activate base
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python - --version 1.2.0a2
```

Open new terminal and check version

```bat
poetry --version
```

## Getting started with ppw

+ use ppw to start with
+ use invoke instead of fire
+ use docausaurus instead of mkdocs

Need to stick with something as there are lot of things to try

We use ppw to make this project
+ [refer](https://zillionare.github.io/cookiecutter-pypackage/tutorial/)

We will replace tox commands from tox.ini to use tasks.py which uses invoke

Then ...
+ Then replace mkdocs to docausaurus
  + As this has website and blog
  + support for API documentation
  + MDX components
  + multi-platform doc i.e. for mobile, desktop etc ...

## Badges

+ You can generate badges and display status
  + https://shields.io/category/coverage

+ Add badges for social networking too ...

## Gen inspirations for different files from

[pyproject.toml](https://github.com/python-poetry/poetry-core/blob/master/pyproject.toml)

[.pre-commit-config.yaml](https://github.com/python-poetry/poetry-core/blob/master/.pre-commit-config.yaml)

[workflows](https://github.com/python-poetry/poetry-core/tree/master/.github/workflows)


## CLI for toolcraft using `cleo`

+ tasks
  + Note the `tasks.py` is for toolcraft management may be not needed.
  + May be, avoid imperative programming for library management.


+ tools
  + we will continue using `typer` instead of `cleo`
  + But anyways get inspiration from poetry library
    + https://github.com/python-poetry/poetry/tree/master/poetry/console/commands

## Understand `tox` and `tox-gh-actions`

Refer
+ https://github.com/ymyzk/tox-gh-actions
