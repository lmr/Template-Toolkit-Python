import re
import cStringIO as StringIO

from template.util import *


WHILE_MAX = 1000


class Error(Exception):
  pass


def makedict(elts):
  buf = "{"
  for key, value in chop(elts, 2):
    buf += key + ": " + value + ","
  buf += "}"
  return buf


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
  def __init__(self):
    pass

  def template(self, block):
    if not block or block.isspace():
      return "def _(context):\n return ''\n"
    code = Code()
    code.write("def _(context):",
               code.indent,
                 "stash = context.stash()",
                 "output = StringIO()",
                 "try:",
                 code.indent,
                   "# BLOCK: {",
                   block,
                   "# }",
                 code.unindent,
                 "except base.Exception, e:",
                 " error = context.catch(e, Reference(output))",
                 " if error.type != 'return':",
                 "  raise error",
                 "return output.getvalue()")
    return code.text()

  def anon_block(self, block):
    code = Code()
    code.write("def _():",
               code.indent,
                 "output = StringIO",
                 "try:",
                 code.indent,
                   "# BLOCK: {",
                   block,
                   "# }",
                 code.unindent,
                 "except base.Exception, e:",
                 " error = context.catch(e, Reference(output))",
                 " if error.type != 'return':",
                 "  raise error",
                 "return output.getvalue()",
               code.unindent,
               "_()")
    return code.text()

  def block(self, block=None):
    return "\n".join(block or [])

  def textblock(self, text):
    return "output.write(str(%s))" % self.text(text)

  def text(self, text):
    return repr(text)

  def quoted(self, items):  # "foo$bar"
    if not items:
      return ""
    elif len(items) == 1:
      return items[0]
    else:
      return "''.join(str(x) for x in (" + ", ".join(items) + ",))"

  def ident(self, ident):   # foo.bar(baz)
    if not ident:
      return "''"
    # does the first element of the identifier have a NAMESPACE
    # handler defined?
    # WTF?  I'll handle this later.
    if len(ident) <= 2 and (len(ident) <= 1 or not ident[1]):
      ident = ident[0]
    else:
      ident = "[ " + ", ".join(str(x) for x in ident) + " ]"
    return "stash.get(%s)" % ident

  def identref(self, ident):  # \foo.bar(baz)
    if not ident:
      return "''"
    if len(ident) <= 2 and not ident[1]:
      ident = ident[0]
    else:
      ident = "[ " + ", ".join(ident) + " ]"
    return "stash.getref(%s)" % ident

  def assign(self, var, val, default=False):  # foo = bar
    if type(var) != str:
      if len(var) == 2 and not var[1]:
        var = var[0]
      else:
        var = "[ " + ", ".join(str(x) for x in var) + " ]"
    if default:
      val += ", 1"
    return "stash.set(%s, %s)" % (var, val)

  def args(self, args):  # foo, bar, baz = qux
    args = list(args)
    hash_ = args.pop(0)
    if hash_:
      # args.append(makedict(hash_))
      args.append("{ %s }" % ", ".join(hash_))
    if not args:
      return "0"
    return "[" + ", ".join(args) + "]"

  def filenames(self, names):
    if len(names) > 1:
      names = "[ " + ", ".join(names) + " ]"
    else:
      names = names[0]
    return names

  def get(self, expr):  # [% foo %]
    return "output.write(str(%s))" % (expr,)

  def call(self, expr):  # [% CALL bar %]
    return expr + "\n"

  def set(self, setlist):  # [% foo = bar, baz = qux %]
    # If one uses a generator as the argument to join here, eventually it
    # raises a "TypeError: sequence expected, generator found".  Puzzling.
    return "\n".join([self.assign(var, val) for var, val in chop(setlist, 2)])

  def default(self, setlist):   # [% DEFAULT foo = bar, baz = qux %]
    return "\n".join(self.assign(var, val, 1) for var, val in chop(setlist, 2))

  def insert(self, nameargs):  # [% INSERT file %]
    return "output.write(str(context.insert(%s)))" % self.filenames(nameargs[0])

  def include(self, nameargs):   # [% INCLUDE template foo = bar %]
    file_, args = unpack(nameargs, 2)
    hash_ = args.pop(0)
    file_ = self.filenames(file_)
    if hash_:
      file_ += ", { %s }" % ", ".join(hash_)
    return "output.write(str(context.include(%s)))" % file_

  def process(self, nameargs):  # [% PROCESS template foo = bar %]
    file_, args = unpack(nameargs, 2)
    hash_ = args.pop(0)
    file_ = self.filenames(file_)
    if hash_:
      file_ += ", " + makedict(hash_)
    return "output.write(str(context.process(%s)))" % file_

  def if_(self, expr, block, else_=None):  # [% IF foo < bar %] [% ELSE %] [% END %]
    if else_:
      elses = else_[:]
    else:
      elses = []
    if elses:
      else_ = elses.pop()  # Ouch.
    else:
      else_ = None
    code = Code()
    code.write("if perlbool(%s):" % expr, code.indent, block)
    for expr, block in elses:
      code.write(code.unindent, "elif perlbool(%s):" % expr, code.indent, block)
    if else_ is not None:
      code.write(code.unindent, "else:", code.indent, else_)
    return code.text()

  def foreach(self, target, list_, args, block):
    # [% FOREACH x = [ foo bar ] %] ... [% END %]
    args = args.pop(0)
    if args:
      args = ", " + makedict(args)
    else:
      args = ""
    if target:
      loop_save = "try:\n oldloop = %s\nexcept:\n pass" % self.ident(["'loop'"])
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
        "list_ = %s" % list_,
        "if not isinstance(list_, Iterator):",
        " list_ = Iterator(list_)",
        "value, error = list_.get_first()",
        loop_save,
        "stash.set('loop', list_)",
        "try:",
        code.indent,
          "while not error:",
          code.indent,
            "try:",
            code.indent,
              loop_set,
              block,
              "value, error = list_.get_next()",
            code.unindent,
            "except Continue:\n value, error = list_.get_next()",
            "except Break:\n break",
          code.unindent,
        code.unindent,
        "finally:",
        code.indent,
          loop_restore,
        code.unindent,
        "if error and error != constants.STATUS_DONE:",
        " raise Exception(error)",
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
    hash.append("'content': output.getvalue()")
    file += ", { " + ",".join(hash) + " }"
    code = Code()
    code.write("def _():",
               code.indent,
                 "output = StringIO()",
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
                 "while failsafe > 0 and perlbool(%s):" % expr,
                 code.indent,
                   "try:",
                   code.indent,
                     "failsafe -= 1",
                     block,
                   code.unindent,
                   "except Continue:\n pass",
                   "except Break:\n break",
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
                 "result = re.compile(str(%s) + '$')" % expr)
    default = cases.pop()
    for match, block in cases:
      code.write("match = %s" % match,
                 "if not isinstance(match, list):",
                 " match = [match]",
                 "for m in match:",
                 code.indent,
                   "if result.match(str(m)):",
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
    final    = catches.pop()
    default  = None
    n        = 0
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
    code.write("def _():",
               code.indent,
                 "output = StringIO()",
                 "try:",
                 code.indent,
                   block,
                 code.unindent,
                 "except base.Exception, e:",
                 code.indent,
                   "error = context.catch(e, Reference(output))",
                   "if error.type in ('return', 'stop'):",
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
                 final,
                 "return output.getvalue()",
               code.unindent,
               "output.write(_())")
    return code.text()

  def throw(self, nameargs):  # [% THROW foo "bar error" %]
    type_, args = nameargs
    hash_ = args.pop(0)
    info  = args.pop(0)
    type_ = type_.pop(0)
    if not info:
      args = "%s, None" % type_
    elif hash_ or args:
      args = "%s, {'args': [ %s ], %s }" % (
        type_, ", ".join([info] + args),
        ", ".join(tuple("'%d': %s" % x for x in enumerate([info] + args)) +
                  tuple(hash_)))
    else:
      args = "%s, %s" % (type_, info)
    return "context.throw(%s, output)" % args # FIXME: \$output in original Perl



  def clear(self):  # [% CLEAR %]
    return "output.seek(0)\noutput.truncate()"

  def break_(self):  # [% BREAK %]
    return "raise Break"

  def return_(self):  # [% RETURN %]
    return "context.throw('return', '', output)"  # \$output in Perl

  def stop(self):  # [% STOP %]
    return "context.throw('stop', '', output)"  # \$output in Perl

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
                 "output = StringIO()",
                 "filter = context.filter(%s) or "
                   "context.throw(context.error())" % name,
                 block,
                 "return filter(output.getvalue())",
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
                 "output = StringIO()",
                 block,
                 "return output.getvalue()",
               code.unindent,
               "stash.set(%s, _())" % name)
    return code.text()

  def macro(self, ident, block, args=None):
    code = Code()
    code.write("# MACRO")
    if args:
      nargs = len(args)
      proto = ", ".join("arg%d" % i for i in range(1, nargs + 1))
      argstr = ", ".join("'%s'" % x for x in args)
      code.write("def _(%s, extra=None):" % proto,
                 code.indent,
                   "params = dict(zip((%s,), (%s,)))" % (argstr, proto),
                   "if extra:",
                   " params.update(extra)")
    else:
      code.write("def _(params=None):",
                 code.indent,
                   "if params is None:",
                   " params = {}")
    code.write("output = StringIO()",
               "stash = context.localise(params)",
               "try:",
               code.indent,
                 block,
               code.unindent,
               "finally:",
               " stash = context.delocalise()",
               "return output.getvalue()")
    code.write(code.unindent, "stash.set('%s', _)" % ident)
    return code.text()
