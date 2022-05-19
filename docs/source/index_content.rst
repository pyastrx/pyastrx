
================
What is PyASTrX?
================


Philosophy
==========

.. raw:: html

    <h1 style="text-align:center;">
    <em>
        "Simple projects are all alike; each complex project
        is complex in its own way."
    </em>
    -
    <strong>
        PyASTrX philosophy
    </strong>
    </h1>


The PyASTrX philosophy is to provide a simple, easy to use,
and extensible framework for code quality analysis, refactoring and
code base analysis.

The main point that I've developed this is because sometimes a necessary
practice in one project can be a bad practice in another project. In other
words, we should  **walk a mile in someone's shoes** before judging
the code quality of someone else's code.

PyASTrX allows you to define new code analysis patterns using just XPATH
expressions. No need to write a parser, creating a python file and shipping
to use in flake8 or pylint!


Features
========

PyASTrX provides the following features:

An easy customizable code quality analysis tool.
------------------------------------------------

Type :code:`pyastrx -h` to see the all the options.

You can also use a :code:`.pyastrx.yaml` file to configure the tool.
See the following page for more details :doc:`the_yaml`.


Human friendly outputs
----------------------

If your code base or pull request is huge, looking for
possible mistakes, bad practices or code smeels can be a pain,
so PyASTrX provides a human friendly output as default.

.. image:: _static/imgs/human_outputs.png
    :alt: Human friendly outputs
    :scale: 80%
    :align: center


Human friendly interface
------------------------

- autocomplete the previous queries
- combo box to select the files
- colorized syntax highlighting

.. image:: _static/imgs/human_outputs.png
    :alt: Human friendly outputs
    :scale: 80%
    :align: center

An interactive interface to explore the AST and XML
---------------------------------------------------

Using the :code: `-i` arg or adding a :code: `interactive: true` in your
`.pyastrx.yaml` you can explore the AST and XML parsed AST of your code.
This can be useful to understand your code base and helps you to write
you custom XPATH queries to be used in your project.