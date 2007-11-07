from template import Template
from template.test import TestCase, main


class HashVmethodsTest(TestCase):
  def testHashVmethods(self):
    params = { "hash": { "a": "b", "c": "d" },
               "uhash": { "tobe": "2b", "nottobe": None } }
    def dump(dict):
      return "{ %s }" % (
        ", ".join(["%s => '%s'" % pair for pair in sorted(dict.items())]))
    Template().context().define_vmethod("hash", "dump", dump)
    self.Expect(DATA, None, params)


DATA = r"""

#------------------------------------------------------------------------
# hash virtual methods
#------------------------------------------------------------------------

-- test --
-- name hash keys --
[% hash.keys.sort.join(', ') %]
-- expect --
a, c

-- test --
-- name hash values --
[% hash.values.sort.join(', ') %]
-- expect --
b, d

-- test --
-- name hash each --
[% hash.each.sort.join(', ') %]
-- expect --
a, b, c, d

-- test --
-- name hash items --
[% hash.items.sort.join(', ') %]
-- expect --
a, b, c, d

-- test --
-- name hash size --
[% hash.size %]
-- expect --
2

-- test --
[% hash.defined('a') ? 'good' : 'bad' %]
[% hash.a.defined ? 'good' : 'bad' %]
[% hash.defined('x') ? 'bad' : 'good' %]
[% hash.x.defined ? 'bad' : 'good' %]
[% hash.defined ? 'good def' : 'bad def' %]
[% no_such_hash.defined ? 'bad no def' : 'good no def' %]
-- expect --
good
good
good
good
good def
good no def

-- test --
[% uhash.defined('tobe') ? 'good' : 'bad' %]
[% uhash.tobe.defined ? 'good' : 'bad' %]
[% uhash.exists('tobe') ? 'good' : 'bad' %]
[% uhash.defined('nottobe') ? 'bad' : 'good' %]
[% hash.nottobe.defined ? 'bad' : 'good' %]
[% uhash.exists('nottobe') ? 'good' : 'bad' %]
-- expect --
good
good
good
good
good
good

-- test --
-- name hash.pairs --
[% FOREACH pair IN hash.pairs -%]
* [% pair.key %] => [% pair.value %]
[% END %]
-- expect --
* a => b
* c => d

-- test --
-- name hash.list (old style) --
[% FOREACH pair IN hash.list -%]
* [% pair.key %] => [% pair.value %]
[% END %]
-- expect --
* a => b
* c => d



#------------------------------------------------------------------------
# user defined hash virtual methods
#------------------------------------------------------------------------

-- test --
-- name dump hash --
[% product = {
     id = 'abc-123',
     name = 'ABC Widget #123'
     price = 7.99
   };
   product.dump
%]
-- expect --
{ id => 'abc-123', name => 'ABC Widget #123', price => '7.99' }

"""

main()

