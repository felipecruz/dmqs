from django.db.models.manager import Manager

from queryset import MemoryQuerySet
from repository import Repository

repository = Repository()

class MemoryManager(Manager):
    def __init__(self, model, default_filters=None):
        self.model_name = model.__name__
        self.model = model
        self.default_filters = default_filters

    def get_query_set(self):
        """Returns a new QuerySet object.  Subclasses can override this method
        to easily customize the behavior of the Manager.
        """
        if self.model_name in repository.get_names():
            if self.default_filters:
                return MemoryQuerySet(self.model,
                                      data=repository.\
                                              get_models(self.model_name)
                                     ).filter(**self.default_filters)
            else:
                return MemoryQuerySet(self.model,
                                  data=repository.get_models(self.model_name))

        return MemoryQuerySet(self.model)

    def create(self, *args, **kwargs):
        return self.model(**kwargs)

    def add(self, instance):
        repository.save(self.model_name, instance)

    def __len__(self):
        return len(self.get_query_set().data)
