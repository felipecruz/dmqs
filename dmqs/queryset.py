import copy

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from operator import attrgetter

from foundation import evaluate_condition, find_groups, mixed_sort
from repository import Repository

repository = Repository()

class MemoryQuerySet(object):
    fetch_from_repo = False

    '''
        This quertset fecthes objects from memory. It will emulate all
        public QuerySet methods to be fully django compatible
    '''

    def __init__(self, model, data=[], current=0):
        self.model = model
        self.model_name = model.__name__
        self.data = data
        self.current = current

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return self

    def next(self):
        if self.current >= len(self.data):
            raise StopIteration
        else:
            self.current += 1
            return self.data[self.current - 1]

    def _data_qs(self, data):
        return MemoryQuerySet(self.model, data=data)

    def aggregate(self, *args, **kwargs):
        pass

    def count(self):
        if not self._safe_data:
            return 0

        return len(self._safe_data)

    def get(self, *args, **kwargs):
        data = []
        if 'pk' in kwargs:
            kwargs['id'] = kwargs.pop('pk')

        for model in self.data:
            if all([evaluate_condition(model, k)(kwargs[k])
                    for k, v in kwargs.items()]):
                data.append(model)

        if len(data) > 1:
            raise MultipleObjectsReturned()

        if len(data) == 0:
            raise ObjectDoesNotExist()

        return data[0]

    def create(self, **kwargs):
        pass

    def bulk_create(self, objs):
        pass

    def get_or_create(self, **kwargs):
        pass

    def latest(self, field_name=None):
        pass

    def in_bulk(self, id_list):
        pass

    def delete(self):
        repository.delete(self.model_name, self.data)
        self.data = repository.get_models(self.model_name)
        MemoryQuerySet.fetch_from_repo = True

    def update(self, **kwargs):
        for model in self._safe_data:
            model.__dict__.update(kwargs)
        return len(self._safe_data)

    def exists(self):
        pass

    def order_by(self, *args):
        data = copy.copy(self._safe_data)
        properties = list(copy.copy(args))
        reverses = []

        for i, arg in enumerate(args):
            if arg.startswith('-'):
                properties[i] = arg[1:]
                reverses.append(True)
            else:
                reverses.append(False)
                properties[i] = arg

        # all false (age, birthday)
        if not any(reverses):
            data = sorted(data, key=attrgetter(*properties))
        # all True (-age, -birthday)
        elif all(reverses):
            data = sorted(data, key=attrgetter(*properties), reverse=True)
        # mixed behaviour (age, -birthday)
        else:
            data = mixed_sort(data, properties, reverses)
        return self._data_qs(data)

    def select_related(self, *args):
        # references are alredy in memory
        return self.all()

    def all(self):
        if self.data:
            return self._data_qs(self._safe_data)

        return self._data_qs([])

    def filter(self, **kwargs):
        data = []
        for model in self._safe_data:
            if all([evaluate_condition(model, k)(kwargs[k])
                    for k, v in kwargs.items()]):
                data.append(model)

        return self._data_qs(data)

    def exclude(self, **kwargs):
        data = copy.copy(self.data)
        for model in self._safe_data:
            if all([evaluate_condition(model, k)(kwargs[k])
                    for k, v in kwargs.items()]):
                data.remove(model)

        return self._data_qs(data)

    @property
    def _safe_data(self):
        if self.fetch_from_repo:
            return repository.get_models(self.model_name)
        return self.data
