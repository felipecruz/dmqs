import os
import sys

sys.path.append('./dmqs/django_app/')
sys.path.append('./dmqs/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'mock_settings'

from dmqs.integration.memorify_django_model import *

from django.test.utils import setup_test_environment, \
                              teardown_test_environment

from django_app.models import Friend, Dog, BestFriend, Friendship

from dmqs.manager import MemoryManager

unpatch_info, default_save = patch_models("django_app")

from datetime import *

try:
    import IPython
    IPython.embed()
except:
    import code
    code.InteractiveConsole(locals=globals()).interact()
