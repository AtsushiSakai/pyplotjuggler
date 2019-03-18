"""
setup.py

How to upload new release
1. change version in setup.py
2. python setup.py sdist upload

"""
from setuptools import setup, find_packages

from pyplotjuggler import pyplotjuggler

# read README
try:
    import pypandoc
    readme = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    readme = open('README.md').read()

setup(
    name="pyplotjuggler",
    version=pyplotjuggler.VERSION,
    url="https://github.com/AtsushiSakai/pyplotjuggler",
    author="Atsushi Sakai",
    author_email="asakaig@gmail.com",
    maintainer='Atsushi Sakai',
    maintainer_email='asakaig@gmail.com',
    description=("A timeseries visualization tool in Python"),
    long_description=readme,
    python_requires='>3.6.0',
    license="MIT",
    keywords="python matplotlib tkinter",
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
)
