from template import Template
from template.document import Document
from template.test import TestCase, main


#  Define a dummy object for runtime processing
class DummyContext:
  def visit(self, *args):
    pass
  def leave(self, *args):
    pass


class DocumentTest(TestCase):
  def testDocument(self):
    # Create a document and check accessor methods for blocks and metadata
    doc = Document(
      { 'BLOCK': lambda *_: 'some output',
        'DEFBLOCKS': { 'foo': lambda *_: 'the foo block',
                       'bar': lambda *_: 'the bar block' },
        'METADATA': { 'author': 'Andy Wardley',
                      'version': 3.14 }})
    c = DummyContext()
    self.failUnless(doc)
    self.assertEquals('Andy Wardley', doc.author)
    self.assertEquals(3.14, doc.version)
    self.assertEquals('some output', doc.process(c))
    self.failUnless(callable(doc.block()))
    self.failUnless(callable(doc.blocks()['foo']))
    self.failUnless(callable(doc.blocks()['bar']))
    self.assertEquals('some output', doc.block()())
    self.assertEquals('the foo block', doc.blocks()['foo']())
    self.assertEquals('the bar block', doc.blocks()['bar']())

    tproc = Template({ 'INCLUDE_PATH': 'test/src' })
    self.Expect(DATA, tproc, { 'mydoc': doc })

DATA = r"""
-- test --
# test metadata
[% META
   author = 'Tom Smith'
   version = 1.23 
-%]
version [% template.version %] by [% template.author %]
-- expect --
version 1.23 by Tom Smith

# test local block definitions are accessible
-- test --
[% BLOCK foo -%]
   This is block foo
[% INCLUDE bar -%]
   This is the end of block foo
[% END -%]
[% BLOCK bar -%]
   This is block bar
[% END -%]
[% PROCESS foo %]

-- expect --
   This is block foo
   This is block bar
   This is the end of block foo

-- test --
[% META title = 'My Template Title' -%]
[% BLOCK header -%]
title: [% template.title or title %]
[% END -%]
[% INCLUDE header %]
-- expect --
title: My Template Title

-- test --
[% BLOCK header -%]
HEADER
component title: [% component.name %]
 template title: [% template.name %]
[% END -%]
component title: [% component.name %]
 template title: [% template.name %]
[% PROCESS header %]
-- expect --
component title: input text
 template title: input text
HEADER
component title: header
 template title: input text

-- test --
[% META title = 'My Template Title' -%]
[% BLOCK header -%]
title: [% title or template.title  %]
[% END -%]
[% INCLUDE header title = 'A New Title' %]
[% INCLUDE header %]
-- expect --
title: A New Title

title: My Template Title

-- test --
[% INCLUDE $mydoc %]
-- expect --
some output

-- stop --
# test for component.caller and component.callers patch
-- test --
[% INCLUDE one;
   INCLUDE two;
   INCLUDE three;
%]
-- expect --
one, three
two, three
"""

main()
