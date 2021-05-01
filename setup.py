from importlib.machinery import SourceFileLoader

from setuptools import find_packages, setup

version = SourceFileLoader(
    'version', 'mongoengine_plus/version.py'
).load_module()


with open('README.md', 'r') as f:
    long_description = f.read()


setup(
    name='mongoengine-plus',
    version=version.__version__,
    author='Cuenca',
    author_email='dev@cuenca.com',
    description='Extras for mongoengine',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/cuenca-mx/mongoengine-plus',
    packages=find_packages(),
    include_package_data=True,
    package_data=dict(mongoengine_plus=['py.typed']),
    python_requires='>=3.8',
    install_requires=[
        'mongoengine>=0.20.0',
        'dnspython>=2.0.0,<2.2.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
