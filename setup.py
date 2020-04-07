#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()
REQUIRES_PYTHON = ">=3.6.0"
requirements = ['pyzmq', 'msgpack-python', 'loguru']

setup_requirements = [
    'pytest-runner',
]

test_requirements = ['pytest', 'pytest-mock']

setup(
    python_requires=REQUIRES_PYTHON,
    author="Wenjie Wu",
    author_email='wuwenjie718@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description=
    "Python Boilerplate contains all the boilerplate you need to create a Python package.",
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='codelab_adapter_client',
    name='codelab_adapter_client',
    packages=[
        'codelab_adapter_client', 'codelab_adapter_client.tools'
    ],  # find_packages(include=['codelab_adapter_client','codelab_adapter_client.tools']),
    entry_points={
        'console_scripts': [
            'codelab-message-monitor = codelab_adapter_client.tools.monitor:monitor',
            'codelab-message-trigger = codelab_adapter_client.tools.trigger:trigger',
            'codelab-message-pub = codelab_adapter_client.tools.pub:pub'
        ],
    },
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/wwj718/codelab_adapter_client',
    version='1.2.0',
    zip_safe=False,
)
