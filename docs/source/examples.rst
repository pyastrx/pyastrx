========
Examples
========


Default arguments
=================

Mutable default arguments
-------------------------

.. code:: yaml

    //defaults/*[self::Dict or self::List or self::Set or self::Call]:
        name: "mutable-defaults"
        description: "Can create bugs that are hard to find"
        severity: "error"
        why: "bad practice"


Global variables
================


Global definition
-----------------

.. code:: yaml

    //FunctionDef/body/Global:
        name: "Global keyword being used"
        description: "Creates side effects that are hard to track"
        severity: "info"
        use_in_liner: false
        why: ""


Unnecessary global keyword in function
--------------------------------------

.. code:: yaml

    //FunctionDef/body/Global/names[not(item=../../Assign/targets/Name/@id)]:
        name: "mutable-defaults"
        description: "Can create bugs that are hard to find"
        severity: "error"
        why: "bad practice"


Function definitions
====================

Recursion
---------

.. code:: yaml

    //FunctionDef[@name=body//Call/func/Name/@id and not(parent::node()/parent::ClassDef)]:
        name: "recursion"
        description: "Recursion pattern detected in this file"
        severity: "info"
        why: "should be refactored"


Recursion in a class method
---------------------------

.. code:: yaml

    //ClassDef/body/FunctionDef[@name=body//Call/func/Attribute[value/Name[@id='self']]/@attr]:
        name: "recursion-class-method"
        description: ""
        severity: "ino"


New variable with the same name as the current function
-------------------------------------------------------

.. code:: yaml

    //FunctionDef[@name=body/Assign/targets/Name/@id]:
        name: "redefinition-of-function-var"
        description: "You should not define a new variable with the same name as the current function"
        severity: "error"
        why: "bad practice"