#!/usr/bin/env python
import os

from setuptools import setup


def read(fname):
    path = os.path.join(os.path.dirname(__file__), fname)
    with open(path) as f:
        return f.read()


setup(
    name='pytest-testdox',
    version='3.1.0',
    description='A testdox format reporter for pytest',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    author='Renan Ivo',
    author_email='renanivom@gmail.com',
    url='https://github.com/renanivo/pytest-testdox',
    keywords='pytest testdox test report bdd',
    install_requires=[
        'pytest>=4.6.0',
    ],
    packages=['pytest_testdox'],
    python_requires=">=3.7",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
    ],
    entry_points={
        'pytest11': [
            'testdox = pytest_testdox.plugin',
        ],
    },
)
