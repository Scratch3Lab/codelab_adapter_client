#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()
REQUIRES_PYTHON = ">=3.6.0"
# todo verison, pyzmq 18 19 20 ok
requirements = ['pyzmq==20.0.0', 'msgpack-python==0.5.6', 'loguru==0.5.3', 'uflash==1.3.0', "zeroconf==0.28.8", "click==7.1.2", "dynaconf==3.1.2"]

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
            'codelab-message-pub = codelab_adapter_client.tools.pub:pub',
            'codelab-adapter-helper = codelab_adapter_client.tools.adapter_helper:adapter_helper',
            'codelab-adapter-settings = codelab_adapter_client.tools.adapter_helper:list_settings',
            'codelab-mdns-registration = codelab_adapter_client.tools.mdns_registration:main',
            'codelab-mdns-browser = codelab_adapter_client.tools.mdns_browser:main',
            'codelab-linda = codelab_adapter_client.tools.linda:cli',            
        ],
    },
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/wwj718/codelab_adapter_client',
    version='4.1.2',
    zip_safe=False,
)
