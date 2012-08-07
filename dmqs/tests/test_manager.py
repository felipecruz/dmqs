from dmqs.manager import MemoryManager
from dmqs.repository import Repository

repository = Repository()

def type_and_instance(type_name, **kwargs):
    dummy_class = type(type_name, (object,), {})
    new_class = type(type_name,
                     (object,),
                     dict(id=lambda s: s.__dict__['id'],
                          objects=MemoryManager(dummy_class)))
    instance = new_class()
    instance.__dict__ = kwargs
    return instance

def test_memory_manager_all():
    person1 = type_and_instance('Person',
                                name="Name 1",
                                nickname="Nickname 1",
                                age=20,
                                memory=True)

    person2 = type_and_instance('Person',
                                name="Name 2",
                                nickname="Nickname 2",
                                age=30,
                                memory=True)

    person3 = type_and_instance('Person',
                                name="Name 2",
                                nickname="Nickname 3",
                                age=40,
                                memory=True)

    persons = [person1, person2, person3]
    for person in persons:
        repository.save(person.__class__.__name__, person)

    Person = person1.__class__

    assert len(Person.objects.all()) == 3
    assert len(Person.objects.all().all()) == 3
    assert len(Person.objects.filter(name__contains="me").all()) == 3

def test_memory_manager_filter():
    repository.clean()
    person1 = type_and_instance('Person',
                                name="Name 1",
                                nickname="Nickname 1",
                                age=20,
                                memory=True)

    person2 = type_and_instance('Person',
                                name="Name 2",
                                nickname="Nickname 2",
                                age=30,
                                memory=True)

    person3 = type_and_instance('Person',
                                name="Name 2",
                                nickname="Nickname 3",
                                age=40,
                                memory=True)

    persons = [person1, person2, person3]
    for person in persons:
        repository.save(person.__class__.__name__, person)

    Person = person1.__class__

    assert len(Person.objects.filter(name__contains="me")) == 3
    assert len(Person.objects.filter(name__contains="me")
                             .filter(nickname__endswith="3")) == 1
