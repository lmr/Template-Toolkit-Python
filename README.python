Introduction
------------

This is a port to Python of the Perl Template Toolkit (TT): a fast, flexible
and extensible template processing system. The Python port is by Sean McAfee
and is based on the original Perl version by Andy Wardley. For more
information about the Template Toolkit, please see:

  http://template-toolkit.org/

For up-to-date information relating to the Python port, please see:

  http://template-toolkit.org/python/

This file documents many of the design differences between the Perl
and Python implementations of the Template Toolkit.

In no particular order:

Documentation
-------------

All source-code-level documentation from the Perl Template Toolkit has
been copied to the Python version, with all Perl-specific terminology
translated to its Python equivalent.  Documentation appears in Python
docstrings, as appropriate.  The main body of POD documentation for
each Perl module appears as the corresponding Python module's
docstring.  For example:

  $ python
  >>> import template.stash
  >>> help(template.stash)

This prints the main documentation for the Python version of the
Template::Stash module.


Grammar
-------

A casual search revealed no well-established Python parser module to
compare with Parse::Yapp, so I simply translated the generated grammar
module Template::Grammar by hand.

Late experimentation suggests that it may be possible to coerce a
Parse::Yapp source file to emit Python code, or at least code in some
format that is easily transformable to Python.  This avenue should be
explored.


Template Input and Output
-------------------------

One can specify an input template to Perl's Template::process() either
as a string (to indicate a source file or block name) or a reference
to a string (which contains the input text).  Perl's reference
semantics are awkward to emulate in Python, so an alternate scheme is
used.  Rather than specifying template text via reference, the text is
wrapped in an instance of the template.util.Literal class:

  from template import Template
  from template.util import Literal

  Template().process(Literal("[% x %]"), { "x": 42 })

Alternatively, one may call the processString method instead, which
simply wraps its first argument in a Literal and calls process().

  Template().processString("[% x %]", { "x": 42 })

Unlike the Perl Toolkit, the Python version of process() does not
accept a third argument indicating a destination for the processed
template text; instead, the text is returned.  The caller must take
responsibility for directing the text to the desired destination.
While the Perl version of process() returns false to indicate an error
condition, which must be fetched with the error() method, the Python
version simply raises an exception.

Perl:

  use Template;

  my $template = Template->new;
  $template->process("someblock") or die $template->error;

Python:

  from template import Template

  template = Template()
  print template.process("someblock")

Or just:

  print Template().process("someblock")

You can, of course, catch a raised exception to take special action.

  from template import Template, TemplateException

  try:
    print Template().process("someblock")
  except TemplateException, e:
    print >>sys.stderr, "Got exception: ", e

The OUTPUT and OUTPUT_PATH options are honored, but do not otherwise
change the behavior of process().



Error Reporting
---------------

As it makes for more idiomatic Python, errors are reported by raising
an exception, rather than returning a status code and/or setting an
instance or module variable.  Since the primary purpose of
Template::Base is to provide such an error-reporting structure, it has
been omitted from the Python implementation.

The (result, error-code) return-value scheme is a public interface of
the Template::Iterator module, so it has been retained by
template.iterator.

Provider-type interfaces (template.filters, template.plugins, etc.)
return None to indicate that the requested resource has been declined,
rather than returning STATUS_DECLINED.


Subroutines
-----------

In Python, it isn't so straightforward to put subroutines in a data
structure, as, for example, with $Template::Stash::SCALAR_OPS:

  our $SCALAR_OPS = {
    ...
    'match' => sub { ... },
    'search' => sub { ... },
    ...
  };

Python function definitions are classed as "statements," and may not
appear in an expression.  (If the function body consists of only a
single expression, a lambda expression may be used, but this does not
suffice in many cases.)  My original approach was simply to split the
definition and registration into two steps:

  def scalar_match():
    ...

  def scalar_search():
    ...

  SCALAR_OPS = {
    'match': scalar_match,
    'search': scalar_search,
    ...
  }

This scheme suffers from unnecessarily distributed information; it
would be easy to add a new function but forget to update SCALAR_OPS.
I eventually hit upon the idea of using function decorators to perform
registration:

  @scalar_op("match")
  def scalar_match(...):
    ...

  @list_op("push")
  def list_push(...):
    ...

  @hash_op("keys")
  def hash_keys(...):
    ...

