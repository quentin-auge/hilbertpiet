# coding: utf8

from setuptools import find_packages, setup

setup(name='piet',
      version='0.1',
      description='Piet playground',
      author='Quentin Augé',
      author_email='quentin.auge@gmail.com',
      license='closed',
      packages=find_packages(),

      package_data={'piet': ['data/piet_numbers.pkl']},

      python_requires='>=3.7',

      classifiers=['Programming Language :: Python :: 3 :: Only',
                   'Operating System :: Unix'],

      extras_require={
          'testing': ['coverage', 'mock', 'pytest', 'pytest-cov']
      },

      entry_points={
          'console_scripts': [
              'piet = piet.cli.run:main',
              'optimize-piet-numbers = piet.cli.optimize_numbers:main'
          ]
      })
