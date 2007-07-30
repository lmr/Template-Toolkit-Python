from template import test


class DatafileTest(test.TestCase):
  def testDatafile(self):
    params = { 'datafile': [ 'test/lib/udata1', 'test/lib/udata2' ] }
    self.Expect(DATA, { 'INTERPOLATE': True, 'POST_CHOMP': True }, params)


DATA = r"""[% USE userlist = datafile(datafile.0) %]
Users:
[% FOREACH user = userlist %]
  * $user.id: $user.name
[% END %]

-- expect --
Users:
  * way: Wendy Yardley
  * mop: Marty Proton
  * nellb: Nell Browser

-- test --
[% USE userlist = datafile(datafile.1, delim = '|') %]
Users:
[% FOREACH user = userlist %]
  * $user.id: $user.name <$user.email>
[% END %]

-- expect --
Users:
  * way: Wendy Yardley <way@cre.canon.co.uk>
  * mop: Marty Proton <mop@cre.canon.co.uk>
  * nellb: Nell Browser <nellb@cre.canon.co.uk>

-- test --
[% USE userlist = datafile(datafile.1, delim = '|') -%]
size: [% userlist.size %]
-- expect --
size: 3


"""

test.main()
