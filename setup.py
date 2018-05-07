#!/usr/bin/env python
from setuptools import setup, find_packages
setup(
    name="Transfire",
    version="0.1",
    test_suite="transfire.test.AllTests",
    packages=find_packages(),
)
