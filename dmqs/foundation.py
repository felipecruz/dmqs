import re
from functools import partial
from operator import attrgetter

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

def isnull_condition(model_instance, prop, arg1=None):
    cond = False
    try:
        cond = model_instance.__dict__[prop] == None
    except KeyError:
        cond = getattr(model_instance, prop) == None
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
        return partial(isnull_condition, obj, elements[0])
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


def get_attribute(value, property_name):
    elements = property_name.split("__")
    if elements == [property_name]:
        return value.__dict__[property_name]
    else:
        return get_attribute(value.__dict__[elements[0]],
                             '__'.join(elements[1:]))


def find_groups(data, attr=None):
    obj = None
    start = 0
    end = 0
    item = (start, end)
    ret = []

    for i, element in enumerate(data):
        if i >= len(data) - 1:
            ret.append((start, i))
            break
        if not attr and element != data[i + 1]:
            ret.append((start, end))
            start = i + 1
            end = end + 1
        elif attr and getattr(element, attr) != getattr(data[i + 1], attr):
            ret.append((start, end))
            start = i + 1
            end = end + 1
        else:
            end = i + 1
    return ret

def mixed_sort(data, properties, _reverses):
    reverses = list(reversed(_reverses))
    for i, prop in enumerate(list(reversed(properties))):
        data = sorted(data, key=attrgetter(prop), reverse=reverses[i])
    return data

def _mixed_sort(data, properties, reverses, index=0):
    from copy import copy
    return_data = copy(data)

    if index <= len(properties) -1:
        return_data = sorted(return_data,
                             key=attrgetter(properties[index]),
                             reverse=reverses[index])
        groups = find_groups(return_data, attr=properties[index])
        for subgroup in groups:
            if subgroup[0] == subgroup[1]:
                continue
            n = index + 1
            return_data[subgroup[0]: subgroup[1] + 1]  = \
                mixed_sort(data[subgroup[0]:
                                 subgroup[1] + 1],
                                 properties,
                                 reverses,
                                 index=n)
        return return_data
    else:
        if not type(data) == list:
            return [data]
        return data
