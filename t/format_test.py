from template.test import TestCase, main


class FormatTest(TestCase):
  def testFormat(self):
    params = { 'a': 'alpha',
               'b': 'bravo',
               'c': 'charlie',
               'd': 'delta' }
    self.Expect(DATA, { 'INTERPOLATE': True, 'POST_CHOMP': 1 }, params)


DATA = r"""[% USE format %]
[% bold = format('<b>%s</b>') %]
[% ital = format('<i>%s</i>') %]
[% bold('heading') +%]
[% ital('author')  +%]
${ ital('affil.') }
[% bold('footing')  +%]
$bold

-- expect --
<b>heading</b>
<i>author</i>
<i>affil.</i>
<b>footing</b>
<b></b>

-- test --
[% USE format('<li> %s') %]
[% FOREACH item = [ a b c d ] %]
[% format(item) +%]
[% END %]
-- expect --
<li> alpha
<li> bravo
<li> charlie
<li> delta

-- test --
[% USE bold = format("<b>%s</b>") %]
[% USE ital = format("<i>%s</i>") %]
[% bold('This is bold')   +%]
[% ital('This is italic') +%]
-- expect --
<b>This is bold</b>
<i>This is italic</i>

-- test --
[% USE padleft  = format('%-*s') %]
[% USE padright = format('%*s')  %]
[% padleft(10, a) %]-[% padright(10, b) %]

-- expect --
alpha     -     bravo

"""

main()
