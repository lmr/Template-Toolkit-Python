import re
import cStringIO
from template import base, constants, iterator, util

ERROR = None

PYEVAL_NAMESPACE = {
  "StringIO":  cStringIO.StringIO,
  "base":      base,  # for Exception
  "constants": constants,
  "Iterator":  iterator.Iterator,
  "Reference": util.Reference,
  "re":        re,
  "util":      util,
  "perlbool":  util.perlbool,
  "Control":   util.Control,
  }

class Document(base.Base):
  def __init__(self, doc):
    base.Base.__init__(self)
    block     = doc.get("BLOCK")
    defblocks = doc.get("DEFBLOCKS") or {}
    metadata  = doc.get("METADATA")  or {}

    #evaluate Python code in block to create sub-routine reference if necessary
    if not callable(block):
      namespace = PYEVAL_NAMESPACE.copy()
      try:
        # print block
        exec block in namespace
      except base.Exception, e:
        return self.error(e)
      block = namespace["_"]

    # same for any additional BLOCK definitions
    for key, block2 in defblocks.items():
      if not callable(block2):
        namespace = PYEVAL_NAMESPACE.copy()
        try:
          exec block2 in namespace
        except base.Exception, e:
          return self.error(e)
        defblocks[key] = namespace["_"]

    for key, value in metadata.items():
      setattr(self, key, value)

    self._BLOCK     = block
    self._DEFBLOCKS = defblocks
    self._HOT       = 0

  def blocks(self):
    return self._DEFBLOCKS

  def process(self, context):
    if self._HOT and not context.RECURSION:
      return context.throw(constants.ERROR_FILE,
                           "recursion into '%s'" % self.name)
    context.visit(self, self._DEFBLOCKS)
    self._HOT = 1
    error = None
    try:
      output = self._BLOCK(context)
    except base.Exception, e:
      error = e
    self._HOT = 0
    context.leave()
    if error:
      raise context.catch(error)

    return output
