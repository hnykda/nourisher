#!/usr/bin/env python

from distutils.core import setup

setup(name='Nourisher',
      version='0.9.1',
      description='Package for collecting info about feeds',
      author='Daniel Hnyk',
      author_email='kotrfa@gmail.com',
      url='https://github.com/kotrfa/nourisher',
      install_requires=['feedparser', 'newspaper3k', 'selenium', 'pymongo', 'beautifulsoup4'],
      packages=["nourisher",],
      include_package_data=True,
     )
