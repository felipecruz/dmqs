import os
import sys

sys.path.append('./dmqs/django_app/')
sys.path.append('./dmqs/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'mock_settings'

from dmqs.integration.memorify_django_model import *
from dmqs.integration.utils import fetch_primary_key

from django.test.utils import setup_test_environment, \
                              teardown_test_environment

from django_app.models import Friend, Dog, BestFriend, Friendship, Stranger
from django.contrib.auth.models import User, Group

from dmqs.manager import MemoryManager

import pytest

def test_get_primary_key():
    setup_test_environment()
    old_name = "django_app"

    from django.db import connection
    old_name = connection.creation.create_test_db(verbosity=1, autoclobber=True)

    stranger = Stranger(name="12")
    stranger.save()

    assert "12" == fetch_primary_key(stranger)

    connection.creation.destroy_test_db(old_name, 1)
    teardown_test_environment()

def test_memorify_foreign_key():
    '''
        The idea here is to create objects on the database, memorify
        single relations (ForeignKey and OneToOne) and then check if
        and check if the relation returns expected data from memory
    '''
    setup_test_environment()
    old_name = "django_app"

    from django.db import connection
    old_name = connection.creation.create_test_db(verbosity=1, autoclobber=True)

    from dmqs.repository import Repository
    repository = Repository()

    dog = Dog(name="Dogao")
    dog.save()

    repository.save(Dog.__name__, dog)

    friend = Friend(name="Name")
    friend.dog = dog
    friend.save()

    repository.save(Friend.__name__, friend)

    assert friend.dog == dog

    memorify_single_relations(friend)

    unpatch_info = patch_models("django_app")
    # the model is patched to make sure that Friend.objects.* comes from
    # memory and not from the database
    memory_person = Friend.objects.get(id=1)

    assert memory_person.dog == dog
    assert memory_person.dog.name == dog.name
    assert isinstance(Friend.objects, MemoryManager)

    connection.creation.destroy_test_db(old_name, 1)
    teardown_test_environment()

    # we must do that to not break other tests
    unpatch_models("django_app", unpatch_info)

def test_memorify_one_to_one_field():
    '''
        The idea here is to create objects on the database, memorify
        single relations (ForeignKey and OneToOne) and then check if
        and check if the relation returns expected data from memory
    '''
    setup_test_environment()
    old_name = "django_app"

    from django.db import connection
    old_name = connection.creation.create_test_db(verbosity=1, autoclobber=True)

    from dmqs.repository import Repository
    repository = Repository()

    other_dog = Dog(name="Dogao 2")
    other_dog.save()

    repository.save(Dog.__name__, other_dog)

    friend = Friend(name="Name")
    friend.other_dog = other_dog
    friend.save()

    repository.save(Friend.__name__, friend)

    assert friend.other_dog == other_dog

    memorify_single_relations(friend)

    unpatch_info = patch_models("django_app")
    # the model is patched to make sure that Friend.objects.* comes from
    # memory and not from the database

    memory_person = Friend.objects.get(id=1)

    assert memory_person.other_dog == other_dog
    assert memory_person.other_dog.name == other_dog.name
    assert isinstance(Friend.objects, MemoryManager)

    connection.creation.destroy_test_db(old_name, 1)
    teardown_test_environment()

    # we must do that to not break other tests
    unpatch_models("django_app", unpatch_info)

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

    Friend.objects.all().delete()
    BestFriend.objects.all().delete()
    Friendship.objects.all().delete()

    unpatch_info = patch_models("django_app")

    memorify_m2m(other_friend, other_friend.m2m_data)

    assert isinstance(other_friend.__dict__['friends'], MemoryManager)
    assert list(other_friend.__dict__['friends'].all()) == [friend]

    assert isinstance(other_friend.friends, MemoryManager)
    assert list(other_friend.friends.all()) == [friend]

    unpatch_models("django_app", unpatch_info)

    connection.creation.destroy_test_db(old_name, 1)
    teardown_test_environment()

def test_m2m_with_through():
    setup_test_environment()
    old_name = "django_app"

    from django.db import connection
    from datetime import date
    connection.creation.create_test_db(verbosity=1, autoclobber=True)

    from dmqs.repository import Repository
    repository = Repository()

    friend = Friend(name="Friend")
    friend.save()

    other_friend = Friend(name="Name")
    other_friend.save()

    other_friend2 = Friend(name="Name2")
    other_friend2.save()

    other_friend3 = Friend(name="Name3")
    other_friend3.save()

    best_friend = BestFriend()
    best_friend.person = other_friend
    best_friend.nickname = "nickname"
    best_friend.save()

    best_friend2 = BestFriend()
    best_friend2.person = other_friend2
    best_friend2.nickname = "nickname2"
    best_friend2.save()

    friendship = Friendship()
    friendship.since = date.today()
    friendship.best_friend1 = best_friend
    friendship.best_friend2 = friend
    friendship.save()

    friendship2 = Friendship()
    friendship2.since = date.today()
    friendship2.best_friend1 = best_friend2
    friendship2.best_friend2 = friend
    friendship2.save()

    friendship3 = Friendship()
    friendship3.since = date.today()
    friendship3.best_friend1 = best_friend2
    friendship3.best_friend2 = other_friend3
    friendship3.save()

    repository.save(Friend.__name__, other_friend)
    repository.save(Friend.__name__, other_friend2)
    repository.save(Friend.__name__, other_friend3)
    repository.save(Friend.__name__, friend)
    repository.save(BestFriend.__name__, best_friend)
    repository.save(BestFriend.__name__, best_friend2)
    repository.save(Friendship.__name__, friendship)
    repository.save(Friendship.__name__, friendship2)
    repository.save(Friendship.__name__, friendship3)

    Friend.objects.all().delete()
    BestFriend.objects.all().delete()
    Friendship.objects.all().delete()

    unpatch_info = patch_models("django_app")

    memorify_m2m(friend, {})
    memorify_m2m(other_friend3, {})

    assert isinstance(friend.__dict__['best_friends'], MemoryManager)
    assert list(friend.__dict__['best_friends'].all()) == [best_friend, best_friend2]
    assert list(friend.__dict__['best_friends'].filter(nickname__endswith="2")) == [best_friend2]

    assert isinstance(other_friend3.__dict__['best_friends'], MemoryManager)
    assert list(other_friend3.__dict__['best_friends'].all()) == [best_friend2]
    assert list(other_friend3.__dict__['best_friends'].filter(nickname__endswith="2")) == [best_friend2]

    assert isinstance(friend.best_friends, MemoryManager)
    assert list(friend.best_friends.all()) == [best_friend, best_friend2]
    assert list(friend.best_friends.filter(nickname__endswith="2")) == [best_friend2]

    assert isinstance(other_friend3.best_friends, MemoryManager)
    assert list(other_friend3.best_friends.all()) == [best_friend2]
    assert list(other_friend3.best_friends.filter(nickname__endswith="2")) == [best_friend2]

    unpatch_models("django_app", unpatch_info)

    connection.creation.destroy_test_db(old_name, 1)
    teardown_test_environment()

def test_memorify_single_relation_hidden_None():
    setup_test_environment()
    old_name = "django_app"

    from django.db import connection
    old_name = connection.creation.create_test_db(verbosity=1, autoclobber=True)

    user = User()
    user.username = "test user"
    user.save()

    group = Group()
    group.name = "test group"
    group.save()

    user.groups.add(group)
    user.save()

    memorify_m2m(user, {'groups': [1]})

    connection.creation.destroy_test_db(old_name, 1)
    teardown_test_environment()

def test_patch_and_unpatch_models():
    '''
        The idea here is to patch a model, call save and fetch from memory
        as you do with regular django models
    '''
    unpatch_info = patch_models("django_app")

    friend = Friend()
    friend.name = "Name"
    friend.save()

    assert isinstance(Friend.objects, MemoryManager)
    assert list(Friend.objects.all()) == [friend]

    unpatch_models("django_app", unpatch_info)
    assert not isinstance(Friend.objects, MemoryManager)
    assert not Friend.save == memory_save
