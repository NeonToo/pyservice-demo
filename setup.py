from setuptools import setup, find_packages
import os
import sys
import codecs


def read_file(filename):
    """Read and return `filename` in root dir of project and return string ."""
    here = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(here, filename), 'r').read()


install_requires = []
if os.path.exists("requirement.txt"):
    install_requires = read_file("requirement.txt").split()
    if "win" in sys.platform:
        for item in ['pexpect']:
            try:
                install_requires.remove(item)
            except ValueError as e:
                pass

setup(
    name='pyservice-demo',
    version='0.0.1',
    packages=find_packages(exclude=['test', 'test.*']),
    url='https://github.com/NeonToo/pyservice-demo.git',
    license='',
    author='kaydu',
    description='Microservice demo of Python.',
    include_package_data=True,
    exclude_package_data={'': ['.gitignore']},
    install_requires=install_requires
)
