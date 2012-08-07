from dmqs.repository import Repository
from dmqs.queryset import MemoryQuerySet

def pytest_runtest_setup():
    repository = Repository()
    repository.clean()
    MemoryQuerySet.fetch_from_repo = False
