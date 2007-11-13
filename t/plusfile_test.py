from template.test import TestCase, main


class PlusfileTest(TestCase):
  def testPlusfile(self):
    self.Expect(DATA, { "INCLUDE_PATH": "test/src" })


DATA = r"""
-- test --
[% INCLUDE foo %]
[% BLOCK foo; "This is foo!"; END %]
-- expect --
This is foo!

-- test --
[% INCLUDE foo+bar -%]
[% BLOCK foo; "This is foo!\n"; END %]
[% BLOCK bar; "This is bar!\n"; END %]
-- expect --
This is foo!
This is bar!

-- test --
[% PROCESS foo+bar -%]
[% BLOCK foo; "This is foo!\n"; END %]
[% BLOCK bar; "This is bar!\n"; END %]
-- expect --
This is foo!
This is bar!

-- test --
[% WRAPPER edge + box + indent
     title = "The Title" -%]
My content
[% END -%]
[% BLOCK indent -%]
<indent>
[% content -%]
</indent>
[% END -%]
[% BLOCK box -%]
<box>
[% content -%]
</box>
[% END -%]
[% BLOCK edge -%]
<edge>
[% content -%]
</edge>
[% END -%]
-- expect --
<edge>
<box>
<indent>
My content
</indent>
</box>
</edge>


-- test --
[% INSERT foo+bar/baz %]
-- expect --
This is the foo file, a is [% a -%][% DEFAULT word = 'qux' -%]
This is file baz
The word is '[% word %]'

-- test --
[% file1 = 'foo'
   file2 = 'bar/baz'
-%]
[% INSERT "$file1" + "$file2" %]
-- expect --
This is the foo file, a is [% a -%][% DEFAULT word = 'qux' -%]
This is file baz
The word is '[% word %]'

"""

main()
