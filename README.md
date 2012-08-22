dmqs
====

This is an in-memory backend implementation for the django models. With dmqs it's possible to load Models, patch them,
and a call to `model_instance.save()` will never hit the database. You can still perform `Model.objects.all()` and
the result will work like if django was running with sqlite in memory, but even faster.

The initial motivation is to speed up fixture loading in Django.

dmqs could be used for many testing and learning purposes, focusing on Testing.

[![Build Status](https://secure.travis-ci.org/felipecruz/dmqs.png)](http://travis-ci.org/felipecruz/dmqs)

Using
-----

Instead of TestCase use dmqs.integration.MemoryTestCase

```python
from dmqs.integration.testcase import MemoryTestCase

class FastTest(MemoryTestCase):
    fixtures = ['dmqs_app/tests/fixtures/fixture.json']

    def test_friend(self):
        friend = Friend.objects.get(id=1)
        self.assertTrue(friend != None)
```

Tests
-----

First time:

`pip install -r requirements.txt`

To actually run the tests:

`make test`

Coverage Report
---------------

First time:

`pip install -r coverage_requirements.txt`

And then:

`make coverage`

Satus
-----

In few weeks I expect to release a beta version. The integration with django test mechanism isn't ready yet.


Authors
-------

Felipe Cruz
felipecruz@loogica.net

Thiago Garcia
thiagogds14@gmail.com
