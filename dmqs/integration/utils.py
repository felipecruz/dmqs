def fetch_primary_key(model_instance):
    try:
        return getattr(model_instance, 'id')
    except:
        for field in model_instance._meta.fields:
            if field.primary_key:
                return getattr(model_instance, field.name)
