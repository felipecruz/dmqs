from dmqs.queryset import MemoryQuerySet
from dmqs.manager import MemoryManager
from dmqs.foundation import memory_save
from functools import partial

from django.db.models.loading import get_app, get_models
from django.db.models import Model
from django.db.models.signals import post_init

_default_save = Model.save

def memorify_single_relations(object):
    for field in object._meta.fields:
        if not field.__class__.__name__ in ("ForeignKey", "OneToOneField"):
            continue
        id = fetch_relation_id(object, field.name)
        MemoryQuerySet.fetch_from_repo = True
        try:
            if id:
                setattr(object, field.name, MemoryManager(field.rel.to).get(id=id))
        except:
            raise Exception("Fuck! %s %s" % (field.name, str(id)))

def memorify_m2m(object, m2m_data):
    for field in object._meta.many_to_many:
        klass = field.rel.to
        if field.attname in m2m_data.keys() and field.rel.is_hidden():
            '''
                A 'simple' many to many relationship, has is_hidden == True
                because Django creates a 'hidden' class, from user point of view
                to handle the relationship

                class Friend(models.Model):
                    friends      = models.ManyToManyField('self', null=True)

                model.friends return a manager associated with Friend.

                This case is a little easier than through many to many rels because
                m2m data has already all IDs which this class is related, so
                if Friend.id == 1 is friend of Friend.id == 2 then:

                m2m_data = {'friends': [2]}

                which means, this model instance is friend of friend.id == 2
            '''
            ids = map(lambda x: int(x), m2m_data[field.attname])
            MemoryQuerySet.fetch_from_repo = True

            # change manager per model instance
            object.__dict__[field.name] = MemoryManager(klass, default_filters=dict(id__in=ids))

        elif not field.rel.is_hidden():
            '''
                A through relation)hip(is_hidden == False), is a many_to_many
                rel where data comes from a query in the through class.

                class Friendship(models.Model):
                    best_friend1 = models.ForeignKey('BestFriend',
                                                     related_name="reverse_friend")
                    best_friend2 = models.ForeignKey('Friend')
                    since        = models.DateField(null=False)

                class Friend(models.Model):
                    best_friends = models.ManyToManyField(BestFriend,
                                                          through=Friendship,
                                                          null=True,
                                                          related_name="friendship")

                model.best_friends return a manager associated with BestFriend

                It must return BestFriend's where exists Friendship between
                this model instance (object in the code) and them.

                The query on Friendship must filter Friendship's where
                best_friend2 is the model instance (object in the code).

                ie: Friendship.objects.filter(best_friend2=object.id
                                             ).values('best_friend1')

                through = Friendship
                filter_field_name = best_friend2
                data_field_name = best_friend1

            '''
            MemoryQuerySet.fetch_from_repo = True

            # find the through class
            through = field.rel.through

            # filter name
            filter_field_name = [_field.name for _field
                                             in through._meta.fields
                                             if _field.rel
                                             and _field.rel.to == field.model][0]

            data_field_name = [_field.name for _field
                                           in through._meta.fields
                                           if _field.rel
                                           and _field.rel.to == field.rel.to][0]
            lazy_filter = dict(_class=through,
                               _filter=object.id,
                               filter_field_name=filter_field_name,
                               data_field_name=data_field_name)

            object.__dict__[field.name] = MemoryManager(klass, lazy_filter=lazy_filter)

class ManyToManyMemoryDescriptor(object):
    def __init__(self, name):
        self.name = name

    def __get__(self, obj, type):
        return obj.__dict__[self.name]

    def __set__(self, obj, value):
        obj.__dict__[self.name] = value

def memorify_m2m_descriptors(klass):
    for field in klass._meta.many_to_many:
        setattr(klass, field.name, ManyToManyMemoryDescriptor(field.name))

def extract_m2m_descriptors(klass):
    descriptors = {}
    for field in klass._meta.many_to_many:
        descriptors[field.name] = klass.__dict__[field.name]
    return descriptors

def restore_m2m_descriptors(klass, descriptors):
    for field in klass._meta.many_to_many:
        setattr(klass, field.name, descriptors[field.name])

def fetch_relation_id(object, name):
    try:
        return getattr(object, '%s_id' % (name))
    except Exception:
        raise Exception("Unknow Field {0}".format(name))

def patch_models(app_name):
    unpatch_info = {}
    app = get_app(app_name)
    for model in get_models(app):
        unpatch_info[model] = dict(manager=model.objects,
                                   descriptors=extract_m2m_descriptors(model))
        memorify_m2m_descriptors(model)
        model.objects = MemoryManager(model)

    from django.db.models import Model
    Model.save = memory_save

    return unpatch_info

def funcToMethod(func, clas, method_name=None):
    '''
        code from: http://code.activestate.com/recipes/81732-dynamically-added-methods-to-a-class/#c1
    '''
    import new
    method = new.instancemethod(func,None,clas)
    if not method_name: method_name=func.__name__
    setattr(clas, method_name, method)

def unpatch_models(app_name, unpatch_info):
    from django.db.models import Model
    funcToMethod(_default_save, Model, method_name='save')

    app = get_app(app_name)
    for model in get_models(app):
        restore_m2m_descriptors(model, unpatch_info[model]['descriptors'])
        model.objects = unpatch_info[model]['manager']
