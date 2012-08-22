from dmqs.queryset import MemoryQuerySet
from dmqs.manager import MemoryManager
from dmqs.foundation import memory_save
from functools import partial

from django.db.models.loading import get_app, get_models
from django.db.models import Model
from django.db.models.signals import post_init

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
            ids = map(lambda x: int(x), m2m_data[field.attname])
            MemoryQuerySet.fetch_from_repo = True
            # help with this!
            # object.__dict__[field.name] = MemoryManager(klass, default_filters=dict(id__in=ids))
            setattr(object.__class__,
                    field.name,
                    MemoryManager(klass, default_filters=dict(id__in=ids)))
        elif not field.rel.is_hidden():
            #import pytest as pdb; pdb.set_trace()
            through = field.rel.through
            MemoryQuerySet.fetch_from_repo = True
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
            setattr(object.__class__,
                    field.name,
                    MemoryManager(klass, lazy_filter=lazy_filter))

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
