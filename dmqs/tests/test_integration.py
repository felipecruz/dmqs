import os
import sys

sys.path.append('./dmqs/django_app/')
sys.path.append('./dmqs/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'mock_settings'

from dmqs.integration.memorify_django_model import *

from django.test.utils import setup_test_environment, \
                              teardown_test_environment

from django_app.models import Friend, Dog

from dmqs.manager import MemoryManager

import pytest

def test_memorify_foreign_key():
    setup_test_environment()
    old_name = "django_app"

    from django.db import connection
    old_name = connection.creation.create_test_db(verbosity=1, autoclobber=True)

    from dmqs.repository import Repository
    repository = Repository()

    dog = Dog(name="Dogao")
    dog.save()

    repository.save(Dog.__name__, dog)

    other_dog = Dog(name="Dogao 2")
    other_dog.save()

    repository.save(Dog.__name__, other_dog)

    person = Friend(name="Name")
    person.dog = dog
    person.other_dog = other_dog
    person.save()

    repository.save(Friend.__name__, person)

    assert person.dog == dog
    assert person.other_dog == other_dog

    memorify_single_relations(person)

    person.objects = MemoryManager(Friend)
    memory_person = Friend.objects.get(id=1)

    assert memory_person.dog == dog
    assert memory_person.other_dog == other_dog

    connection.creation.destroy_test_db(old_name, 1)
    teardown_test_environment()

def test_m2m():
    setup_test_environment()
    old_name = "django_app"

    from django.db import connection
    connection.creation.create_test_db(verbosity=1, autoclobber=True)

    from dmqs.repository import Repository
    repository = Repository()

    friend = Friend(name="Friend")
    friend.save()

    person = Friend(name="Name")
    person.save()

    person.friends.add(friend)
    person.save()

    repository.save(Friend.__name__, person)
    repository.save(Friend.__name__, friend)

    person.m2m_data = {'friends': [1]}

    memorify_m2m(person, person.m2m_data)

    assert isinstance(person.__dict__['friends'], MemoryManager)
    assert list(person.__dict__['friends'].all()) == [friend]
