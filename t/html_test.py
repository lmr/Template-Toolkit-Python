# coding: latin-1
import os

from template.test import TestCase, main


class HtmlTest(TestCase):
  def testHtml(self):
    cfg = { "INCLUDE_PATH": os.path.join(os.pardir, "templates", "html") }
    vars = { "entities": True }
    self.Expect(DATA, cfg, vars)


DATA = r"""
-- test --
-- name html plugin --
[% USE HTML -%]
OK
-- expect --
OK

-- test --
-- name html filter --
[% FILTER html -%]
< &amp; >
[%- END %]
-- expect --
&lt; &amp;amp; &gt;

-- test --
-- name html entity --
[% TRY; 
     text =
      "Léon Brocard" | html_entity;
   CATCH;
     error;
   END;
 "passed" IF text == "L&eacute;on Brocard";
 "passed" IF text == "L&#233;on Brocard";
%]
-- expect --
-- process --
[%  IF entities -%]
passed
[%- ELSE -%]
html_entity error - cannot locate Apache::Util or HTML::Entities
[%- END %]

-- test --
[% USE html; html.url('my file.html') -%]
-- expect --
my%20file.html

-- test --
-- name escape --
[% USE HTML -%]
[% HTML.escape("if (a < b && c > d) ...") %]
-- expect --
if (a &lt; b &amp;&amp; c &gt; d) ...

-- test --
-- name sorted --
[% USE HTML(sorted=1) -%]
[% HTML.element(table => { border => 1, cellpadding => 2 }) %]
-- expect --
<table border="1" cellpadding="2">

-- test --
-- name attributes --
[% USE HTML -%]
[% HTML.attributes(border => 1, cellpadding => 2).split.sort.join %]
-- expect --
border="1" cellpadding="2"

-- stop --
# These are tests for the now defunct 'entity' option.
# At some point this functionality should return elsewhere
# so we'll keep the tests lying around in case we need them
# again later.

-- test --
[% FILTER html(entity = 1) -%]
< &amp; >
[%- END %]
-- expect --
&lt; &amp; &gt;

-- test --
[% FILTER html(entity = 1) -%]
<foo> &lt;bar> <baz&gt; &lt;boz&gt;
[%- END %]
-- expect --
&lt;foo&gt; &lt;bar&gt; &lt;baz&gt; &lt;boz&gt;

"""

main()
