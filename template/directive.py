import cStringIO as StringIO
import re

from template.util import *


WHILE_MAX = 1000


class Code:
  class Error(Exception):
    pass

  indent   = Error()  # any class
  unindent = Error()  # will do

  def __init__(self):
    self.buffer = StringIO.StringIO()
    self.depth  = 0

  def write(self, *args):
    for arg in args:
      if arg is self.indent:
        self.depth += 1
      elif arg is self.unindent:
        if self.depth == 0:
          raise self.Error("Too many unindents")
        self.depth -= 1
      elif not arg:
        pass  # skip blank lines
      else:
        for line in arg.split("\n"):
          if line and not line.isspace():
            self.buffer.write(" " * self.depth)
            self.buffer.write(line)
            self.buffer.write("\n")

  def text(self):
    return self.buffer.getvalue()


#  Template::Directive

class Directive:
  def __init__(self, config):
    self.NAMESPACE = config.get("NAMESPACE")


  def template(self, block):
    if not block or block.isspace():
      return "def _(context):\n return ''\n"
    code = Code()
    code.write("def _(context):",
               code.indent,
                 "stash = context.stash()",
                 "output = Buffer()",
                 "try:",
                 code.indent,
                   "# BLOCK: {",
                   block,
                   "# }",
                 code.unindent,
                 "except Error, e:",
                 " error = context.catch(e, output)",
                 " if error.type() != 'return':",
                 "  raise error",
                 "return output.get()")
    return code.text()

  def anon_block(self, block):
    code = Code()
    code.write("def _():",
               code.indent,
                 "output = Buffer()",
                 "try:",
                 code.indent,
                   "# BLOCK: {",
                   block,
                   "# }",
                 code.unindent,
                 "except Error, e:",
                 " error = context.catch(e, output)",
                 " if error.type() != 'return':",
                 "  raise error",
                 "return output.get()",
               code.unindent,
               "_()")
    return code.text()

  def block(self, block=None):
    return "\n".join(block or [])

  def textblock(self, text):
    return "output.write(%s)" % self.text(text)

  def text(self, text):
    return repr(text)

  def quoted(self, items):  # "foo$bar"
    if not items:
      return ""
    else:
      return "Concat(%s)" % ", ".join(items)

  def ident(self, ident):   # foo.bar(baz)
    if not ident:
      return "''"
    # does the first element of the identifier have a NAMESPACE
    # handler defined?
    # WTF?  I'll handle this later.
    if len(ident) <= 2 and (len(ident) <= 1 or not ident[1]):
      ident = ident[0]
    else:
      ident = "[%s]" % ", ".join(str(x) for x in ident)
    return "stash.get(%s)" % ident

  def identref(self, ident):  # \foo.bar(baz)
    if not ident:
      return "''"
    if len(ident) <= 2 and not ident[1]:
      ident = ident[0]
    else:
      ident = "[%s]" % ", ".join(str(x) for x in ident)
    return "stash.getref(%s)" % ident

  def assign(self, var, val, default=False):  # foo = bar
    if not isinstance(var, str):
      if len(var) == 2 and not var[1]:
        var = var[0]
      else:
        var = "[%s]" % ", ".join(str(x) for x in var)
    if default:
      val += ", 1"
    return "stash.set(%s, %s)" % (var, val)

  def args(self, args):  # foo, bar, baz = qux
    args = list(args)
    hash_ = args.pop(0)
    if hash_:
      args.append("Dict(%s)" % ", ".join(hash_))
    if not args:
      return "0"
    return "[" + ", ".join(args) + "]"

  def filenames(self, names):
    if len(names) > 1:
      names = "[%s]" % ", ".join(names)
    else:
      names = names[0]
    return names

  def get(self, expr):  # [% foo %]
    return "output.write(%s)" % (expr,)

  def call(self, expr):  # [% CALL bar %]
    return expr + "\n"

  def set(self, setlist):  # [% foo = bar, baz = qux %]
    # If one uses a generator as the argument to join here, eventually it
    # raises a "TypeError: sequence expected, generator found".  Puzzling.
    return "\n".join([self.assign(var, val) for var, val in chop(setlist, 2)])

  def default(self, setlist):   # [% DEFAULT foo = bar, baz = qux %]
    return "\n".join(self.assign(var, val, 1) for var, val in chop(setlist, 2))

  def insert(self, nameargs):  # [% INSERT file %]
    return "output.write(context.insert(%s))" % self.filenames(nameargs[0])

  def include(self, nameargs):   # [% INCLUDE template foo = bar %]
    file_, args = unpack(nameargs, 2)
    hash_ = args.pop(0)
    file_ = self.filenames(file_)
    if hash_:
      file_ += ", Dict(%s)" % ", ".join(hash_)
    return "output.write(context.include(%s))" % file_

  def process(self, nameargs):  # [% PROCESS template foo = bar %]
    file_, args = unpack(nameargs, 2)
    hash_ = args.pop(0)
    file_ = self.filenames(file_)
    if hash_:
      file_ += ", Dict(%s)" % ", ".join(hash_)
    return "output.write(context.process(%s))" % file_

  def if_(self, expr, block, else_=None):
    # [% IF foo < bar %] [% ELSE %] [% END %]
    if else_:
      elses = else_[:]
    else:
      elses = []
    if elses:
      else_ = elses.pop()  # Ouch.
    else:
      else_ = None
    code = Code()
    code.write("if %s:" % expr, code.indent, block)
    for expr, block in elses:
      code.write(code.unindent, "elif %s:" % expr,
                 code.indent, block)
    if else_ is not None:
      code.write(code.unindent, "else:", code.indent, else_)
    return code.text()

  def foreach(self, target, list, args, block):
    # [% FOREACH x = [ foo bar ] %] ... [% END %]
