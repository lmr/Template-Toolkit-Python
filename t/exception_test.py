from template.test import TestCase, main
from template.util import StringBuffer, TemplateException


class ExceptionTest(TestCase):
    def testException(self):
        text = "the current output buffer"
        e1 = TemplateException("e1.type", "e1.info")
        e2 = TemplateException("e2.type", "e2.info", StringBuffer(text))
        self.assertEqual("e1.type", e1.type())
        self.assertEqual("e2.info", e2.info())
        ti = e1.type_info()
        self.assertEqual("e1.type", ti[0])
        self.assertEqual("e1.info", ti[1])
        self.assertEqual("e2.type error - e2.info", str(e2))
        self.assertEqual("the current output buffer", e2.text())
        prepend = "text to prepend "
        e2.text(StringBuffer(prepend))
        self.assertEqual("text to prepend the current output buffer", e2.text())
        handlers = ("something", "e2", "e1.type")
        self.assertEqual("e1.type", e1.select_handler(handlers))
        self.assertEqual("e2", e2.select_handler(handlers))
        e3 = TemplateException("e3.type", "e3.info", None)
        self.assertEqual("", e3.text())
        self.assertEqual("e3.type error - e3.info", str(e3))


if __name__ == '__main__':
    main()