This has the added advantage that the decorators may be employed by
users to add custom vmethods.  For example:

  from template.stash import scalar_op

  @scalar_op("double")
  def my_double(x):
    return x * 2

As opposed to the slightly more obscure:

  $Template::Stash::SCALAR_OP->{double} = sub { shift * 2 };



Filters
-------

Dynamic filter factories in the Perl TT are indicated with a
two-element array reference, where the second element is true, eg:

  sub password_filter_factory {
    my $char = shift;
    return sub {
      return $char x length $_[0];
    }
  }

  my $filters = Template::Filters->new({
    FILTERS => {
      password => [ \&password_filter_factory, 1 ]
    }
  });

In Python this is accomplished more simply by setting an attribute on
the function object:

  def password_filter_factory(char):
    def password_filter(str):
      return char * len(str)
    return password_filter

  password_filter_factory.dynamic_filter = True

  filters = template.filters.Filters({
    'FILTERS': {
      'password': password_filter_factory
    }
  })

Even easier, a function decorator is provided to set the attribute:

  from template.filters import dynamic_filter

  @dynamic_filter
  def password_filter_factory(char):
    def password_filter(str):
      return char * len(str)
    return password_filter


Scalar semantics
----------------

Python variables have very different semantics from Perl scalars.  The
most important differences from the perspective of generated code are
these:

*  Python variables do not automatically convert to strings or numbers
   as appropriate as Perl scalars do.

*  Notions of booleanness differ.  Empty Python lists or dictionaries
   are considered false, while in Perl all references are true, even
   references to empty arrays or hashes.  The string "0" is true in
   Python, but false in Perl.

Perl's scalar semantics are expressed in the Python class PerlScalar,
found in the template.util module, and available to generated code
under the name "scalar".  A PerlScalar wraps a Python value and
provides Perl-like semantics via special methods like __add__,
__nonzero__, etc.  PerlScalars are employed ubiquitously in generated
code.  Constants are wrapped explicitly in a scalar; for example, this
template:

  [% IF "0"; "yes"; ELSE; "no"; END %]

...would be translated into this code:

  if scalar("0"):
    output.write("yes")
  else:
    output.write("no")

Note that without the scalar wrapper, a bare Python

  if "0":

...would take the opposite branch of the if statement.

Operations involving two PerlScalars result in another PerlScalar.
Arithmetic operations result in Perl-style conversion from string to
number, if necessary.

Python values are wrapped in a PerlScalar on being retrieved from a
Stash object, and are unwrapped on being stored in one.

See the PerlScalar documentation in template/util.py for more
exhaustive information and examples.


Classes
-------

Perl classes typically occur in one-to-one correspondence with module
source files, and so they can be uniquely identified by a package
identifier like "Template::Plugin::File".  In Python the situation is
a little more complicated; there is no conventional relationship
between the path to a module and the primary class of interest it
exposes.  Therefore, in situations where the user may identify a class
(template.config, template.plugins), the class may be identified
unambiguously using a two-element tuple: the module name, followed by
the class name within that module.  For example, from
template.plugins:

  STD_PLUGINS = {
    "datafile":  ("template.plugin.datafile", "Datafile"),
    "date":      ("template.plugin.date", "Date"),
    ...
  }

A user-supplied class should be identified by using this scheme, or
one of two alternates.  First, the class object may be given directly:

  class MyFilters:
    ...

  template.config.Config.FILTERS = MyFilters

  class MyCustomPlugin:
    ...

  tt = Template({ "PLUGINS": { "custom": MyCustomPlugin } })

This of course requires that the class be loaded prior to processing
the template.  The second alternate is to supply a module name as a
plain string.  A simple heuristic is applied to guess a class name:
the last component of the module name is capitalized.

  tt = Template({ "PLUGINS": { "custom": "my.org.plugins.custom" } })

Here, the name of the plugin class is assumed to be "Custom".

This last way of identifying classes should typically be avoided, as
less precise than the other options.


Arrays and Hashes
-----------------

