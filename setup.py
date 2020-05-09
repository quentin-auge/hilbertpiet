# coding: utf8

from setuptools import find_packages, setup

setup(name='hilbertpiet',
      version='0.1',
      description='Hilbert-curve-shaped Piet programs generation',
      author='Quentin Augé',
      author_email='quentin.auge@gmail.com',
      license='closed',
      packages=find_packages(),

      package_data={'hilbertpiet': ['data/piet_numbers.pkl']},

      python_requires='>=3.7',

      classifiers=['Programming Language :: Python :: 3 :: Only',
                   'Operating System :: Unix'],

      install_requires=['pillow'],

      extras_require={
          'testing': ['coverage', 'mock', 'pytest', 'pytest-cov']
      },

      entry_points={
          'console_scripts': [
              'hilbertpiet = hilbertpiet.cli.main:main',
              'optimize-piet-numbers = hilbertpiet.cli.optimize_numbers:main'
          ]
      })
