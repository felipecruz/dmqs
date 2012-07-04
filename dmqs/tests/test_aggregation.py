import pytest

from dmqs.aggregation import Avg, Max, Min, Sum, Var, Std, Count

def type_instance(type_name, prop, value):
    instance_type = type(type_name, (object,), {})
    instance = instance_type()
    instance.__dict__ = {prop: value}
    return instance

def test_aggregation_agv():
    model1 = type_instance('Student', 'grade', 9.0)
    model2 = type_instance('Student', 'grade', 8.0)
    model3 = type_instance('Student', 'grade', 2.0)
    model4 = type_instance('Student', 'grade', 3.0)
    model5 = type_instance('Student', 'grade', 7.0)
    model6 = type_instance('Student', 'grade', 1.0)

    models = [model1, model2, model3, model4, model5, model6]

    avg = Avg('grade')

    assert avg.return_value(models) == 5.0


def test_aggregation_min():
    model1 = type_instance('Student', 'grade', 9.0)
    model2 = type_instance('Student', 'grade', 8.0)
    model3 = type_instance('Student', 'grade', 2.0)
    model4 = type_instance('Student', 'grade', 3.0)
    model5 = type_instance('Student', 'grade', 7.0)
    model6 = type_instance('Student', 'grade', 1.0)

    models = [model1, model2, model3, model4, model5, model6]

    min = Min('grade')

    assert min.return_value(models) == 1.0

def test_aggregation_max():
    model1 = type_instance('Student', 'grade', 9.0)
    model2 = type_instance('Student', 'grade', 8.0)
    model3 = type_instance('Student', 'grade', 2.0)
    model4 = type_instance('Student', 'grade', 3.0)
    model5 = type_instance('Student', 'grade', 7.0)
    model6 = type_instance('Student', 'grade', 1.0)

    models = [model1, model2, model3, model4, model5, model6]

    max = Max('grade')

    assert max.return_value(models) == 9.0

def test_aggregation_count():
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

    assert count.return_value(data)[0].__dict__['accounts__count']== 3
    assert count.return_value(data)[1].__dict__['accounts__count'] == 2

def test_aggregation_stdev():
    model1 = type_instance('Student', 'grade', 9.0)
    model2 = type_instance('Student', 'grade', 8.0)
    model3 = type_instance('Student', 'grade', 2.0)
    model4 = type_instance('Student', 'grade', 3.0)
    model5 = type_instance('Student', 'grade', 7.0)
    model6 = type_instance('Student', 'grade', 1.0)

    models = [model1, model2, model3, model4, model5, model6]

    std = Std('grade')

    with pytest.raises(NotImplementedError):
        assert std.return_value(models) == 3.1

def test_aggregation_variance():
    model1 = type_instance('Student', 'grade', 9.0)
    model2 = type_instance('Student', 'grade', 8.0)
    model3 = type_instance('Student', 'grade', 2.0)
    model4 = type_instance('Student', 'grade', 3.0)
    model5 = type_instance('Student', 'grade', 7.0)
    model6 = type_instance('Student', 'grade', 1.0)

    models = [model1, model2, model3, model4, model5, model6]

    var = Var('grade')

    with pytest.raises(NotImplementedError):
        assert var.return_value(models) == 3.1

def test_aggregation_sum():
    model1 = type_instance('Student', 'grade', 9.0)
    model2 = type_instance('Student', 'grade', 8.0)
    model3 = type_instance('Student', 'grade', 2.0)
    model4 = type_instance('Student', 'grade', 3.0)
    model5 = type_instance('Student', 'grade', 7.0)
    model6 = type_instance('Student', 'grade', 1.0)

    models = [model1, model2, model3, model4, model5, model6]

    sum = Sum('grade')

    assert sum.return_value(models) == 30.0
