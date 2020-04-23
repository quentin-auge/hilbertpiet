# coding: utf8

from setuptools import find_packages, setup

setup(name='piet',
      version='0.1',
      description='Piet playground',
      author='Quentin Augé',
      author_email='quentin.auge@gmail.com',
      license='closed',
      packages=find_packages(),

      python_requires='>=3.6',

      classifiers=['Programming Language :: Python :: 3 :: Only',
                   'Operating System :: Unix'],

      extras_require={
          'testing': ['coverage', 'mock', 'pytest', 'pytest-cov']
      },

      entry_points={
          'console_scripts': [
              'piet = piet.run:main'
          ]
      })
