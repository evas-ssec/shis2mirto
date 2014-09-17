#!/usr/bin/env python
# encoding: utf-8
"""Script for installing the shis2mirto package.

Copyright (C) 2014 Space Science and Engineering Center (SSEC),
 University of Wisconsin-Madison.

This file is part of the shis2mirto software package.

    Written by Eva Schiffer    September 2014
    University of Wisconsin-Madison 
    Space Science and Engineering Center
    1225 West Dayton Street
    Madison, WI  53706
    eva.schiffer@ssec.wisc.edu

distribution:
python setup.py develop --install-dir=$HOME/Library/Python
python setup.py sdist
python setup.py bdist_egg
(cd dist; TODO)
"""
__docformat__ = "restructuredtext en"

from setuptools import setup, find_packages

classifiers = ""
version = '0.1'

setup(
    name='shis2mirto',
    version=version,
    description="Library and scripts to SHIS to Mirto",
    packages = ['shis2mirto'], #find_packages('.'),
    package_data = {'': ['*.txt', '*.gif']},
    zip_safe=False,
    install_requires=[
        'numpy',
        'netCDF4',
        ],
    entry_points = {'console_scripts' : [
            'shis2mirto = shis2mirto.conversion:main',
            ]},
)

