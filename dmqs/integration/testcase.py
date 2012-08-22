from __future__ import with_statement

'''
    This code is a modified code from the django project.

    Copyright (c) Django Software Foundation and individual contributors.
'''

import sys
import os
import gzip
import zipfile
from optparse import make_option
import traceback

from django.test import TestCase
from django.db import (transaction, connection, connections, DEFAULT_DB_ALIAS,
    reset_queries)

from django.conf import settings
from django.core import serializers
from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import (connections, router, transaction, DEFAULT_DB_ALIAS,
      IntegrityError, DatabaseError)
from django.db.models import get_apps
from django.utils.itercompat import product

try:
    import bz2
    has_bz2 = True
except ImportError:
    has_bz2 = False

from dmqs.manager import MemoryManager
from dmqs.queryset import MemoryQuerySet
from dmqs.foundation import memory_save
from dmqs.integration.memorify_django_model import memorify_m2m, \
                                                   memorify_single_relations, \
                                                   patch_models, \
                                                   unpatch_models
from functools import partial

class MemoryTestCase(TestCase):
    def _fixture_setup(self):
        if getattr(self, 'multi_db', False):
            databases = connections
        else:
            databases = [DEFAULT_DB_ALIAS]

        for db in databases:
            if hasattr(self, 'fixtures'):
                self.handle(*self.fixtures,
                             **{
                                'verbosity': 0,
                                'commit': False,
                                'database': db
                             })

    def handle(self, *fixture_labels, **options):
        '''
            All database code is unnecessary but remove it will broke.
        '''

        #TODO remove database, connection code and stuff

        using = options.get('database')

        connection = connections[using]
        self.style = no_style()

        if not len(fixture_labels):
            print("No database fixture specified. Please provide the path of at least one fixture in the command line.\n")
            return

        verbosity = int(options.get('verbosity'))
        show_traceback = options.get('traceback')

        # commit is a stealth option - it isn't really useful as
        # a command line option, but it can be useful when invoking
        # loaddata from within another script.
        # If commit=True, loaddata will use its own transaction;
        # if commit=False, the data load SQL will become part of
        # the transaction in place when loaddata was invoked.
        commit = options.get('commit', True)

        # Keep a count of the installed objects and fixtures
        fixture_count = 0
        loaded_object_count = 0
        fixture_object_count = 0
        models = set()

        humanize = lambda dirname: "'%s'" % dirname if dirname else 'absolute path'

        # Get a cursor (even though we don't need one yet). This has
        # the side effect of initializing the test database (if
        # it isn't already initialized).
        cursor = connection.cursor()

        # Start transaction management. All fixtures are installed in a
        # single transaction to ensure that all references are resolved.
        if commit:
            transaction.commit_unless_managed(using=using)
            transaction.enter_transaction_management(using=using)
            transaction.managed(True, using=using)

        class SingleZipReader(zipfile.ZipFile):
            def __init__(self, *args, **kwargs):
                zipfile.ZipFile.__init__(self, *args, **kwargs)
                if settings.DEBUG:
                    assert len(self.namelist()) == 1, "Zip-compressed fixtures must contain only one file."
            def read(self):
                return zipfile.ZipFile.read(self, self.namelist()[0])

        compression_types = {
            None:   open,
            'gz':   gzip.GzipFile,
            'zip':  SingleZipReader
        }
        if has_bz2:
            compression_types['bz2'] = bz2.BZ2File

        app_module_paths = []
        for app in get_apps():
            if hasattr(app, '__path__'):
                # It's a 'models/' subpackage
                for path in app.__path__:
                    app_module_paths.append(path)
            else:
                # It's a models.py module
                app_module_paths.append(app.__file__)

        app_fixtures = [os.path.join(os.path.dirname(path), 'fixtures') for path in app_module_paths]

        instances = []
        apps = set()

        try:
            #with connection.constraint_checks_disabled():
            for fixture_label in fixture_labels:
                parts = fixture_label.split('.')

                if len(parts) > 1 and parts[-1] in compression_types:
                    compression_formats = [parts[-1]]
                    parts = parts[:-1]
                else:
                    compression_formats = compression_types.keys()

                if len(parts) == 1:
                    fixture_name = parts[0]
                    formats = serializers.get_public_serializer_formats()
                else:
                    fixture_name, format = '.'.join(parts[:-1]), parts[-1]
                    if format in serializers.get_public_serializer_formats():
                        formats = [format]
                    else:
                        formats = []

                if formats:
                    if verbosity >= 2:
                        print("Loading '%s' fixtures...\n" % fixture_name)
                else:
                    print("Problem installing fixture '%s': %s is not a known serialization format.\n" %
                            (fixture_name, format))
                    if commit:
                        transaction.rollback(using=using)
                        transaction.leave_transaction_management(using=using)
                    return

                if os.path.isabs(fixture_name):
                    fixture_dirs = [fixture_name]
                else:
                    fixture_dirs = app_fixtures + list(settings.FIXTURE_DIRS) + ['']

                for fixture_dir in fixture_dirs:
                    if verbosity >= 2:
                        self.stdout.write("Checking %s for fixtures...\n" % humanize(fixture_dir))

                    label_found = False
                    for combo in product([using, None], formats, compression_formats):
                        database, format, compression_format = combo
                        file_name = '.'.join(
                            p for p in [
                                fixture_name, database, format, compression_format
                            ]
                            if p
                        )

                        if verbosity >= 3:
                            self.stdout.write("Trying %s for %s fixture '%s'...\n" % \
                                (humanize(fixture_dir), file_name, fixture_name))
                        full_path = os.path.join(fixture_dir, file_name)
                        open_method = compression_types[compression_format]
                        try:
                            fixture = open_method(full_path, 'r')
                        except IOError:
                            if verbosity >= 2:
                                self.stdout.write("No %s fixture '%s' in %s.\n" % \
                                    (format, fixture_name, humanize(fixture_dir)))
                        else:
                            try:
                                if label_found:
                                    print("Multiple fixtures named '%s' in %s. Aborting.\n" %
                                        (fixture_name, humanize(fixture_dir)))
                                    if commit:
                                        transaction.rollback(using=using)
                                        transaction.leave_transaction_management(using=using)
                                    return

                                fixture_count += 1
                                objects_in_fixture = 0
                                loaded_objects_in_fixture = 0
                                if verbosity >= 2:
                                    self.stdout.write("Installing %s fixture '%s' from %s.\n" % \
                                        (format, fixture_name, humanize(fixture_dir)))

                                objects = serializers.deserialize(format, fixture, using=using)

                                for obj in objects:
                                    objects_in_fixture += 1
                                    if router.allow_syncdb(using, obj.object.__class__):
                                        loaded_objects_in_fixture += 1
                                        models.add(obj.object.__class__)
                                        try:
                                            obj.object.save = partial(memory_save, obj.object)
                                            #if obj.object.__class__.__name__ == "PedidoExame":
                                            #    import ipdb; ipdb.set_trace() ### XXX BREAKPOINT
                                            obj.object.save()
                                            instances.append(obj)

                                        except (DatabaseError, IntegrityError), e:
                                            msg = "Could not load %(app_label)s.%(object_name)s(pk=%(pk)s): %(error_msg)s" % {
                                                    'app_label': obj.object._meta.app_label,
                                                    'object_name': obj.object._meta.object_name,
                                                    'pk': obj.object.pk,
                                                    'error_msg': e
                                                }
                                            raise e.__class__, e.__class__(msg), sys.exc_info()[2]

                                loaded_object_count += loaded_objects_in_fixture
                                fixture_object_count += objects_in_fixture
                                label_found = True
                            finally:
                                fixture.close()

                            # If the fixture we loaded contains 0 objects, assume that an
                            # error was encountered during fixture loading.
                            if objects_in_fixture == 0:
                                print("No fixture data found for '%s'. (File format may be invalid.)\n" %
                                        (fixture_name))
                                if commit:
                                    transaction.rollback(using=using)
                                    transaction.leave_transaction_management(using=using)
                                return

            # Since we disabled constraint checks, we must manually check for
            # any invalid keys that might have been added
            table_names = [model._meta.db_table for model in models]
            #connection.check_constraints(table_names=table_names)

        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception:
            if commit:
                transaction.rollback(using=using)
                transaction.leave_transaction_management(using=using)
            if show_traceback:
                traceback.print_exc()
            else:
                print("Problem installing fixture '%s': %s\n" %
                         (full_path, ''.join(traceback.format_exception(sys.exc_type,
                             sys.exc_value, sys.exc_traceback))))
            return


        # If we found even one object in a fixture, we need to reset the
        # database sequences.
        if loaded_object_count > 0:
            sequence_sql = connection.ops.sequence_reset_sql(self.style, models)
            if sequence_sql:
                if verbosity >= 2:
                    self.stdout.write("Resetting sequences\n")
                for line in sequence_sql:
                    cursor.execute(line)

        if commit:
            transaction.commit(using=using)
            transaction.leave_transaction_management(using=using)

        if verbosity >= 1:
            if fixture_object_count == loaded_object_count:
                self.stdout.write("Installed %d object(s) from %d fixture(s)\n" % (
                    loaded_object_count, fixture_count))
            else:
                self.stdout.write("Installed %d object(s) (of %d) from %d fixture(s)\n" % (
                    loaded_object_count, fixture_object_count, fixture_count))

        for obj in instances:
            memorify_m2m(obj.object, obj.m2m_data)
            memorify_single_relations(obj.object)
            apps.add(obj.object._meta.app_label)

        self.apps_config = []
        for app_name in settings.INSTALLED_APPS:
            real_app_name = app_name.split('.')[-1]
            self.apps_config.append((real_app_name, patch_models(real_app_name)))

        # Close the DB connection. This is required as a workaround for an
        # edge case in MySQL: if the same connection is used to
        # create tables, load data, and query, the query can return
        # incorrect results. See Django #7572, MySQL #37735.
        if commit:
            connection.close()

    def _fixture_teardown(self):
        from dmqs.repository import Repository
        repository = Repository()
        repository.clean()

        for restore_config in self.apps_config:
            unpatch_models(restore_config[0], restore_config[1])
