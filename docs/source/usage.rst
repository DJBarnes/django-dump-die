Usage
=====
General
^^^^^^^
The middleware is where most of this package's heavy lifting happens.

By having the middleware installed, you can run ``dump(<variable>)`` and/or
``dd(<variable>)`` anywhere you want, and it will run the dump logic.
No importing or extra logic is required.

Each ``dump(<variable>)`` command will add the object passed to dump to an
internal list that will be dumped either when a ``dd(<variable>)`` is used
or if the entirety of the request finishes.
You can have as many ``dump(<variable>)`` statements as you want leading up to
a ``dd(<variable>)``.

If you make a call to ``dd(<variable>)``, execution will immediately stop and
all dumped objects including the the one sent to dd will be output.

If you do not make a call to ``dd(<variable>)`` and only use
``dump(<variable>)`` statements, the request will continue processing until it
is time to return the response at which point it will replace the response with
the data that has been dumped thus far.



Example
^^^^^^^

.. code-block:: python

    # Sample classes for output.
    class EmptyClass:
        """Empty Class."""
        pass


    class SomeClass:
        """Some Class."""
        SAMPLE_CONST = 41

        def __init__(self, *args, **kwargs):
            self.my_number = 32
            self.my_string = 'A super cool string'
            self.works = True
            self.nothing = None
            self.bytes = bytes('My Bytes', 'utf-8')
            self.list_o_stuff = ['A', 'B', 'C']
            self.sample_set = {'A', 'B', 'C'}
            self.sample_tuple = ('A', 12, True)
            self.empty_class = EmptyClass()
            self.empty_class_dup = self.empty_class

        def do_work(self):
            """Do some work"""
            return True


    # Example Usage
    empty_class = EmptyClass()
    some_class = SomeClass()

    dump('Simple String')
    dump(empty_class)
    dd(some_class)

.. image:: img/dd_example.png

**Note:** that most editors will give a red error squiggle for the dd command.

This is intentional, and the command will still run. This is because this
command is meant to be used for debugging, and is not meant to stay long-term.
The red squiggle helps identify it as something that should be removed before
any actual commits.

Available Parameters
^^^^^^^^^^^^^^^^^^^^
Both the ``dd()`` and ``dump()`` functions take the same parameters, in the
same ordering:

index_range
***********

:Type: ``int, list, tuple``
:Default: ``None``

An index range to modify output values of parent entity (if iterable).
Allows changing the range of which direct-child indexes are fully examined.
Only affects the direct children of the outermost parent object. Can be useful
with large datasets, when only wanting to examine a specific range of values.

When an index range is passed, the end index of that range overrides the
``DJANGO_DD_MAX_ITERABLE_LENGTH`` value set in settings.

Value can be:

* A single index.
* A range of two values, to specify starting and ending index (defined such as
  in a list or tuple).

Example::

    # Single index
    dump(my_list, index_range=18)  # Will do from index 18 to 18 + DJANGO_DD_MAX_ITERABLE_LENGTH
    # Range index
    dd(my_list, index_range=(18, 37))  # Will do from index 18 to 37

deepcopy
********

:Type: ``bool``
:Default: ``False``

A boolean to specify if passed objects should be deep-copied before being
passed into dd/dump logic. If set to ``True``, then preserves exact state of
object at time of passing into dd/dump. Useful if you are dumping an object,
then making changes to that object, and then dumping it again.

Example::

    # Dump starting state
    dump(my_list, deepcopy=True)
    # Update list
    my_list[5] = 42
    # Dump updated state
    dd(my_list)
