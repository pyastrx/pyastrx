
CLI: Interactive mode
---------------------


Start the interactive mode in src folder
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    $ pyastrx -i -d src

For specific files
~~~~~~~~~~~~~~~~~~

.. code-block:: console

    $ pyastrx -i -f src/script_1.py

or

.. code-block:: console

    $ pyastrx -i -f src/script_1.py -f src/script_2.py


Using an inline expression
~~~~~~~~~~~~~~~~~~~~~~~~~~

Supose you want to look for all the defaults in your
code base, do the following:

.. code-block:: console

    $ pyastrx -i -expr //defaults

As a linter
-----------

The linter mode will run outside of the CLI
and also will ignore any rule in the `pyastrx.yaml`
file that has the `use_in_linter: false`  flag.

.. code-block:: console

    $ pyastrx -l


More options
------------

.. code-block:: console

    $ pyastrx --help
