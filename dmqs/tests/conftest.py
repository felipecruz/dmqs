from dmqs.repository import Repository

def pytest_runtest_setup():
    repository = Repository()
    repository.clean()