Perl's arrays and hashes are fundamental data types, and the type that
a reference points to can be inferred at compile time from the way
it's used (eg. $ref->[$index] or $ref->{$key}).  In Python the
situation is more nebulous.  Any class can expose a list-like or
dict-like interface, and functions that expect a list or dict will
usually happily accept an object of such a class.  Such effects can be
achieved in Perl via "use overload '@{}'" et al, but seemingly are
comparatively rarer than in Python, and the Perl Template Toolkit
would reject such hijinks.  It would not be valid to apply the
[% FOREACH %] construct to a stash variable that is not an
honest-to-goodness array reference, but an object that overloaded
'@{}'.

I have tried to be as permissive as possible in not requiring objects
to be instances of list, tuple, or dict, but to pass along any object
that can raise an exception if used in an inappropriate manner.  For
example, the function is_seq() in template.util guesses that an object
is a sequence type if it supports iteration but is not a string.  This
isn't a perfect solution (I just recently discovered that Python's
base Exception class is iterable--what the heck?), and cannot be
universally applied (such as in deciding whether a stash object can
have scalar, array, or hash vmethods called on it), but it seems to
work well enough for the time being.  In more recent vintages of
Python it's possible to derive classes directly from the built-in
container types; one more permanent solution might involve requiring
classes that expect to be transparently treated as containers by the
Template Toolkit to be so derived.


Hash Keys
---------

Perl hash keys are always converted to strings; Python dictionary keys
aren't.  The following dict contains two distinct items:

  mydict = { 1: "number", "1": "string" }

