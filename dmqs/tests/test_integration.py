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

    friend = Friend(name="Name")
    friend.dog = dog
    friend.other_dog = other_dog
    friend.save()

    repository.save(Friend.__name__, friend)

    assert friend.dog == dog
    assert friend.other_dog == other_dog

    memorify_single_relations(friend)

    friend.objects = MemoryManager(Friend)
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

    other_friend = Friend(name="Name")
    other_friend.save()

    other_friend.friends.add(friend)
    other_friend.save()

    repository.save(Friend.__name__, other_friend)
    repository.save(Friend.__name__, friend)

    other_friend.m2m_data = {'friends': [1]}

    memorify_m2m(other_friend, other_friend.m2m_data)

    assert isinstance(other_friend.__dict__['friends'], MemoryManager)
    assert list(other_friend.__dict__['friends'].all()) == [friend]
