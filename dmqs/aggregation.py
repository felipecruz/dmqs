from dmqs.foundation import get_attribute
from operator import attrgetter

class Avg(object):
    def __init__(self, property_name):
        self.property_name = property_name

    def return_value(self, data):
        return float(sum([get_attribute(d, self.property_name)
                          for d in data])/len(data))

class Max(object):
    def __init__(self, property_name):
        self.property_name = property_name

    def return_value(self, data):
        return max([get_attribute(d, self.property_name) for d in data])

class Min(object):
    def __init__(self, property_name):
        self.property_name = property_name

    def return_value(self, data):
        return min([get_attribute(d, self.property_name) for d in data])

class Sum(object):
    def __init__(self, property_name):
        self.property_name = property_name

    def return_value(self, data):
        return sum([get_attribute(d, self.property_name) for d in data])

class Std(object):
    def __init__(self, property_name):
        self.property_name = property_name

    def return_value(self, data):
        raise NotImplementedError()
'''
        from math import sqrt
        mean = float(sum([get_attribute(d, self.property_name)
                          for d in data])/len(data))
        std = 0
        std = reduce(lambda x, y: x + (y-mean)**2,
                     [get_attribute(d, self.property_name) for d in data])
        std = sqrt(std / float(len(data)-1))
        return std
'''

class Var(object):
    def __init__(self, property_name):
        self.property_name = property_name

    def return_value(self, data):
        raise NotImplementedError()

class Count(object):
    def __init__(self, property_name):
        self.property_name = property_name

    def return_value(self, data, aggregate_name=None):
        for d in data:
            if not aggregate_name:
                aggregate_name = "{0}__count".format(self.property_name)
            d.__dict__[aggregate_name] = \
                                    len(get_attribute(d, self.property_name))
        return data
