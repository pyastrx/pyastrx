========
Examples
========


Defaults arguments
==================

Mutable defaults arguments
--------------------------

.. code:: yaml

    "//defaults/*[self::Dict or self::List or self::Set or self::Caller]":
        name: "mutable-defaults"
        description: "Can create bugs that are hard to find"
        severity: "error"
        why: "bad practice"


Global variables
================


Global definition
-----------------

.. code:: yaml

    "//defaults/body/Global":
        name: "mutable-defaults"
        description: "Can create bugs that are hard to find"
        severity: "error"
        why: "bad practice"


Unnecessary global keyword in function
--------------------------------------

.. code:: yaml

    "//FunctionDef/body/Global/names[not(item=../../Assign/targets/Name/@id)]":
        name: "mutable-defaults"
        description: "Can create bugs that are hard to find"
        severity: "error"
        why: "bad practice"
