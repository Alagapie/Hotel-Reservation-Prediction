from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirement= f.read().splitlines()
setup(
name='Project-1',
author='Abdulbasit',
version = '0.1',
packages= find_packages(),
install_requires=requirement
)