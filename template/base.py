import re
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
    
  def select_handler(self, *options):
    type = self.type
    hlut = dict((option, True) for option in options)
    while type:
      if hlut.get(type):
        return type
      type = re.sub(r'\.?[^.]*$', '', type)
    return None

  def __str__(self):
    return "%s error - %s" % (self.type or "", self.info)


class Base:
  def __init__(self):
    self._ERROR = None

  def error(self, *args):
    if args:
      if not isinstance(args[0], (str, int)):
        self._ERROR = args[0]
      else:
        self._ERROR = "".join(args)
    else:
      return self._ERROR

