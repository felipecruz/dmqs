from dmqs.repository import Repository
def pytest_runtest_setup(item):
    repository = Repository()
    repository.clean()
