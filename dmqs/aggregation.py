from operator import attrgetter

class Avg(object):
    def __init__(self, property_name):
        self.property_name = property_name

    def return_value(self, data):
        return float(sum([d.__dict__[self.property_name] for d in data])/len(data))
