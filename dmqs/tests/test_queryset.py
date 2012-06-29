from dmqs.queryset import MemoryQuerySet

def type_and_instance(type_name,**kwargs):
    new_class = type(type_name, (object,), {})
    instance = new_class()
    instance.__dict__ = kwargs
    return instance

def test_query_all():
    person1 = type_and_instance('Person', name="Name 1", memory=True)
    person2 = type_and_instance('Person', name="Name 2", memory=True)

    data = [person1, person2]
    queryset = MemoryQuerySet(person1.__class__, data=data)

    assert len(queryset.all()) == 2

def test_query_filter():
    person1 = type_and_instance('Person',
                                name="Name 1",
                                nickname="Nickname 1",
                                memory=True)

    person2 = type_and_instance('Person',
                                name="Name 2",
                                nickname="Nickname 2",
                                memory=True)

    person3 = type_and_instance('Person',
                                name="Name 2",
                                nickname="Nickname 3",
                                memory=True)

    data = [person1, person2, person3]
    queryset = MemoryQuerySet(person1.__class__, data=data)

    assert len(queryset.filter(name="Name 1")) == 1
    assert len(queryset.filter(name="Name 2")) == 2
    assert len(queryset.filter(name="Name 2", nickname="Nickname 2")) == 1

def test_query_filter_other_conditions():
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

    data = [person1, person2, person3]
    queryset = MemoryQuerySet(person1.__class__, data=data)

    assert len(queryset.filter(name__contains="1")) == 1
    assert len(queryset.filter(name__in=["Name 2"])) == 2
    assert len(queryset.filter(name__icontains="Name",
                                age__gte=30)) == 2

    assert len(queryset.filter(name__icontains="Name",
                                nickname__startswith="Nick",
                                age__gte=30,
                                name__in=["Name 1"])) == 0

    assert len(queryset.filter(name__icontains="Name",
                                nickname__startswith="Nick",
                                age__gte=30,
                                name__in=["Name 2"])) == 2
