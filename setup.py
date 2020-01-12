#!/usr/bin/env python3
# This file is part of the docpath package.
# Please see the COPYRIGHT and README.rst files at the top level of this
# repository for full copyright notices, license terms and support information.
from os.path import dirname, join
from setuptools import setup, find_packages


def read(fname):
    with open(join(dirname(__file__), fname), 'r', encoding='utf-8') as file:
        return file.read()


setup(
    name='docpath',
    version='0.1.0',
    description="Use xpath style paths with docutils document trees.",
    long_description=read('README.rst'),
    author='David Harper',
    author_email='python-packages@libateq.org',
    url='https://bitbucket.org/libateq/docpath',
    project_urls={
        "Bug Tracker": 'https://bitbucket.org/libateq/docpath/issues',
        "Source Code": 'https://bitbucket.org/libateq/docpath',
    },
    keywords='docpath docutils sphinx xpath',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',  # noqa
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Documentation',
    ],
    license='GPL-3',
    platforms='any',
    packages=find_packages(),
    python_requires='>=3.5',
    install_requires=[
        'docutils>=0.14',
    ],
    zip_safe=False,
)
