import cStringIO as StringIO
import re

from template.util import *


WHILE_MAX = 1000


class Code:
  class Error(Exception):
    pass

  indent   = Error()  # any distinct objects
  unindent = Error()  # will do

  @classmethod
  def format(cls, *args):
    code = cls()
    code.write(*args)
    return code.text()

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
      return "def block(context):\n return ''\n"
    return Code.format(
      "def block(context):",
      Code.indent,
        "stash = context.stash()",
        "output = Buffer()",
        "try:",
        Code.indent,
          block,
        Code.unindent,
        "except Error, e:",
        " error = context.catch(e, output)",
        " if error.type() != 'return':",
        "  raise error",
        "return output.get()")

  def anon_block(self, block):
    return Code.format(
      "def _():",
      Code.indent,
        "output = Buffer()",
        "try:",
        Code.indent,
          block,
        Code.unindent,
        "except Error, e:",
        " error = context.catch(e, output)",
        " if error.type() != 'return':",
        "  raise error",
        "return output.get()",
      Code.unindent,
      "_()")

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
    # Does the first element of the identifier have a NAMESPACE
    # handler defined?
    if ident and len(ident) > 2 and self.NAMESPACE:
      key = ident[0]
      if key.startswith("'") and key.endswith("'"):
        key = key[1:-1]
      ns = self.NAMESPACE.get(key)
      if ns:
        return ns.ident(ident)
    return self.Ident(ident)

  @classmethod
  def Ident(cls, ident):
    if not ident:
      return "''"
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
    return Code.format(
      "def _(stash):",
      Code.indent,
        "oldloop = None",
        "loop = Iterator(%s)" % list,
        loop_save,
        "stash.set('loop', loop)",
        "try:",
        Code.indent,
          "for value in loop:",
          Code.indent,
            "try:",
            Code.indent,
              loop_set,
              block,
            Code.unindent,
            "except Continue:",
            " continue",
            "except Break:",
            " break",
          Code.unindent,
        Code.unindent,
        "finally:",
        Code.indent,
          loop_restore,
        Code.unindent,
      Code.unindent,
      "_(stash)")

  def next(self, *args):
    return "raise Continue"

  def wrapper(self, nameargs, block):  # [% WRAPPER template foo = bar %]
    file, args = unpack(nameargs, 2)
    hash = args.pop(0)
    if len(file) > 1:
      return self.multi_wrapper(file, hash, block)
    file = file[0]
    hash.append("('content', output.get())")
    file += ", Dict(%s)" % ", ".join(hash)
    return Code.format(
      "def _():",
      Code.indent,
        "output = Buffer()",
        block,
        "return context.include(%s)" % file,
      Code.unindent,
      "output.write(_())")

  def multi_wrapper(self, file, hash, block):
    hash.append("('content', output.get())")
    return Code.format(
      "def _():",
      Code.indent,
        "output = Buffer()",
        block,
        "for file in %s:" % ", ".join(reversed(file)),
        " output.reset(context.include(file, Dict(%s)))" % ", ".join(hash),
        "return output.get()",
      Code.unindent,
      "output.write(_())")

  def while_(self, expr, block):  # [% WHILE x < 10 %] ... [% END %]
    return Code.format(
      "def _():",
      Code.indent,
        "failsafe = %d" % (WHILE_MAX - 1),
        "while failsafe and (%s):" % expr,
        Code.indent,
          "try:",
          Code.indent,
            "failsafe -= 1",
            block,
          Code.unindent,
          "except Continue:",
          " continue",
          "except Break:",
          " break",
        Code.unindent,
        "if not failsafe:",
        " raise Error(None, 'WHILE loop terminated (> %d iterations)')"
          % WHILE_MAX,
      Code.unindent,
      "_()")

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
      default = Code.format("else:", Code.indent, default, "error = ''")
    else:
      default = "# NO DEFAULT"
    handlers = ", ".join(handlers)

    return Code.format(
      "def _():",
      Code.indent,
        "output = Buffer()",
        "error = None",
        "try:",
        Code.indent,
          block,
        Code.unindent,
        "except Exception, e:",
        Code.indent,
          "error = context.catch(e, output)",
          "if error.type() in ('return', 'stop'):",
          " raise error",
          "stash.set('error', error)",
          "stash.set('e', error)",
          "handler = error.select_handler(%s)" % handlers,
          "if handler:",
          Code.indent,
            catchblock.text(),
          Code.unindent,
          default,
        Code.unindent,
        final,
        "if error:",
        " raise error",
        "return output.get()",
      Code.unindent,
      "output.write(_())")

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
    return "stash.set(%s, context.plugin(%s))" % (alias, file_)

  def view(self, nameargs, block, defblocks):  # [% VIEW name args %]
    raise NotImplementedError("VIEW")

  def python(self, block):
    return Code.format(
      "if not context.eval_python():",
      " context.throw('python', 'EVAL_PYTHON not set')",
      "def _():",
      Code.indent,
        "output = Buffer()",
        block,
        "return Evaluate(output.get(), context, stash)",
      Code.unindent,
      "output.write(_())")

  def no_python(self):
    return "context.throw('python', 'EVAL_PYTHON not set')"

  def rawpython(self, block, line):
    block = unindent(block)
    line = line and " (starting line %s)" % line or ""
    return "#line 1 'RAWPYTHON block%s'\n%s" % (line, block)

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
    return Code.format(
      "def _():",
      Code.indent,
        "output = Buffer()",
        "filter = context.filter(%s) or "
          "context.throw(context.error())" % name,
        block,
        "return filter(output.get())",
      Code.unindent,
      "output.write(_())")

  def capture(self, name, block):
    if isinstance(name, list):
      if len(name) == 2 and not name[1]:
        name = name[0]
      else:
        name = "[" + ", ".join(name) + "]"
    return Code.format(
      "def _():",
      Code.indent,
        "output = Buffer()",
        block,
        "return output.get()",
      Code.unindent,
      "stash.set(%s, _())" % name)

  def macro(self, ident, block, args=None):
    code = Code()
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
