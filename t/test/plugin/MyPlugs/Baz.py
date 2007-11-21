class Baz:
  def __init__(self, value):
    self.__value = value

  def output(self):
    return "This is the Baz module, value is %s" % (self.__value,)
