dmqs
====

The initial motivation is to speed up fixture loading in Django.

dmqs could be used for many testing and learning purposes.

Tests
-----

Install pytest:

`pip install pytest`

How I test:

`py.test --verbose .`

First Goal
----------

Calls to model_instance.save(), will be executed on a "in memory" Repository.

The Repository is known by MemoryManagers, which return MemoryQuerySet objects.

After a `person.save()` it will be possible to call `Person.objects.all()` without
hit the database. It'll be just a python list iteration.

When a fixture is loaded for the first time and repository data goes to memory, it will
be possible to pickle the Repository dictionary and every model inside of it. If the same
fixture is used again, we can unpickle the repository data and skip this **slow** 
(fludh db, deserialize fixture, save each model) proccess

This way, even with big fixtures used all over the test code, this process should speed up a lot.

Contact
-------

Felipe Cruz
felipecruz@loogica.net