Since the Template Toolkit assumes Perlish hash semantics, there is
some unavoidable ambiguity when it comes to retrieving items from a
dict in the stash:

  [% x = 1; mydict.x  # is this "number" or "string"? %]

I have tried to follow a principle of least surprise here.  Dict
lookup is attempted up to three times, first using the given key, then
using the stringified key if possible, then using the key converted to
an integer if possible.  Therefore the previous template snippet would
print "number", and the other cases are exhibited thusly:

  mydict = { 1: "one", "2": "two" }

  [% x = "1"; y = 2 %]
  [% mydict.x  # "one" %]
  [% mydict.y  # "two" %]

In the more complicated case of an object that supported conversion to
both string and integer, the string version would win out.

  class Dubious:
    def __str__(self): return "1"
    def __int__(self): return 1

  dubious = Dubious()

  mydict = { 1: "number", "1": "string" }

  [% mydict.dubious #  prints "string" %]


Unit Tests
----------

All unit tests have been translated using the standard Python unittest
module.  This is the framework with which I am most familiar, but it
transpires that the Perl unit tests don't lend themselves particularly
well to this approach.  A typical unittest test should examine each
aspect of the object or class under test, one per method.  For
example:

  class MyTest(unittest.TestCase):
    def testMethodOne(self):
      ...
    def testMethodTwo(self):
      ...

No order of test evaluation is defined, which encourages tests to be
written independently of each other.  In contrast, the Perl unit tests
typically include a long sequence of template/output pairs that must
be processed in sequence, since later templates depend on state
established by earlier templates.  The Python tests therefore don't
exploit the full power of the unittest approach, and have the
appearance of mere boilerplate.  Many test programs share a very
similar structure:

  class FooTest(TestCase):
    def testFoo(self):
      # some setup
      self.Expect(DATA, templates, variables)

    # No other test methods!

  DATA = r"""
  -- test --
  ...
  -- expect --
  ...
  """

  main()

In my opinion, the existing tests provide a good, but far from
exhaustive, level of test coverage.  For example, on a few occasions
I've noticed Perl functions that I neglected to translate into Python,
and the omission went undetected by the relevant unit test.  Many more
tests could and should be written in the mold of the unittest module,
and backported into the Perl version of the Toolkit.


PERL/RAWPERL/evalperl
---------------------

For obvious reasons, the Python version of the Template Toolkit does
not support the PERL or RAWPERL template directives.  It does,
however, have the parallel directives PYTHON and RAWPYTHON, and the
parallel configuration option EVAL_PYTHON.  The variables "context"
and "stash" are available, mirroring the $context and $stash Perl
variables--but note that stash.get() returns a PerlScalar wrapping
object, which can be upwrapped by calling its value() method.

Perl version:

  [% PERL %]
    print $context->include('myfile');
    $stash->set(foo => 'bar');
    print 'foo value: ', $stash->get('foo');
  [% END %]

Python version:

  [% PYTHON %]
    print context.include('myfile'),
    stash.set('foo', 'bar')
    print 'foo value:', stash.get('foo'),
  [% END %]

Note that Python's print statement has semantics that may be
considered nontrivial; according to the online documentation, "a space
is written before each object is (converted [to a string] and)
written, unless the output system believes it is positioned at the
beginning of a line."  Limited experimentation suggests that the
"output system" may become confused in the context of template
evaluation.  To eliminate any ambiguity, one may alternately produce
output by calling the "write" method of the variable "stdout".

Alternate Python version:

  [% PYTHON %]
    stdout.write(context.include('myfile'))
    stash.set('foo', 'bar')
    stdout.write('foo value: ')
    stdout.write(stash.get('foo'))
  [% END %]

The print statement and the stdout variable both send output to
sys.stdout, which is temporarily set to a StringIO object during the
evaluation of the block.  Note that the write() method of StringIO,
like that of ordinary Python file objects, accepts only a single
argument.  For convenience, output may alternately be sent to the
write() method of the variable "output", which accepts any number of
arguments.

Another alternate Python version:

  [% PYTHON %]
    output.write(context.include('myfile'))
    stash.set('foo', 'bar')
    output.write('foo value: ', stash.get('foo'))
  [% END %]

In RAWPYTHON blocks, only the "output" variable is available, taking
the place of the RAWPERL $output variable.

  [% RAWPERL %]
    $output .= foo() . bar();
  [% END %]

  Vs:

  [% RAWPYTHON %]
    output.write(foo(), bar())
  [% END %]

Astute readers may be wondering how Python's (in)famous
indentation-as-block-delimiter feature figures into the evaluation of
PYTHON/RAWPYTHON blocks.  The answer is that prior to passing the
contents of such blocks to the Python interpreter, each line of code
in such blocks has a number of leading whitespace characters stripped
which is equal to the smallest number of leading whitespace characters
found on any line in the block, not including empty lines and lines
consisting solely of whitespace.  This should produce unsurprising
results, as long as all lines in the block are indented by a
consistent amount.  Inconsistent indentation will likely produce a
syntax error, and should be avoided.

An example of a block that will cause a syntax error:

  [% PYTHON %]
    print "line 1"
      print "line 2"
  [% END %]

Another block that will cause a syntax error:

  [% PYTHON %]
      print "line 1"
    print "line 2"
  [% END %]

Note that leading whitespace is stripped indiscriminately; tab and
space characters are not distinguished at all.  One shouldn't mix
tabs and spaces in leading whitespace, or problems are very likely to
occur.

For convenience in PYTHON blocks, a standard filter called "repr" is
provided which passes the stringified version of its argument to the
built-in Python function repr().  Example:

  [% x = 1; y = 2 %]
  [% PYTHON %]
    print "x =", [% x | repr %], "; y =", [% y | repr %]
    # Or:
    print "x = %s; y = %s" % ([% x | repr %], [% y | repr %])
  [% END %]

Finally, there is a standard filter "python", but it is more limited
than its "evalperl" counterpart.  The latter filter produces its final
expression as output; for example, this prints "hello world":

  [% FILTER perl %]
    x = f()
    y = g()
    "hello world"
  [% END %]

The same effect cannot be achieved in Python readily, if at all;
Python's dynamic code evaluation feature does not return the final
expression as Perl's does.  One must produce output explicitly by
printing it, just as if the filtered text appeared in a PYTHON block,
as described above.

  [% FILTER python %]
    x = f()
    y = g()
    print "hello world"
  [% END %]


Precompiled Templates
---------------------

The Python Template Toolkit supports the COMPILE_DIR and COMPILE_EXT
options, just as the Perl version does.  Another level of optimization
that is possible, but not yet exploited, is to byte-compile the
precompiled template source code.  A future version Python Toolkit
should take advantage of this capability.


