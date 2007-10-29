import re

PyException = Exception


class Exception(PyException):
  def __init__(self, type, info, textref=None):
    PyException.__init__(self)
    self.__type    = type
    self.__info    = info
    self.__textref = textref

  def text(self, newtextref=None):
    if newtextref:
      if self.__textref and self.__textref is not newtextref:
        newtextref.set(newtextref.get() + self.__textref.get())
      self.__textref = newtextref
      return ""
    elif self.__textref:
      return self.__textref.get()
    else:
      return ""

  def select_handler(self, *options):
    type = str(self.__type)
    hlut = dict((str(option), True) for option in options)
    while type:
      if hlut.get(type):
        return type
      type = re.sub(r'\.?[^.]*$', '', type)
    return None

  def type(self):
    return self.__type

  def info(self):
    return self.__info

  def type_info(self):
    return self.__type, self.__info

  def __str__(self):
    return "%s error - %s" % (self.__type or "", self.__info)


class Base:
  def __init__(self):
    self._ERROR = None

  def error(self, *args):
    if args:
      self._ERROR = self.__ErrorMessage(args)
    else:
      return self._ERROR

  @classmethod
  def Error(cls, *args):
    if args:
      cls.ERROR = self.__ErrorMessage(args)
    else:
      return getattr(cls, "ERROR", None)

  @staticmethod
  def __ErrorMessage(args):
    if len(args) == 1:
      return args[0]
    else:
      return "".join(args)
