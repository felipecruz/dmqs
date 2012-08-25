DATABASES = {
    'default': {
        'NAME' : ':memory:',
        'ENGINE': 'django.db.backends.sqlite3',
        'SUPPORTS_TRANSACTIONS' : 'False'
    }
}

INSTALLED_APPS = ('django.contrib.auth',
                  'django.contrib.contenttypes',
                  'django_app',)
