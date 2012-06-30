from collections import defaultdict

class Repository(object):
    __shared_state = defaultdict(list)
    def __init__(self):
        self.__dict__ = self.__shared_state

    def get_models(self, model_name):
        return self.__dict__[model_name]

    def get_names(self):
        return self.__dict__.keys()

    def clean(self):
        self.__dict__ = defaultdict(list)

    def save(self, model_name, value):
        update = False

        for i, model in enumerate(self.get_models(model_name)):
            if model.id == value.id:
                self.get_models(model_name)[i] = value
                update = True

        if not update:
            self.get_models(model_name).append(value)

        return update

    def delete(self, model_name, value):
        self.__dict__[model_name][:] = [x for x in self.__dict__[model_name]
                                        if x not in value]
