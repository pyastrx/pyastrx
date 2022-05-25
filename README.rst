
================
What is PyASTrX?
================


Philosophy
==========


"Simple projects are all alike; each complex project is complex in its own way."
--------------------------------------------------------------------------------

(adapted from Tolstoy's Anna Karenina)


The PyASTrX philosophy is to provide a simple, easy-to-use, and
extensible framework for code quality analysis, refactoring and codebase analysis.

The main point that I've developed is that sometimes a necessary practice in one project can be a bad practice in another
project. In other words, we should **walk a **mile in **someone's** shoes** before judging the code quality of someone else code.

PyASTrX allows you to define new code analysis patterns using just XPATH
expressions. No need to write a parser, create a python file and ship to use in flake8 or pylint!


.. code-block:: bash

    pip install pyastrx


========
Features
========

PyASTrX provides the following features:

An easy customizable code quality analysis tool.
================================================

Type :code:`pyastrx -h` to see all the options.

You can also use a :code:`pyastrx.yaml` file to configure the tool.


Human-friendly
==============

Search and Linter outputs
-------------------------

If your codebase or pull request is huge, looking for possible
mistakes, bad practices or code smells can be a pain, so PyASTrX
provides a human-friendly output as default.

.. image:: _static/imgs/human_outputs.png
    :alt: Human-friendly outputs
    :align: center


Friendly interface
------------------

- autocomplete the previous queries
- combo box to select the files
- colorized syntax highlighting

.. image:: _static/imgs/interface.png
    :alt: Human friendly outputs
    :align: center

pre-commit
==========


Copy the `main.py` available at `pyastrx/.pre-commit-hook`_
in your folder and add the following entry in your `.pre-commit-config.yaml`.

.. _pyastrx/.pre-commit-hook: https://github.com/devmessias/pyastrx/blob/main/.pre-commit-hook/main.py

.. code-block:: yaml

    - repo: local
        hooks:
        - id: pyastrx
            name: PyASTrX linter
            entry: ./<LOCATION>/main.py
            language: script
            args: ["-q"]
            types: ["python"]
            description: Check for any violations using the pyastrx.yaml config


Later on, I will ship this to be used in the pre-commit channels.

VsCode extension
================


Soon, I will ship a VS Code extension.


Explore the AST and XML
=======================

Using the :code: `-i` arg or adding a :code: `interactive: true` in your
`pyastrx.yaml` you can explore the AST and XML parsed AST of your code.
This can be useful to understand your code base and helps you to write
you custom XPATH queries to be used in your project.


Folder exploration
------------------

**Start the interactive interface**

.. code:: console

    $ pyastrx -i -d path_to_folder (or just save that in yaml)

**Press f and choose a file**

.. image:: _static/imgs/ast_explorer2.png
    :alt: Interactive interface
    :align: center
    :width: 45%

**Choose the ast (t), xml (x) or code exploration (o)**

.. image:: _static/imgs/ast_explorer3.png
    :alt: Interactive interface
    :align: center
    :width: 45%

**Learn!**

.. image:: _static/imgs/ast_explorer4.png
    :alt: Interactive interface
    :align: center
    :width: 45%

.. image:: _static/imgs/ast_explorer5.png
    :alt: Interactive interface
    :align: center
    :width: 45%

File exploration (one key-press distance)
-----------------------------------------


**Open the interactive with the python file**

.. code:: console

    $ pyastrx -i -f path_to_file (or just save that in yaml)


**Choose the ast (t), xml (x) or code exploration (o)**

==========================
On the shoulders of giants
==========================


This project is possible only because of the work of several
developers across the following projects:


lxml
=====

One of the greatest Python libraries, downloaded over millions of time.
Please, consider doing a donation to the `lxml <https://lxml.de/>`_ developers.


astpath
=======

The PyASTrX started with the idea of using the astpath as a dependency, but I've
decided to rewrite and redesign it to improve the maintainability and the
usability features of PyASTrX. `astpath`_ is a great and simple tool
developed by `H. Chase Stevens`_.

.. _astpath: https://github.com/hchasestevens/astpath
.. _H. Chase Stevens: http://www.chasestevens.com/


GAST
====

`GAST`_ it's a remarkable tool developed by `Serge Sans Paille`_.
GAST allows you to use the same XPATH expressions to analyze different
code bases written in different python versions.


.. _Serge Sans Paille: http://serge.liyun.free.fr/serge/
.. _GAST: https://github.com/serge-sans-paille/gast



prompt_toolkit
==============

A project created by `Jonathan Slenders`_ that
 provides a powerful and reliable way to construct command-line interfaces.

This project has a lot of features, good documentation and the maintainers keep
it well updated.

.. _Jonathan Slenders: https://github.com/jonathanslenders
.. _prompt_toolkit: https://github.com/prompt-toolkit/