##     args = args.pop(0)
##     if args:
##       args = ", " + makedict(args)
##     else:
##       args = ""
    if target:
      loop_save = ("try:\n"
                   " oldloop = %s\n"
                   "except StandardError:\n"
                   " pass") % self.ident(["'loop'"])
      loop_set = "stash.contents['%s'] = value" % target
      loop_restore = "stash.set('loop', oldloop)"
    else:
      loop_save = "stash = context.localise()"
      loop_set = ("if isinstance(value, dict):\n"
                  " stash.get(['import', [value]])")
      loop_restore = "stash = context.delocalise()"
    code = Code()
    code.write(
      "def _(stash):",
      code.indent,
        "oldloop = None",
        "loop = Iterator(%s)" % list,
        loop_save,
        "stash.set('loop', loop)",
        "try:",
        code.indent,
          "for value in loop:",
          code.indent,
            "try:",
            code.indent,
              loop_set,
              block,
            code.unindent,
            "except Continue:",
            " continue",
            "except Break:",
            " break",
          code.unindent,
        code.unindent,
        "finally:",
        code.indent,
          loop_restore,
        code.unindent,
      code.unindent,
      "_(stash)")
    return code.text()

  def next(self, *args):
    return "raise Continue"

  def wrapper(self, nameargs, block):  # [% WRAPPER template foo = bar %]
    file, args = unpack(nameargs, 2)
    hash = args.pop(0)
    if len(file) > 1:
      return self.multi_wrapper(file, hash, block)
    file = file[0]
    hash.append("'content': output.get()")
    file += ", { " + ",".join(hash) + " }"
    code = Code()
    code.write("def _():",
               code.indent,
                 "output = Buffer()",
                 block,
                 "return context.include(%s)" % file,
               code.unindent,
               "output.write(_())")
    return code.text()

  def while_(self, expr, block):  # [% WHILE x < 10 %] ... [% END %]
    code = Code()
    code.write("def _():",
               code.indent,
                 "failsafe = %d" % WHILE_MAX,
##                  "while failsafe > 0 and perlbool(%s):" % expr,
                 "while failsafe > 0 and %s:" % expr,
                 code.indent,
                   "try:",
                   code.indent,
                     "failsafe -= 1",
                     block,
                   code.unindent,
                   "except Continue:",
                   " pass",
                   "except Break:",
                   " break",
                 code.unindent,
                 "if not failsafe:",
                 " raise Error('WHILE loop terminated (> %d iterations)')"
                   % WHILE_MAX,
               code.unindent,
               "_()")
    return code.text()

  def switch(self, expr, cases):  # [% SWITCH %] [% CASE foo %] ... [% END %]
    code = Code()
    code.write("def _():",
               code.indent,
                 "result = Regex(str(%s) + '$')" % expr)
    default = cases.pop()
    for match, block in cases:
      code.write("for match in Switch(%s):" % match,
                 code.indent,
                   "if result.match(str(match)):",
                   code.indent,
                     block,
                     "return",
                   code.unindent,
                 code.unindent)
    if default is not None:
      code.write(default)
    code.write(code.unindent, "_()")
    return code.text()

  def try_(self, block, catches):  # [% TRY %] ... [% CATCH %] ... [% END %]
    handlers = []
    final = catches.pop()
    default = None
    n = 0
    catchblock = Code()

    for catch in catches:
      if catch[0]:
        match = catch[0]
      else:
        if default is None:
          default = catch[1]
        continue
      mblock = catch[1]
      handlers.append("'%s'" % match)
      catchblock.write((n == 0 and "if" or "elif")
                       + " handler == '%s':" % match)
      n += 1
      catchblock.write(catchblock.indent, mblock, catchblock.unindent)
    catchblock.write("error = 0")
    if default:
      code = Code()
      code.write("else:", code.indent, "# DEFAULT", default, "error = ''")
      default = code.text()
    else:
      default = "# NO DEFAULT"
    handlers = ", ".join(handlers)

    code = Code()
    code.write(
      "def _():",
      code.indent,
        "output = Buffer()",
        "error = None",
        "try:",
        code.indent,
          block,
        code.unindent,
        "except Exception, e:",
        code.indent,
          "error = context.catch(e, output)",
          "if error.type() in ('return', 'stop'):",
          " raise error",
          "stash.set('error', error)",
          "stash.set('e', error)",
          "handler = error.select_handler(%s)" % handlers,
          "if handler:",
          code.indent,
            catchblock.text(),
          code.unindent,
          default,
        code.unindent,
        "# FINAL",
        final,
        "if error:",
        " raise error",
        "return output.get()",
      code.unindent,
      "output.write(_())")
    return code.text()

  def throw(self, nameargs):  # [% THROW foo "bar error" %]
    type_, args = nameargs
    if args:
      hash_ = args.pop(0)
    else:
      hash_ = None
    if args:
      info = args.pop(0)
    else:
      info = None
    type_ = type_.pop(0)
    if not info:
      info = "None"
    elif hash_ or args:
      info = "Dict(('args', List(%s)), %s)" % (
        ", ".join([info] + args),
        ", ".join(["(%d, %s)" % pair for pair in enumerate([info] + args)]
                  + hash_))
    else:
      pass
    return "context.throw(%s, %s, output)" % (type_, info)


  def clear(self):  # [% CLEAR %]
    return "output.clear()"

  def break_(self):  # [% BREAK %]
    return "raise Break"

  def return_(self):  # [% RETURN %]
    return "context.throw('return', '', output)"

  def stop(self):  # [% STOP %]
    return "context.throw('stop', '', output)"

  def use(self, lnameargs):  # [% USE alias = plugin(args) %]
    file_, args, alias = unpack(lnameargs, 3)
    file_ = file_[0]
    alias = alias or file_
    args = self.args(args)
    if args:
      file_ = "%s, %s" % (file_, args)
    return "# USE\nstash.set(%s, context.plugin(%s))" % (alias, file_)

  def view(self, nameargs, block, defblocks):  # [% VIEW name args %]
    raise NotImplementedError("VIEW")

  def filter_(self, lnameargs, block):
    name, args, alias = unpack(lnameargs, 3)
    name = name[0]
    args = self.args(args)
    if alias:
      if args:
        args = "%s, %s" % (args, alias)
      else:
        args = ", None, %s" % alias
    if args:
      name += ", %s" % args
    code = Code()
    code.write("# FILTER",
               "def _():",
               code.indent,
                 "output = Buffer()",
                 "filter = context.filter(%s) or "
                   "context.throw(context.error())" % name,
                 block,
                 "return filter(output.get())",
               code.unindent,
               "output.write(_())")
    return code.text()

  def capture(self, name, block):
    if isinstance(name, list):
      if len(name) == 2 and not name[1]:
        name = name[0]
      else:
        name = "[" + ", ".join(name) + "]"
    code = Code()
    code.write("def _():",
               code.indent,
                 "output = Buffer()",
                 block,
                 "return output.get()",
               code.unindent,
               "stash.set(%s, _())" % name)
    return code.text()

  def macro(self, ident, block, args=None):
    code = Code()
    code.write("# MACRO")
    if args:
      nargs = len(args)
      proto = ", ".join("arg%d=None" % i for i in range(1, nargs + 1))
      formal = ", ".join("arg%d" % i for i in range(1, nargs + 1))
      argstr = ", ".join("'%s'" % x for x in args)
      code.write(
        "def _(%s, extra=None):" % proto,
        code.indent,
          "params = dict(zip((%s,), (%s,)))" % (argstr, formal),
          "if extra:",
          " params.update(extra)")
    else:
      code.write(
        "def _(params=None):",
        code.indent,
          "if params is None:",
          " params = {}")
    code.write(
      "output = Buffer()",
      "stash = context.localise(params)",
      "try:",
      code.indent,
        block,
      code.unindent,
      "finally:",
      " stash = context.delocalise()",
      "return output.get()")
    code.write(code.unindent, "stash.set('%s', _)" % ident)
    return code.text()
