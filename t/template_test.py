from template import Template, TemplateException
from template.util import StringBuffer
from template.test import TestCase, main


class TemplateTest(TestCase):
    def testTemplate(self):
        out = StringBuffer()
        tt = Template({"INCLUDE_PATH": "test/src:test/lib",
                       "OUTPUT": out})
        tt.process("header")
        self.assertTrue(out.get())
        out.clear()
        try:
            tt.process("this_file_does_not_exist")
            self.fail("exception not raised")
        except TemplateException as e:
            self.assertEqual("file", e.type())
            self.assertEqual("this_file_does_not_exist: not found", e.info())


if __name__ == '__main__':
    main()
