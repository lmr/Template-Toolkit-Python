from template import Template
from template.test import TestCase, main


class EvalPythonTest(TestCase):
  def testEvalPython(self):
    tt_no_python = Template({ "INTERPOLATE": 1,
                              "POST_CHOMP": 1,
                              "EVAL_PYTHON": 0,
                              "INCLUDE_PATH": "test/lib" })
    tt_do_python = Template({ "INTERPOLATE": 1,
                              "POST_CHOMP": 1,
                              "EVAL_PYTHON": 1,
                              "INCLUDE_PATH": "test/lib" })
    ttprocs = (("no_python", tt_no_python), ("do_python", tt_do_python))
    self.Expect(DATA, ttprocs, self._callsign())


DATA = r"""
-- test --
[% META
   author  = 'Andy Wardley'
   title   = 'Test Template $foo #6'
   version = 1.23
%]
[% TRY %]
[% PYTHON %]
    output = "author: [% template.author %]\n"
    stash.set('a', 'The cat sat on the mat')
    output += "more python generated output\n"
    print output,
[% END %]
[% CATCH %]
Not allowed: [% error +%]
[% END %]
a: [% a +%]
a: $a
[% TRY %]
[% RAWPYTHON %]
output.write("The cat sat on the mouse mat\n")
stash.set('b', 'The cat sat where?')
[% END %]
[% CATCH %]
Still not allowed: [% error +%]
[% END %]
b: [% b +%]
b: $b
-- expect --
Not allowed: python error - EVAL_PYTHON not set
a: alpha
a: alpha
Still not allowed: python error - EVAL_PYTHON not set
b: bravo
b: bravo

-- test --
[% TRY %]
nothing
[% PYTHON %]
We don't care about correct syntax within PYTHON blocks if EVAL_PYTHON isn't set.
They're simply ignored.
[% END %]
[% CATCH %]
ERROR: [% error.type %]: [% error.info %]
[% END %]
-- expect --
nothing
ERROR: python: EVAL_PYTHON not set

-- test --
some stuff
[% TRY %]
[% INCLUDE badrawpython %]
[% CATCH %]
ERROR: [[% error.type %]] [% error.info %]
[% END %]
-- expect --
some stuff
This is some text
ERROR: [python] EVAL_PYTHON not set

-- test --
-- use do_python --
some stuff
[% TRY %]
[% INCLUDE badrawpython %]
[% CATCH +%]
ERROR: [[% error.type %]]
[% END %]
-- expect --
some stuff

# This is some text
# more stuff goes here
ERROR: [file]

-- test --
-- use do_python --
[% META author = 'Andy Wardley' %]
[% PYTHON %]
    output = "author: [% template.author %]\n"
    stash.set('a', 'The cat sat on the mat')
    output += "more python generated output\n"
    print output,
[% END %]
-- expect --
author: Andy Wardley
more python generated output

-- test --
-- use do_python --
[% META 
   author  = 'Andy Wardley'
   title   = 'Test Template $foo #6'
   version = 3.14
%]
[% PYTHON %]
    output = "author: [% template.author %]\n"
    stash.set('a', 'The cat sat on the mat')
    output += "more python generated output\n"
    print output,
[% END %]
a: [% a +%]
a: $a
[% RAWPYTHON %]
output.write("The cat sat on the mouse mat\n")
stash.set('b', 'The cat sat where?')
[% END %]
b: [% b +%]
b: $b
-- expect --
author: Andy Wardley
more python generated output
a: The cat sat on the mat
a: The cat sat on the mat
The cat sat on the mouse mat
b: The cat sat where?
b: The cat sat where?

-- test --
[% BLOCK foo %]This is block foo[% END %]
[% PYTHON %]
print context.include('foo'),
print "\nbar\n",
[% END %]
The end
-- expect --
This is block foo 
bar
The end

-- test --
[% TRY %]
   [%- PYTHON %] raise Exception("nothing to live for\n") [% END %]
[% CATCH %]
   error: [% error %]
[% END %]
-- expect --
   error: None error - nothing to live for

"""

main()
