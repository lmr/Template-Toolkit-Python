from template.config import Config
from template.test import TestCase, main


class PrefixTest(TestCase):
  def testPrefix(self):
    src_prov = Config.provider({ "INCLUDE_PATH": "test/src" })
    lib_prov = Config.provider({ "INCLUDE_PATH": "test/lib" })
    config = { "LOAD_TEMPLATES": [ src_prov, lib_prov ],
               "PREFIX_MAP": { "src": "0", "lib": "1", "all": "0, 1" } }
    self.Expect(DATA, config)


DATA = r"""
-- test --
[% INCLUDE foo a=10 %]
-- expect --
This is the foo file, a is 10

-- test --
[% INCLUDE src:foo a=20 %]
-- expect --
This is the foo file, a is 20

-- test --
[% INCLUDE all:foo a=30 %]
-- expect --
This is the foo file, a is 30

-- test --
[% TRY;
    INCLUDE lib:foo a=30 ;
   CATCH;
    error;
   END
%]
-- expect --
file error - lib:foo: not found

-- test --
[% INSERT src:foo %]
-- expect --
This is the foo file, a is [% a -%]

"""

main()
