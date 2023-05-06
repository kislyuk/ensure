#!/usr/bin/env python

import os

from setuptools import find_packages, setup

setup(
    name="ensure",
    version="1.0.3",
    url="https://github.com/kislyuk/ensure",
    license="Apache Software License",
    author="Andrey Kislyuk",
    author_email="kislyuk@gmail.com",
    description="Literate BDD assertions in Python with no magic",
    long_description=open("README.rst").read(),
    python_requires=">=3.6",
    install_requires=["six >= 1.11.0"],
    extras_require={"test": ["coverage", "ruff"]},
    packages=find_packages(exclude=["test"]),
    include_package_data=True,
    platforms=["MacOS X", "Posix"],
    test_suite="test",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
