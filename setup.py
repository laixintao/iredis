#!/usr/bin/env python
import os
import sys
from setuptools import setup, find_packages

from iredis import __version__


f = open(os.path.join(os.path.dirname(__file__), "README.md"))
long_description = f.read()
f.close()

with open(os.path.join(os.path.dirname(__file__), "requirements.txt")) as req_f:
    requirements = req_f.readlines()


setup(
    name="iredis",
    version=__version__,
    description="A Terminal Client for Redis with AutoCompletion and Syntax Highlighting. ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/laixintao/iredis",
    author="laixintao",
    author_email="laixintaoo@gmail.com",
    maintainer="laixintao",
    maintainer_email="laixintaoo@gmail.com",
    keywords=["Redis", "key-value store", "Commandline tools"],
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=requirements,
    # include_package_data=True,
    package_data={"mypkg": ["commands.csv", "commands.json", "command_syntax.csv"]},
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
    ],
    entry_points={"console_scripts": ["iredis = iredis.entry:main"]},
)
