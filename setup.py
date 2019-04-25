from setuptools import setup, find_packages

setup(
    name='pyservice-demo',
    version='0.0.1',
    packages=find_packages(exclude=['test', 'test.*']),
    url='https://github.com/NeonToo/pyservice-demo.git',
    license='',
    author='kaydu',
    description='Microservice demo of Python.',
    include_package_data=True,
    exclude_package_date={'': ['.gitignore']},
)
