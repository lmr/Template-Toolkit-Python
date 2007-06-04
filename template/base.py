from template import util

PyException = Exception

class Exception(PyException):
  def __init__(self, type, info, textref=None):
    PyException.__init__(self)
    self.type    = type
    self.info    = info
    self.textref = textref

  def text(self, newtextref=None):
    if newtextref:
      if self.textref and self.textref is not newtextref:
        newtextref.set(newtextref.get() + self.textref.get())
      self.textref = newtextref
      return ""
    elif self.textref:
      return self.textref.get()
    else:
      return ""

  def __str__(self):
    return "%s error - %s" % (self.type or "", self.info)


class Base:
  def __init__(self):
    self._ERROR = None

  def error(self, *args):
    errvar = util.Reference(self, "_ERROR")
    if args:
      if isinstance(args[0], (int, str)):
        errvar.set("".join(str(x) for x in args))
      else:
        errvar.set(args[0])
      return None
    else:
      return errvar.get()
