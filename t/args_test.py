from template import base, test


class MyObj(base.Base):
  def foo(self, *arg):
    return "object:\n" + self.args(*arg)
  def args(self, *arg):
    if arg and isinstance(arg[-1], dict):
      arg = list(arg)
      named = arg.pop()
    else:
      named = { }
    return "  ARGS: [ %s ]\n NAMED: { %s }\n" % (
      ", ".join(str(x) for x in arg),
      ", ".join("%s => %s" % (key, named[key]) for key in sorted(named.keys())))


class ArgsTest(test.TestCase):
  def testArgs(self):
    replace = self._callsign()
    o = MyObj()
    replace['args'] = o.args
    replace['obj'] = MyObj()
    self.Expect(DATA, { 'INTERPOLATE': True }, replace)


DATA = r"""
-- test --
[% args(a b c) %]
-- expect --
  ARGS: [ alpha, bravo, charlie ]
 NAMED: {  }

-- test --
[% args(a b c d=e f=g) %]
-- expect --
  ARGS: [ alpha, bravo, charlie ]
 NAMED: { d => echo, f => golf }

-- test --
[% args(a, b, c, d=e, f=g) %]
-- expect --
  ARGS: [ alpha, bravo, charlie ]
 NAMED: { d => echo, f => golf }

-- test --
[% args(a, b, c, d=e, f=g,) %]
-- expect --
  ARGS: [ alpha, bravo, charlie ]
 NAMED: { d => echo, f => golf }

-- test --
[% args(d=e, a, b, f=g, c) %]
-- expect --
  ARGS: [ alpha, bravo, charlie ]
 NAMED: { d => echo, f => golf }

-- test --
[% obj.foo(d=e, a, b, f=g, c) %]
-- expect --
object:
  ARGS: [ alpha, bravo, charlie ]
 NAMED: { d => echo, f => golf }

-- test --
[% obj.foo(d=e, a, b, f=g, c).split("\n").1 %]
-- expect --
  ARGS: [ alpha, bravo, charlie ]

"""

test.main()
