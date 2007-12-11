#!/usr/bin/env python

from distutils.core import setup

setup(name         = 'Template-Python',
      version      = '0.1',
      description  = 'Python port of the Template Toolkit',
      author       = 'Sean McAfee',
      author_email = 'eefacm@gmail.com',
      url          = 'http://template-toolkit.org/python/',
      packages     = ['template', 'template.plugin', 'template.namespace'],
      package_dir  = { 'template.plugin': 'template/plugin', 'template.namespace': 'template/namespace' },
     )