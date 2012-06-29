from datetime import date, datetime

from dmqs.foundation import evaluate_condition

def type_and_instance(type_name,**kwargs):
    new_class = type(type_name, (object,), {})
    instance = new_class()
    instance.__dict__ = kwargs
    return instance

def test_condition_equal():
    person = type_and_instance('Person',
                                name="Name",
                                nickname="Nickname",
                                age=20,
                                memory=True)

    assert evaluate_condition(person, "name")("Name") == True
    assert evaluate_condition(person, "name__exact")("Name") == True

def test_condition_iexact():
    person = type_and_instance('Person',
                                name="Name",
                                nickname="Nickname",
                                age=20,
                                memory=True)

    assert evaluate_condition(person, "name__iexact")("nAmE") == True
    assert evaluate_condition(person, "name__iexact")("name") == True

def test_condition_greater_than():
    person = type_and_instance('Person',
                                name="Name",
                                nickname="Nickname",
                                age=20,
                                memory=True)

    assert evaluate_condition(person, "age__gt")(10) == True

def test_condition_lesser_than():
    person = type_and_instance('Person',
                                name="Name",
                                nickname="Nickname",
                                age=20,
                                memory=True)

    assert evaluate_condition(person, "age__lt")(40) == True

def test_condition_greater_or_equal_than():
    from dmqs.foundation import evaluate_condition

    person = type_and_instance('Person',
                                name="Name",
                                nickname="Nickname",
                                age=20,
                                memory=True)

    assert evaluate_condition(person, "age__gte")(10) == True
    assert evaluate_condition(person, "age__gte")(20) == True

def test_condition_lesser_or_equal_than():
    person = type_and_instance('Person',
                                name="Name",
                                nickname="Nickname",
                                age=20,
                                memory=True)

    assert evaluate_condition(person, "age__lte")(40) == True
    assert evaluate_condition(person, "age__lte")(20) == True

def test_condition_isnull():
    person = type_and_instance('Person',
                                name="Name",
                                nickname=None,
                                age=20,
                                memory=True)

    assert evaluate_condition(person, "nickname__isnull") == True

def test_nested_condition_equal():
    person = type_and_instance('Person',
                                name="Name",
                                nickname=None,
                                age=20,
                                memory=True)

    dog = type_and_instance('Dog', owner=person, memory=True)

    assert evaluate_condition(dog, "owner__name")("Name") == True
    assert evaluate_condition(dog, "owner__name__iexact")("name") == True

def test_nested_condition_iexact():
    person = type_and_instance('Person',
                                name="Name",
                                nickname=None,
                                age=20,
                                memory=True)

    dog = type_and_instance('Dog', owner=person, memory=True)

    assert evaluate_condition(dog, "owner__name__iexact")("name") == True

def test_nested_condition_gt():
    person = type_and_instance('Person',
                                name="Name",
                                nickname=None,
                                age=20,
                                memory=True)

    dog = type_and_instance('Dog', owner=person, memory=True)

    assert evaluate_condition(dog, "owner__age__gt")(19) == True

def test_nested_condition_isnull():
    person = type_and_instance('Person',
                                name="Name",
                                nickname=None,
                                age=20,
                                memory=True)

    dog = type_and_instance('Dog', owner=person, memory=True)

    assert evaluate_condition(dog, "owner__nickname__isnull") == True

def test_condition_contains():
    person = type_and_instance('Person',
                                name="Name",
                                nickname="Nickname",
                                age=20,
                                memory=True)

    assert evaluate_condition(person, "name__contains")("ame") == True
    assert evaluate_condition(person, "name__contains")("Na") == True
    assert evaluate_condition(person, "name__contains")("na") == False

def test_condition_icontains():
    person = type_and_instance('Person',
                                name="Name",
                                nickname="Nickname",
                                age=20,
                                memory=True)

    assert evaluate_condition(person, "name__icontains")("ame") == True
    assert evaluate_condition(person, "name__icontains")("Na") == True

def test_condition_startswith():
    person = type_and_instance('Person',
                                name="Name",
                                nickname="Nickname",
                                age=20,
                                memory=True)

    assert evaluate_condition(person, "name__startswith")("Na") == True
    assert evaluate_condition(person, "name__startswith")("Nam") == True

