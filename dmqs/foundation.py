import re
from functools import partial

from repository import Repository

repository = Repository()

def memory_save(self, *args, **kwargs):
    repository.save(self.__class__.__name__, self)

def eq_condition(model_instance, prop, arg1):
    if arg1 == None:
        return isnull_condition(model_instance, prop)
    return model_instance.__dict__[prop] == arg1

def iexact_condition(model_instance, prop, arg1):
    return model_instance.__dict__[prop].upper() == arg1.upper()

def contains_condition(model_instance, prop, arg1):
    return model_instance.__dict__[prop].find(arg1) >= 0

def icontains_condition(model_instance, prop, arg1):
    return model_instance.__dict__[prop].upper().find(arg1.upper()) >= 0

def startswith_condition(model_instance, prop, arg1):
    return model_instance.__dict__[prop].startswith(arg1)

def istartswith_condition(model_instance, prop, arg1):
    return model_instance.__dict__[prop].upper().startswith(arg1.upper())

def endswith_condition(model_instance, prop, arg1):
    return model_instance.__dict__[prop].endswith(arg1)

def iendswith_condition(model_instance, prop, arg1):
    return model_instance.__dict__[prop].upper().endswith(arg1.upper())

def lt_condition(model_instance, prop, arg1):
    return model_instance.__dict__[prop] < arg1

def gt_condition(model_instance, prop, arg1):
    return model_instance.__dict__[prop] > arg1

def lte_condition(model_instance, prop, arg1):
    return model_instance.__dict__[prop] <= arg1

def gte_condition(model_instance, prop, arg1):
    return model_instance.__dict__[prop] >= arg1

def isnull_condition(model_instance, prop):
    cond = False
    try:
        cond = model_instance.__dict__[prop] == None
    except KeyError:
        return True
    return cond

def in_condition(model_instance, prop, arg1):
    return model_instance.__dict__[prop] in arg1

def range_condition(model_instance, prop, arg1, arg2):
    return model_instance.__dict__[prop] >= arg1 and \
           model_instance.__dict__[prop] <= arg2

def year_condition(model_instance, prop, arg1):
    return model_instance.__dict__[prop].year == arg1

def month_condition(model_instance, prop, arg1):
    return model_instance.__dict__[prop].month == arg1

def day_condition(model_instance, prop, arg1):
    return model_instance.__dict__[prop].day == arg1

def weekday_condition(model_instance, prop, arg1):
    return model_instance.__dict__[prop].isoweekday() == arg1

def regex_condition(model_instance, prop, arg1):
    return re.match(arg1, model_instance.__dict__[prop]) != None

def iregex_condition(model_instance, prop, arg1):
    return re.match(arg1, model_instance.__dict__[prop],
                    re.IGNORECASE) != None

def evaluate_condition(obj, value):
    elements = value.split('__')
    if elements == [value]:
        return partial(eq_condition, obj, value)
    elif elements[1] == "exact":
        return partial(eq_condition, obj, elements[0])
    elif elements[1] == "iexact":
        return partial(iexact_condition, obj, elements[0])
    elif elements[1] == "contains":
        return partial(contains_condition, obj, elements[0])
    elif elements[1] == "icontains":
        return partial(icontains_condition, obj, elements[0])
    elif elements[1] == "startswith":
        return partial(startswith_condition, obj, elements[0])
    elif elements[1] == "istartswith":
        return partial(istartswith_condition, obj, elements[0])
    elif elements[1] == "endswith":
        return partial(endswith_condition, obj, elements[0])
    elif elements[1] == "iendswith":
        return partial(iendswith_condition, obj, elements[0])
    elif elements[1] == "lt":
        return partial(lt_condition, obj, elements[0])
    elif elements[1] == "gt":
        return partial(gt_condition, obj, elements[0])
    elif elements[1] == "lte":
        return partial(lte_condition, obj, elements[0])
    elif elements[1] == "gte":
        return partial(gte_condition, obj, elements[0])
    elif elements[1] == "isnull":
        return partial(isnull_condition, obj, elements[0])()
    elif elements[1] == "in":
        return partial(in_condition, obj, elements[0])
    elif elements[1] == "range":
        return partial(range_condition, obj, elements[0])
    elif elements[1] == "year":
        return partial(year_condition, obj, elements[0])
    elif elements[1] == "day":
        return partial(day_condition, obj, elements[0])
    elif elements[1] == "month":
        return partial(month_condition, obj, elements[0])
    elif elements[1] == "weekday":
        return partial(weekday_condition, obj, elements[0])
    elif elements[1] == "regex":
        return partial(regex_condition, obj, elements[0])
    elif elements[1] == "iregex":
        return partial(iregex_condition, obj, elements[0])
    else:
        return evaluate_condition(getattr(obj,elements[0]),
                                  value[len(elements[0])+2:])
