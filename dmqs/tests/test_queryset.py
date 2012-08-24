import pytest

from django.core.exceptions import MultipleObjectsReturned, \
                                    ObjectDoesNotExist

from dmqs.queryset import MemoryQuerySet
from dmqs.repository import Repository
from dmqs.aggregation import Max, Min, Sum, Avg, Count

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
    setattr(new_class, 'DoesNotExist', ObjectDoesNotExist)
    setattr(new_class, 'MultipleObjectsReturned', MultipleObjectsReturned)
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

def test_query_values():
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

    assert queryset.values() == [person1.__dict__,
                                 person2.__dict__,
                                 person3.__dict__]

    assert queryset.values("name") == [{'name': "Name 1"},
                                       {'name': "Name 2"},
                                       {'name': "Name 2"}]

def test_query_values_list():
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

    assert queryset.values_list() == [tuple(person1.__dict__.values()),
                                      tuple(person2.__dict__.values()),
                                      tuple(person3.__dict__.values())]

    assert queryset.values_list("name") == [("Name 1",),
                                            ("Name 2",),
                                            ("Name 2",)]

    assert list(queryset.values_list("name", flat=True)) == ["Name 1",
                                                             "Name 2",
                                                             "Name 2"]
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
    repository.__dict__['data']['Person'] = data

    queryset.filter(age__gte=10,birthday__lte=date(2011, 05, 05)).delete()
    assert len(queryset.all()) == 2
    assert queryset.all().count() == 2

    queryset = MemoryQuerySet(person1.__class__, data=data)
    assert len(queryset.all()) == 2
    assert queryset.all().count() == 2

def test_queryset_get():
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
                                nickname="Nickname 2",
                                birthday=date(2010, 6, 20),
                                age=30,
                                memory=True)

    data = [person1, person2, person3, person4]

    queryset = MemoryQuerySet(person1.__class__, data=data)
    MemoryQuerySet.fetch_from_repo = False

    assert queryset.get(name="Name 1") == person1
    assert queryset.get(name="Name 1").name == person1.name


    with pytest.raises(ObjectDoesNotExist):
        queryset.get(name="Nobody")

    with pytest.raises(MultipleObjectsReturned):
        queryset.get(nickname="Nickname 2")

def test_queryset_create():
    class Dummy(object):
        def __init__(self, **kwargs):
            self.__dict__ = kwargs

    queryset = MemoryQuerySet(Dummy, data=[])
    assert len(queryset.all()) == 0

    model = queryset.create(id=1, name="Name 1", age=20)
    assert isinstance(model, Dummy)
    assert len(queryset.all()) == 1
    assert queryset.get(age=20).name == "Name 1"

    model = queryset.create(id=2, name="Name 2", age=25)
    assert isinstance(model, Dummy)
    assert len(queryset.all()) == 2
    assert queryset.get(age=20).name == "Name 1"
    assert queryset.get(age=25).name == "Name 2"

    queryset2 = MemoryQuerySet(Dummy, data=[])
    MemoryQuerySet.fetch_from_repo = True
    assert len(queryset2.all()) == 2
    assert queryset2.get(age=20).name == "Name 1"
    assert queryset2.get(age=25).name == "Name 2"


def test_queryset_annotate():
    def type_and_instance(type_name, **kwargs):
        new_class = type(type_name, (object,), {})
        instance = new_class()
        instance.__dict__ = kwargs
        return instance

    account1 = type_and_instance('Account',
                                credit=300)
    account2 = type_and_instance('Account',
                                credit=200)
    account3 = type_and_instance('Account',
                                credit=100)

    accounts = [account1, account2, account3]

    account11 = type_and_instance('Account',
                                credit=300)
    account12 = type_and_instance('Account',
                                credit=200)

    accounts1 = [account11, account12]

    person = type_and_instance('Person',
                               name="Name 4",
                               nickname="Nickname 4",
                               accounts=accounts,
                               age=1,
                               memory=True)

    person1 = type_and_instance('Person',
                               name="Name 4",
                               nickname="Nickname 4",
                               accounts=accounts1,
                               age=1,
                               memory=True)

    count = Count('accounts')

    data = [person, person1]

    queryset = MemoryQuerySet(person.__class__, data=data)
    result = list(queryset.annotate(num_accounts=Count('accounts')))

    assert result[0].__dict__['num_accounts'] == 3
    assert result[1].__dict__['num_accounts'] == 2

def test_queryset_aggregate():
    def type_and_instance(type_name, **kwargs):
        new_class = type(type_name, (object,), {})
        instance = new_class()
        instance.__dict__ = kwargs
        return instance

    account1 = type_and_instance('Account',
                                credit=100)
    account2 = type_and_instance('Account',
                                credit=200)
    account3 = type_and_instance('Account',
                                credit=100)
    account4 = type_and_instance('Account',
                                credit=600)
    account5 = type_and_instance('Account',
                                credit=500)

    accounts = [account1, account2, account3, account4, account5]


    queryset = MemoryQuerySet(account1.__class__, data=accounts)

    assert queryset.aggregate(max_credit=Max('credit')) == \
           dict(max_credit=600)

    assert queryset.aggregate(max_credit=Max('credit'), min_credit=Min('credit')) == \
           dict(max_credit=600, min_credit=100)

    assert queryset.aggregate(min_credit=Min('credit')) == \
           dict(min_credit=100)

    assert queryset.aggregate(sum_credit=Sum('credit')) == \
           dict(sum_credit=1500)

    assert queryset.aggregate(avg_credit=Avg('credit')) == \
           dict(avg_credit=300)

    assert queryset.aggregate(avg_credit=Avg('credit'), sum_credit=Sum('credit')) == \
           dict(avg_credit=300, sum_credit=1500)
