from importlib.machinery import SourceFileLoader
from pathlib import Path

from setuptools import setup, find_packages

module_path = Path(__file__).parent / Path('logme/__init__.py')
logme_module = SourceFileLoader('logme', str(module_path)).load_module()

version = logme_module.__version__

requires = [
    'click',
]

with open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='logme',
    packages=find_packages(exclude=['tests*']),
    install_requires=requires,
    version=version,
    description='package for easy logging',
    long_description=readme,
    author='Luna Chen',
    url='https://github.com/BNMetrics/logme',
    author_email='luna@bnmetrics.com',
    keywords=['logging', 'cli'],
    python_requires='>=3',
    entry_points={'console_scripts': ['logme=logme:cli']},
    license='Apache 2.0',
)
