import sys
from setuptools import setup, find_packages
requires = [
    'click',
]


setup(
    name='logme',
    packages=find_packages(exclude=['tests*']),
    install_requires=requires,
    version='1.00',
    description='package for easy logging',
    author='Luna Chen',
    author_email='luna@bnmetrics.com',
    entry_points={'console_scripts': ['logme=logme:cli']},
)