def test_condition_istartswith():
    person = type_and_instance('Person',
                                name="Name",
                                nickname="Nickname",
                                age=20,
                                memory=True)

    assert evaluate_condition(person, "name__istartswith")("na") == True
    assert evaluate_condition(person, "name__istartswith")("nam") == True

def test_condition_endswith():
    person = type_and_instance('Person',
                                name="Name",
                                nickname="Nickname",
                                age=20,
                                memory=True)

    assert evaluate_condition(person, "name__endswith")("me") == True
    assert evaluate_condition(person, "name__endswith")("e") == True

def test_condition_iendswith():
    person = type_and_instance('Person',
                                name="NAME",
                                nickname="Nickname",
                                age=20,
                                memory=True)

    assert evaluate_condition(person, "name__iendswith")("me") == True
    assert evaluate_condition(person, "name__iendswith")("e") == True

def test_condition_in():
    person = type_and_instance('Person',
                            name="Name 1",
                            nickname="Nickname 1",
                            age=20,
                            memory=True)

    assert evaluate_condition(person, "name__in")(["Name 1", "Name 2"]) == True

def test_condition_range():
    person = type_and_instance('Person',
                            name="Name 1",
                            nickname="Nickname 1",
                            age=20,
                            memory=True)

    assert evaluate_condition(person, "age__range")(20, 30) == True
    assert evaluate_condition(person, "age__range")(10, 30) == True
    assert evaluate_condition(person, "age__range")(10, 20) == True
    assert evaluate_condition(person, "age__range")(21, 30) == False
    assert evaluate_condition(person, "age__range")(9, 19) == False

def test_condition_year():
    today = date.today()
    now = datetime.now()

    person = type_and_instance('Person',
                            name="Name 1",
                            nickname="Nickname 1",
                            age=20,
                            birthday=today,
                            appointment=now,
                            memory=True)

    assert evaluate_condition(person, "birthday__year")(today.year) == True

    assert evaluate_condition(person, "appointment__year")(today.year + 1) == False

    assert evaluate_condition(person, "birthday__year")(today.year + 1) == False

    assert evaluate_condition(person, "appointment__year")(today.year) == True


def test_condition_month():
    from datetime import date, datetime

    today = date.today()
    now = datetime.now()

    person = type_and_instance('Person',
                            name="Name 1",
                            nickname="Nickname 1",
                            age=20,
                            birthday=today,
                            appointment=now,
                            memory=True)

    assert evaluate_condition(person, "birthday__month")(today.month) == True

    assert evaluate_condition(person, "appointment__month")(today.month + 1) == False

    assert evaluate_condition(person, "birthday__month")(today.month + 1) == False

    assert evaluate_condition(person, "appointment__month")(today.month) == True

def test_condition_day():
    from datetime import date, datetime

    today = date.today()
    now = datetime.now()

    person = type_and_instance('Person',
                            name="Name 1",
                            nickname="Nickname 1",
                            age=20,
                            birthday=today,
                            appointment=now,
                            memory=True)

    assert evaluate_condition(person, "birthday__day")(today.day) == True

    assert evaluate_condition(person, "appointment__day")(today.day + 1) == False

    assert evaluate_condition(person, "birthday__day")(today.day + 1) == False

    assert evaluate_condition(person, "appointment__day")(today.day) == True

def test_condition_weekday():
    from datetime import date, datetime

    today = date.today()
    now = datetime.now()

    person = type_and_instance('Person',
                            name="Name 1",
                            nickname="Nickname 1",
                            age=20,
                            birthday=today,
                            appointment=now,
                            memory=True)

    assert evaluate_condition(person, "birthday__weekday")(today.isoweekday()) == True

    assert evaluate_condition(person, "appointment__weekday")(today.isoweekday() + 1) == False

    assert evaluate_condition(person, "birthday__weekday")(today.isoweekday() + 1) == False

    assert evaluate_condition(person, "appointment__weekday")(today.isoweekday()) == True

def test_condition_regex():
    person = type_and_instance('Person',
                            name="Name 1",
                            nickname="Nickname 1",
                            age=20,
                            memory=True)

    assert evaluate_condition(person, "name__regex")(r'.*am.*') == True

def test_condition_iregex():
    person = type_and_instance('Person',
                            name="Name 1",
                            nickname="Nickname 1",
                            age=20,
                            memory=True)

    assert evaluate_condition(person, "name__iregex")(r'.*Am.*') == True
