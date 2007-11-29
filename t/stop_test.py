from template import Template, TemplateException
from template.test import TestCase, main


def halt(*args):
  raise TemplateException("stop", "big error")


class StopTest(TestCase):
  def testStop(self):
    ttblocks = { "header": lambda *_: "This is the header\n",
                 "footer": lambda *_: "This is the footer\n",
                 "halt1": halt }
    ttvars = { "halt": halt }
    ttbare = Template({ "BLOCKS": ttblocks })
    ttwrap = Template({"PRE_PROCESS": "header",
                       "POST_PROCESS": "footer",
                       "BLOCKS": ttblocks })
    self.Expect(DATA, (("bare", ttbare), ("wrapped", ttwrap)), ttvars)


DATA = r"""
-- test --
This is some text
[% STOP %]
More text
-- expect --
This is some text

-- test --
This is some text
[% halt %]
More text
-- expect --
This is some text

-- test --
This is some text
[% INCLUDE halt1 %]
More text
-- expect --
This is some text

-- test --
This is some text
[% INCLUDE myblock1 %]
More text
[% BLOCK myblock1 -%]
This is myblock1
[% STOP %]
more of myblock1
[% END %]
-- expect --
This is some text
This is myblock1

-- test --
This is some text
[% INCLUDE myblock2 %]
More text
[% BLOCK myblock2 -%]
This is myblock2
[% halt %]
more of myblock2
[% END %]
-- expect --
This is some text
This is myblock2


#------------------------------------------------------------------------
# ensure 'stop' exceptions get ignored by TRY...END blocks
#------------------------------------------------------------------------
-- test --
before
[% TRY -%]
trying
[% STOP -%]
tried
[% CATCH -%]
caught [[% error.type %]] - [% error.info %]
[% END %]
after

-- expect --
before
trying


#------------------------------------------------------------------------
# ensure PRE_PROCESS and POST_PROCESS templates get added with STOP
#------------------------------------------------------------------------

-- test --
-- use wrapped --
This is some text
[% STOP %]
More text
-- expect --
This is the header
This is some text
This is the footer

"""

main()
