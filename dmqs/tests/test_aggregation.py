from dmqs.aggregation import Avg

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
    pass

def test_aggregation_max():
    pass

def test_aggregation_count():
    pass

def test_aggregation_stdev():
    pass

def test_aggregation_variance():
    pass

def test_aggregation_sum():
    pass
