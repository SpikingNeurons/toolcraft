# Guide

## How to do Readme

How to get readme
+ https://readme.so/editor
+ https://www.youtube.com/watch?v=K7jeBfiNqR4

## Visual Programming

+ [pygame based](https://github.com/IndiePython/nodezator)
+ [blender based](https://stackoverflow.com/questions/21859936/is-there-a-python-reusable-component-that-is-like-the-blender-node-editor)

## ASGI server

Use Uvicorn or more better Hypercorn

## Making things fast

ToDo:
+ Especially caching with marshalling.HashableClass
+ Note avoid using `__dict__` to keep things fast (listen to talk)

https://www.youtube.com/watch?v=xKk7IXm0XO0
* Adaptive specializing interpreter (PEP 659)
* Consecutively allocated execution frames
* Zero cost try-except
* More regular object layout
* Lazily created object dictionaries.

https://www.youtube.com/watch?v=6P68IBou_cg
* The fastest way of removing duplicates from a list
* How much faster your code is when you reuse the built-in functions instead of trying to reinvent the wheel
* What is faster than the “for loop”
* If the lookup is faster in a list or a set
* When it’s better to beg for forgiveness than to ask for permission

https://www.youtube.com/watch?v=9OOJcTp8dqE
+ Multi-threaded python without GIL

## conda env

create or delete environment

```bat
conda remove --name toolcraft --all
conda create --name toolcraft python=3.10
```

## Poetry installation

Note that poetry needs to be installed in isolated environment. So refrain from `pip install poetry`

https://python-poetry.org/docs/master/#installation
https://python-poetry.org/docs/1.2/

```bat
activate base
conda update --all
conda install python=3.10

curl -sSL https://install.python-poetry.org | python - --uninstall
curl -sSL https://install.python-poetry.org | python - --version 1.2.0
poetry --version

```

Go to your repo i.e. toolcraft and update packages with poetry

```bat
activate toolcraft
poetry update
```

Also do some more things docs and pytest to work
Rest all dependencies will be taken care on cloud

```bat
poetry install --with dev --with test --with docs --with pre-commit --with build --no-root
```

## Pre-commit (use in future if needed) -- IGNORE
We will use this in future ...

This works only locally to do automated tests before commit ...
should be taken care by individuals

```bat
pre-commit install --install-hooks
```

## Poetry publish

With `tasks.py`

Note that there will be draft release on Github ...
Once you release there things will be uploaded to pypi
No need to do below stuffs as Github Actions ill handle it :)

```bat
git commit -m "update to next alpha"
git push
poetry run invoke bump --alpha
```

## In case you want to publish from local machine  -- IGNORE

Note that you need to store pypi creds in poetry config and then you can publish

```bat
poetry config --list
poetry config repositories.<repo_name> https://upload.pypi.org/legacy/
poetry config --list
poetry config http-basic.<repo_name> __token__ <pypi-token>
poetry publish -r <repo_name>
poetry cache clear -all .
poetry update
```

## EXTRAS

### Getting started with ppw

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

### Unittests

#### hypothesis
Maybe look hypothesis .... it is modern ...
The author has added feature add_node in python 3.11 for exceptions
Also look it has specialized numpy pandas and pyarrow api
https://hypothesis.readthedocs.io/en/latest/numpy.html#array-api

### Documentations

#### Docusauraus
Docusauraus will be great
Discussion to get sphinx inside it are going on
https://github.com/${organizationName}/${projectName}/issues/1059

#### mkdocs
https://www.mkdocs.org
Not sure but thsi soes not have stuff for Docausaurus
#### pydoc=markdown
[pydoc-markdown](https://niklasrosenstein.github.io/pydoc-markdown/api/pydoc_markdown/renderers/docusaurus/) has docausaurus renderer

but I assume this one is completely different as it does not use sphinx instead has its own markdowm

### Badges

+ You can generate badges and display status
  + https://shields.io/category/coverage

+ Add badges for social networking too ...

### LOGO Icons Images

+ https://fontmeme.com/minecraft-font

### Gen inspirations for different files from

[pyproject.toml](https://github.com/python-poetry/poetry-core/blob/master/pyproject.toml)

[.pre-commit-config.yaml](https://github.com/python-poetry/poetry-core/blob/master/.pre-commit-config.yaml)

[workflows](https://github.com/python-poetry/poetry-core/tree/master/.github/workflows)


### CLI for toolcraft using `cleo`

+ tasks
  + Note the `tasks.py` is for toolcraft management may be not needed.
  + May be, avoid imperative programming for library management.


+ tools
  + we will continue using `typer` instead of `cleo`
  + But anyways get inspiration from poetry library
    + https://github.com/python-poetry/poetry/tree/master/poetry/console/commands

### Understand `tox` and `tox-gh-actions`

Refer
+ https://github.com/ymyzk/tox-gh-actions


### Security (check dependencies and check python code)

Three options for dependencies:
+ snyk
+ pyup
+ dependabot from github security
  + https://github.com/SpikingNeurons/toolcraft/security

For code analysis
+ code-ql (from github)

Github has a lab for it ... use tools from them maybe (https://securitylab.github.com/)

Currently pyup it expects requirements file ... need to see how and when they will support poetry based files

Snyk seems to support poetry but the badge link does not work ... need to see that

#### Add workflow for security

Make sure that before release the vulnerabilities are addressed in workflow
Either use
+ github dependabot
+ snyk
+ or something else

### Add to conda-forge
Example repo https://github.com/pytest-dev/pytest


### Pre-commit

Currently, we let pre-commit serves handle it
But if it fails our workflows will not know that
So we can make our own `pre-commit` workflow ... this also make it dependent on release tags

### Coverage

There are two options
+ codecov
+ coveralls

We are using codecov
But looks like both do not have release-tag specific badges
We need to just have badge on main branch and disable it for release

Note that codecov report can be specialized for branch but same is not known for tags

You can see branches here
https://app.codecov.io/gh/SpikingNeurons/toolcraft/branches?page=1&order=-updatestamp


### Release tag specific readme badge

We might need to have badges specific to release tage
And the badges that cannot be release-tag specific must be removed from readme...


### Having workflows as dependency

https://github.com/KarmaComputing/Github-Trigger-workflow-from-another-workflow/tree/main/.github/workflows


### Netlify

We will use this as [facebook](https://github.com/${organizationName}/${projectName}/edit/main/README.md) uses it


#### Cloud functions

Netlify allows deploying cloud functions
We have set that to `website/functions` dir
[Netlify Functions](https://docs.netlify.com/functions/build-with-typescript/)
