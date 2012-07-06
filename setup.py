from distutils.core import setup

setup(name='dmqs',
      version='0.1a',
      description='django memory queryset',
      author='Felipe Cruz',
      author_email='felipecruz@loogica.net',
      url='http://dmqs.readthedocs.org',
      install_requires=["django>=1.2.5"],
      license="BSD",
      packages=['dmqs'])
