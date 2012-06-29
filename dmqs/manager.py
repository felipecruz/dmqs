from django.db.models.manager import Manager

from queryset import MemoryQuerySet
from repository import Repository

repository = Repository()

class MemoryManager(Manager):
    def __init__(self, model):
        self.model_name = model.__name__
        self.model = model

    def get_query_set(self):
        """Returns a new QuerySet object.  Subclasses can override this method
        to easily customize the behavior of the Manager.
        """
        if self.model_name in repository.get_names():
            return MemoryQuerySet(self.model,
                                  data=repository.get_models(self.model_name))

        return MemoryQuerySet(self.model)

    def create(self, *args, **kwargs):
        return self.model(**kwargs)
