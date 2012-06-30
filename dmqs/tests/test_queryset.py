from dmqs.queryset import MemoryQuerySet
from dmqs.repository import Repository

def type_and_instance(type_name, **kwargs):
    _id = 'id'
    new_class = type(type_name, (object,), {
        '__eq__': lambda x, y: x.__dict__[_id] == y.__dict__[_id],
        '__ne__': lambda x, y: x.__dict__[_id] != y.__dict__[_id],
        '__lt__': lambda x, y: x.__dict__[_id] < y.__dict__[_id],
        '__gt__': lambda x, y: x.__dict__[_id] > y.__dict__[_id]
    })
    instance = new_class()
    instance.__dict__ = kwargs
    return instance

instance_id = 1

def type_and_instance_attr_eq(type_name, **kwargs):
    global instance_id
    attr = 'id'

    new_class = type(type_name, (object,),
    {
        '__eq__': lambda x, y: x.id == y.id,
        '__ne__': lambda x, y: x.id != y.id,
    })
    instance = new_class()
    instance.__dict__ = kwargs
    instance.__dict__['id'] = instance_id
    instance_id += 1
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
    assert set(queryset.filter(name="Name 1")) == set([person1])
    assert len(queryset.filter(name="Name 2")) == 2
    assert set(queryset.filter(name="Name 2")) == set([person2, person3])
    assert len(queryset.filter(name="Name 2", nickname="Nickname 2")) == 1
    assert set(queryset.filter(name="Name 2", nickname="Nickname 2")) == \
           set([person2])

def test_query_exclude():
    person1 = type_and_instance_attr_eq('Person',
                                name="Name 1",
                                nickname="Nickname 1",
                                memory=True)

    person2 = type_and_instance_attr_eq('Person',
                                name="Name 2",
                                nickname="Nickname 2",
                                memory=True)

    person3 = type_and_instance_attr_eq('Person',
                                name="Name 2",
                                nickname="Nickname 3",
                                memory=True)

    data = [person1, person2, person3]
    queryset = MemoryQuerySet(person1.__class__, data=data)

    assert len(queryset.exclude(name="Name 1")) == 2
    assert set(queryset.exclude(name="Name 1")) == set([person2, person3])
    assert len(queryset.exclude(name="Name 2")) == 1
    assert set(queryset.exclude(name="Name 2")) == set([person1])
    assert len(queryset.exclude(name="Name 2", nickname="Nickname 2")) == 2
    assert set(queryset.exclude(name="Name 2", nickname="Nickname 2")) == \
           set([person1, person3])

def test_query_simple_orderby():
    from datetime import date
    person1 = type_and_instance('Person',
                                name="Name 1",
                                nickname="Nickname 1",
                                birthday=date(2011, 6, 20),
                                age=99,
                                memory=True)

    person2 = type_and_instance('Person',
                                name="Name 2",
                                nickname="Nickname 2",
                                birthday=date(2011, 6, 22),
                                age=50,
                                memory=True)

    person3 = type_and_instance('Person',
                                name="Name 3",
                                nickname="Nickname 3",
                                birthday=date(2011, 4, 20),
                                age=80,
                                memory=True)

    person4 = type_and_instance('Person',
                                name="Name 4",
                                nickname="Nickname 4",
                                birthday=date(2010, 6, 20),
                                age=1,
                                memory=True)

    data = [person1, person2, person3, person4]
    queryset = MemoryQuerySet(person1.__class__, data=data)

    assert list(queryset.order_by('age')) == \
                                 [person4, person2, person3, person1]
    assert list(queryset.order_by('age', 'birthday')) == \
                                 [person4, person2, person3, person1]
    assert list(queryset.order_by('-age')) == \
                                 [person1, person3, person2, person4]
    assert list(queryset.order_by('-age', '-birthday')) == \
                                 [person1, person3, person2, person4]

def test_query_complex_orderby():
    from datetime import date
    person1 = type_and_instance('Person',
                                name="Name 1",
                                nickname="Nickname 1",
                                birthday=date(2011, 6, 20),
                                age=99,
                                memory=True)

    person2 = type_and_instance('Person',
                                name="Name 2",
                                nickname="Nickname 2",
                                birthday=date(2011, 6, 22),
                                age=50,
                                memory=True)

    person3 = type_and_instance('Person',
                                name="Name 3",
                                nickname="Nickname 3",
                                birthday=date(2011, 4, 20),
                                age=50,
                                memory=True)

    person4 = type_and_instance('Person',
                                name="Name 4",
                                nickname="Nickname 4",
                                birthday=date(2010, 6, 20),
                                age=1,
                                memory=True)

    data = [person1, person2, person3, person4]
    queryset = MemoryQuerySet(person1.__class__, data=data)


    assert list(queryset.order_by('age', 'birthday')) == \
                                 [person4, person3, person2, person1]

    assert list(queryset.order_by('age', '-birthday')) == \
                                 [person4, person2, person3, person1]

    assert list(queryset.order_by('-age', 'birthday')) == \
                                 [person1, person3, person2, person4]

    assert list(queryset.order_by('-age', '-birthday')) == \
                                 [person1, person2, person3, person4]

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

def test_query_update():
    from datetime import date
    person1 = type_and_instance('Person',
                                name="Name 1",
                                nickname="Nickname 1",
                                birthday=date(2011, 6, 20),
                                age=30,
                                memory=True)

    person2 = type_and_instance('Person',
                                name="Name 2",
                                nickname="Nickname 2",
                                birthday=date(2011, 6, 22),
                                age=57,
                                memory=True)

    person3 = type_and_instance('Person',
                                name="Name 3",
                                nickname="Nickname 3",
                                birthday=date(2011, 4, 20),
                                age=30,
                                memory=True)

    person4 = type_and_instance('Person',
                                name="Name 4",
                                nickname="Nickname 4",
                                birthday=date(2010, 6, 20),
                                age=30,
                                memory=True)

    data = [person1, person2, person3, person4]
    queryset = MemoryQuerySet(person1.__class__, data=data)

    assert queryset.filter(age=30).update(birthday=date(2011, 01, 04)) == 3
    assert person1.birthday == date(2011, 01, 04)
    assert person3.birthday == date(2011, 01, 04)
    assert person4.birthday == date(2011, 01, 04)

def test_query_delete():
    from datetime import date

    person1 = type_and_instance_attr_eq('Person',
                                name="Name 1",
                                nickname="Nickname 1",
                                birthday=date(2011, 6, 20),
                                age=30,
                                memory=True)

    person2 = type_and_instance_attr_eq('Person',
                                name="Name 2",
                                nickname="Nickname 2",
                                birthday=date(2011, 6, 22),
                                age=57,
                                memory=True)

    person3 = type_and_instance_attr_eq('Person',
                                name="Name 3",
                                nickname="Nickname 3",
                                birthday=date(2011, 4, 20),
                                age=30,
                                memory=True)

    person4 = type_and_instance_attr_eq('Person',
                                name="Name 4",
                                nickname="Nickname 4",
                                birthday=date(2010, 6, 20),
                                age=30,
                                memory=True)

    data = [person1, person2, person3, person4]

    queryset = MemoryQuerySet(person1.__class__, data=data)
    repository = Repository()
    repository.__dict__['Person'] = data

    queryset.filter(age__gte=10,birthday__lte=date(2011, 05, 05)).delete()
    assert len(queryset.all()) == 2
    assert queryset.all().count() == 2

    queryset = MemoryQuerySet(person1.__class__, data=data)
    assert len(queryset.all()) == 2
    assert queryset.all().count() == 2
