#!/usr/bin/env python

# -*- coding: utf-8 -*-

from jira_commits_report import __version__
from setuptools import setup, find_packages

print(find_packages())
setup(name='jira-commits-report',
      version=__version__,
      description='Create changelogs from commit Jira issues',
      long_description=open('README.md').read(),
      keywords='',
      author='Pablo Muñoz',
      author_email='pablerass@gmail.com',
      url='https://github.com/pablerass/jira-commits-report',
      license='GPLv3',
      py_modules=['jira_commits_report'],
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
