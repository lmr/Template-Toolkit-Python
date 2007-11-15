from template.test import TestCase, main


class T1:
  def __init__(self, **kwargs):
    for key, value in kwargs.items():
      setattr(self, key, value)
  def die(self):
    raise Exception("barfed up\n")


class TestObject:
  def __init__(self, params=None):
    params = params or {}
    self.PARAMS = params
    self.DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday",
                 "Friday", "Saturday", "Sunday")
    self.DAY = 0
    self.public = 314
    self._hidden = 537
    setattr(self, ".private", 425)

  def yesterday(self):
    return "Love was such an easy game to play..."

  def today(self):
    return "Live for today and die for tomorrow."

  def tomorrow(self, dayno=None):
    if dayno is None:
      dayno = self.DAY
      self.DAY += 1
    dayno %= 7
    return self.DAYS[dayno]

  def belief(self, *args):
    b = " and ".join(args) or "<nothing>"
    return "Oh I believe in %s." % b

  def concat(self, *args):
    self.PARAMS["args"] = "ARGS: %s" % ", ".join(args)

  def _private(self):
    raise Exception("illegal call to private method _private()")

  def __getattr__(self, name):
    if not (name and name[0].islower()):
      raise AttributeError
    value = self.PARAMS.get(name)
    if callable(value):
      def func(*params):
        return value(*params)
    else:
      def func(*params):
        if params:
          param = params[0]
          self.PARAMS[name] = param
          return param
        else:
          return value
    return func


class Stringy:
  def __init__(self, text):
    self.text = text
  def __str__(self):
    return "stringified '%s'" % self.text
  stringify = __str__


class ObjectTest(TestCase):
  def testObject(self):
    objconf = { "a": "alpha",
                "b": "bravo",
                "w": "whisky" }
    replace = { "thing": TestObject(objconf),
                "string": Stringy("Test String"),
                "t1": T1(a=10) }
    replace.update(self._callsign())
    self.Expect(DATA, { "INTERPOLATE": 1 }, replace)


DATA = r"""# test method calling via autoload to get parameters
[% thing.a %] [% thing.a %]
[% thing.b %]
$thing.w
-- expect --
alpha alpha
bravo
whisky

# ditto to set parameters
-- test --
[% thing.c = thing.b -%]
[% thing.c %]
-- expect --
bravo

-- test --
[% thing.concat = thing.b -%]
[% thing.args %]
-- expect --
ARGS: bravo

-- test --
[% thing.concat(d) = thing.b -%]
[% thing.args %]
-- expect --
ARGS: delta, bravo

-- test --
[% thing.yesterday %]
[% thing.today %]
[% thing.belief(thing.a thing.b thing.w) %]
-- expect --
Love was such an easy game to play...
Live for today and die for tomorrow.
Oh I believe in alpha and bravo and whisky.

-- test --
Yesterday, $thing.yesterday
$thing.today
${thing.belief('yesterday')}
-- expect --
Yesterday, Love was such an easy game to play...
Live for today and die for tomorrow.
Oh I believe in yesterday.

-- test --
[% thing.belief('fish' 'chips') %]
[% thing.belief %]
-- expect --
Oh I believe in fish and chips.
Oh I believe in <nothing>.

-- test --
${thing.belief('fish' 'chips')}
$thing.belief
-- expect --
Oh I believe in fish and chips.
Oh I believe in <nothing>.

-- test --
[% thing.tomorrow %]
$thing.tomorrow
-- expect --
Monday
Tuesday

-- test --
[% FOREACH [ 1 2 3 4 5 ] %]$thing.tomorrow [% END %].
-- expect --
Wednesday Thursday Friday Saturday Sunday .


#------------------------------------------------------------------------
# test private methods do not get exposed
#------------------------------------------------------------------------
-- test --
before[% thing._private %] mid [% thing._hidden %]after
-- expect --
before mid after

-- test --
[% key = '_private' -%]
[[% thing.$key %]]
-- expect --
[]

-- test --
[% key = '.private' -%]
[[% thing.$key = 'foo' %]]
[[% thing.$key %]]
-- expect --
[]
[]

#------------------------------------------------------------------------
# test auto-stringification
#------------------------------------------------------------------------

-- test --
[% string.stringify %]
-- expect --
stringified 'Test String'

-- test --
[% string %]
-- expect --
stringified 'Test String'

-- test --
[% "-> $string <-" %]
-- expect --
-> stringified 'Test String' <-

-- test --
[% "$string" %]
-- expect --
stringified 'Test String'

-- test --
foo $string bar
-- expect --
foo stringified 'Test String' bar

-- test --
.[% t1.dead %].
-- expect --
..

-- test --
.[% TRY; t1.die; CATCH; error; END %].
-- expect --
# .undef error - barfed up
.None error - barfed up
.
"""

main()
