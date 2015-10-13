#!/usr/bin/env python

#
#  The Template-Python distribution is Copyright (C) Sean McAfee 2007-2008,
#  derived from the Perl Template Toolkit Copyright (C) 1996-2007 Andy
#  Wardley.  All Rights Reserved.
#
#  The file "LICENSE" at the top level of this source distribution describes
#  the terms under which this file may be distributed.
#


from distutils.core import setup

setup(name         = 'Template-Python',
      version      = '0.1.post1',
      description  = 'Python port of the Template Toolkit',
      author       = 'Sean McAfee',
      author_email = 'eefacm@gmail.com',
      url          = 'http://template-toolkit.org/python/',
      packages     = ['template', 'template.plugin', 'template.namespace'],
      package_dir  = { 'template.plugin': 'template/plugin', 'template.namespace': 'template/namespace' },
     )
