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
