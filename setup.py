#!/usr/bin/env python

# -*- coding: utf-8 -*-

#from jira_commits_report import __version__
from setuptools import setup, find_packages

print(find_packages())
setup(name='jira-commits-report',
      #version=__version__,
      description='',
      #long_description=open('README.md').read(),
      keywords='',
      author='',
      author_email='',
      url='',
      license='',
      py_modules=['jira_commits_report'],
      #packages=find_packages(exclude=['test']),
      entry_points={
          'console_scripts': [
             'jira-commits-report = jira_commits_report:main',
          ],
      },
      include_package_data=True,
      zip_safe=False,
      install_requires=[line for line in open('requirements.txt')],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Topic :: Utilities'
      ]
)
