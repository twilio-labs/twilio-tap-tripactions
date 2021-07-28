#!/usr/bin/env python
from setuptools import setup

setup(
    name="twilio-tap-tripactions",
    version="0.0.01",
    description="Singer.io tap for extracting data from TripActions API",
    author="Twilio",
    url="https://www.twilio.com/",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["tap_tripactions"],
    install_requires=[
        "singer-python",
        "requests",
    ],
    entry_points="""
    [console_scripts]
    tap-tripactions=tap_tripactions:main
    """,
    packages=["tap_tripactions"],
    include_package_data=True,
)
