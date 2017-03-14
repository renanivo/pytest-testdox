#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from setuptools import setup


def read(fname):
    path = os.path.join(os.path.dirname(__file__), fname)
    with open(path) as f:
        return f.read()


setup(
    name='pytest-testdox',
    version='0.2.0',
    description='A testdox format reporter for pytest',
    long_description=read('README.rst'),
    author='Renan Ivo',
    author_email='renanivom@gmail.com',
    url='https://github.com/renanivo/pytest-testdox',
    keywords='pytest testdox test report bdd',
    install_requires=[
        'pytest>=3.0.0'
    ],
    packages=['pytest_testdox'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'pytest11': [
            'testdox = pytest_testdox.plugin',
        ],
    },
)
