from dmqs.queryset import MemoryQuerySet
from dmqs.manager import MemoryManager
from dmqs.foundation import memory_save
from functools import partial

from django.db.models.loading import get_app, get_models
from django.db.models import Model
from django.db.models.signals import post_init

def memorify_single_relations(object):
    for field in object._meta.fields:
        if field.__class__.__name__ != "ForeignKey":
            continue
        id = fetch_relation_id(object, field.name)
        MemoryQuerySet.fetch_from_repo = True
        try:
            if id:
                setattr(object, field.name, MemoryManager(field.rel.to).get(id=id))
        except:
            raise Exception("Fuck! %s %s" % (field.name, str(id)))

def memorify_m2m(object, m2m_data):
    for k, v in m2m_data.items():
        for field in object._meta.many_to_many:
            #if not field.rel.through:
            klass = field.rel.to
            ids = map(lambda x: int(x), v)
            MemoryQuerySet.fetch_from_repo = True
            object.__dict__[field.name] = MemoryManager(klass, default_filters=dict(id__in=ids))

def fetch_relation_id(object, name):
    try:
        return getattr(object, '%s_id' % (name))
    except Exception:
        raise Exception("Unknow Field {0}".format(name))

def patch_models(app_name):
    unpatch_info = {}
    app = get_app(app_name)
    for model in get_models(app):
        unpatch_info[model] = model.objects
        model.objects = MemoryManager(model)

    from django.db.models import Model
    default_save = Model.save
    Model.save = memory_save

    return unpatch_info, default_save

def unpatch_models(app_name, unpatch_info, default_save):
    from django.db.models import Model
    Model.save = default_save

    app = get_app(app_name)
    for model in get_models(app):
        model.objects = unpatch_info[model]
