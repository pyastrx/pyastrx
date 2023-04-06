

YAML demonstration file
-----------------------

Below is a YAML configuration file that can be used to configure the
command line interface and the code analysis.

.. code-block:: yaml

        after_context: 3
        before_context: 3
        interactive_files: true
        pagination: true
        quiet: false
        specifications:
            default:
                language: python
                folder: "."
                recursive: true
                exclude:
                - .venv
                - .tox
                - .pyastrx
                rules:
                    //defaults/*[self::Dict or self::List or self::Set or self::Call]:
                        description: Can create bugs that are hard to find
                        name: mutable-defaults
                        severity: error
                        why: bad practice
            dbt-yaml:
                language: yaml
                folder: "models"
                recursive: true
                rules:
                   quoting-database:
                        xpath:
                            |
                            //KeyNode[@name="quoting"]
                            /MappingNode
                            /KeyNode[@name="database"]
                            /*[
                                self::IntNode or self::StrNode or self::KeyNode
                            ]
                            severity: error
                            description: "Database quoting should be a boolean"

Options
-------

after_context
~~~~~~~~~~~~~~

The number of lines of context to show after the line match

before_context
~~~~~~~~~~~~~~~

The number of lines of context to show before the line match

interactive_files
~~~~~~~~~~~~~~~~~

Shows a selection interface listing the files that a match was found in.


pagination
~~~~~~~~~~

Uses `pydoc` and `less` to paginate the output.


parallel
~~~~~~~~

If true, the analysis will be run in parallel.

folder
~~~~~~

The folder to be analyzed.

exclude
~~~~~~~

A list of folders to be excluded from the analysis.

normalize_ast
~~~~~~~~~~~~~

This uses the great `gast project`_ to normalize the AST between different Python versions.

.. _gast project: https://github.com/serge-sans-paille/gast

Rules for code quality
----------------------

.. code-block:: yaml

    rules:
        <XPATH_EXPRESSION (You can also use re:match or re:search)>:
            name: ("", optional, recommended)
            description: ("", optional)
            severity: ("info", optional)
            why: ("", optional)
            use_in_linter: (true, optional)


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
