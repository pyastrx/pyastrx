=======================
Configure the YAML file
=======================

YAML demonstration file
-----------------------

Below is a YAML configuration file that can be used to configure the
command line interface and the code analysis.

.. code-block:: yaml

    after_context: 3
    before_context: 3
    folder: "tests"
    parallel: true
    rules:
        "//ClassDef[re:match('.*Var', @name)]":
            name: "B001"
            description: "Classes with 'Var' in name"
            severity: "warning"
            why: "bad practice"
            use_in_linter: true

Options
-------

after_context
~~~~~~~~~~~~~~

The number of lines of context to show after the line of the violation.

before_context
~~~~~~~~~~~~~~~

The number of lines of context to show before the line of the violation.

parallel
~~~~~~~~

If true, the analysis will be run in parallel.

folder
~~~~~~

The folder to be analyzed.

exclude
~~~~~~~

A list of folders to be excluded from the analysis.

output
~~~~~~

The output format.

- "human"
- "json"
- "pylint"

Rules for code quality
----------------------

.. code-block:: yaml

    rules:
        <XPATH_EXPRESSION (You can also use re:match or re:search)>:
            name: "SHORT_NAME"
            description: "DESCRIPTION"
            severity: "How severe the violation is"
            why: "Why this rule is important"
            ignore: A boolean value to indicate if the rule should be ignored


XPATH Expression
~~~~~~~~~~~~~~~~~~
    The name of the rule.

description
~~~~~~~~~~~
    A description of the rule.

severity
~~~~~~~~
    The severity of the rule.

why
~~~

use_in_linter
~~~~~~~~~~~~~
    A boolean value to indicate if the rule should be ignored.
