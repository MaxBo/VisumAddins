# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 20:33:08 2016

@author: MaxBohnet
"""

from setuptools import setup, find_packages


setup(
    name="visumhelpers",
    version="0.8",
    description="helpers for Visum AddIns",

    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['visumhelpers'],

    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    data_files=[
        ],

    extras_require=dict(
        extra=[],
        test=[]
    ),

    install_requires=[
        'lxml',
        #'numpy',
        #'tables',

    ],
)
