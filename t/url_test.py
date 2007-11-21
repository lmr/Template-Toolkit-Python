from template.plugin import url
from template.test import TestCase, main


def no_escape():
  url.JOINT = "&"


def sort_params(query):
  base, args = (query.split("?", 2) + [""])[:2]
  args = args.split("&amp;")
  keys = [x.split("=")[0] for x in args]
  argtab = dict(zip(keys, args))
  keys = sorted(argtab.keys())
  args = [argtab[x] for x in keys]
  args = "&amp;".join(args)
  query = "?".join(base and [base, args] or [args])
  return query


class UrlTest(TestCase):
  def testUrl(self):
    urls = [{ "name": "view",
              "url": "/product" },
            { "name": "add",
              "url": "/product",
              "args": { "action": "add" } },
            { "name": "edit",
              "url": "/product",
              "args": { "action": "edit", "style": "editor" } } ]
    urls = dict((x["name"], url.Url.factory(None, x["url"], x.get("args")))
                for x in urls)
    urls = { "product": urls }
    vars = { "url": urls,
             "sorted": sort_params,
             "no_escape": no_escape }
    self.Expect(DATA, { "INTERPOLATE": 1 }, vars)



DATA = r"""
-- test --
[% USE url -%]
loaded
[% url %]
[% url('foo') %]
[% url(foo='bar') %]
[% url('bar', wiz='woz') %]

-- expect --
loaded

foo
foo=bar
bar?wiz=woz

-- test --
[% USE url('here') -%]
[% url %]
[% url('there') %]
[% url(any='where') %]
[% url('every', which='way') %]
[% sorted( url('every', which='way', you='can') ) %]

-- expect --
here
there
here?any=where
every?which=way
every?which=way&amp;you=can

-- test --
[% USE url('there', name='fred') -%]
[% url %]
[% url(name='tom') %]
[% sorted( url(age=24) ) %]
[% sorted( url(age=42, name='frank') ) %]

-- expect --
there?name=fred
there?name=tom
there?age=24&amp;name=fred
there?age=42&amp;name=frank

-- test --
[% USE url('/cgi-bin/woz.pl') -%]
[% url(name="Elrich von Benjy d'Weiro") %]

-- expect --
/cgi-bin/woz.pl?name=Elrich%20von%20Benjy%20d%27Weiro

-- test --
[% USE url '/script' { one => 1, two => [ 2, 4 ], three => [ 3, 6, 9] } -%]
[% url  %]

-- expect --
/script?one=1&amp;three=3&amp;three=6&amp;three=9&amp;two=2&amp;two=4

-- test --
[% url.product.view %]
[% url.product.view(style='compact') %]
-- expect --
/product
/product?style=compact

-- test --
[% url.product.add %]
[% url.product.add(style='compact') %]
-- expect --
/product?action=add
/product?action=add&amp;style=compact

-- test --
[% url.product.edit %]
[% url.product.edit(style='compact') %]
-- expect --
/product?action=edit&amp;style=editor
/product?action=edit&amp;style=compact

-- test --
[% CALL no_escape -%]
[% url.product.edit %]
[% url.product.edit(style='compact') %]
-- expect --
/product?action=edit&style=editor
/product?action=edit&style=compact
"""

main()

